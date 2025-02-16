import flet as ft
import requests
import hashlib
import os
import sys
import zipfile
import shutil
import logging
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature  # ✅ Mantenha apenas esta
from config import VERSAO_ATUAL, REPO_URL, CHAVE_PUBLICA_PATH

class Atualizador:
    def __init__(self, page: ft.Page):
        self.page = page
        self.versao_atual = VERSAO_ATUAL
        self.dialogo_ativo = False
        self._carregar_chave_publica()

    def _carregar_chave_publica(self):
        try:
            with open(CHAVE_PUBLICA_PATH, "rb") as f:
                self.chave_publica = load_pem_public_key(f.read())
        except Exception as e:
            logging.error(f"Erro ao carregar chave pública: {str(e)}")
            raise

    async def verificar_atualizacoes(self, e=None):
        try:
            ultima_versao = await self._obter_ultima_versao()
            
            if self._comparar_versoes(ultima_versao):
                await self._mostrar_dialogo_atualizacao(ultima_versao)
        except Exception as e:
            await self._mostrar_erro(f"Falha na verificação: {str(e)}")

    async def _obter_ultima_versao(self):
        try:
            response = requests.get(
                f"{REPO_URL}/releases/latest",  # ← URL corrigida
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()["tag_name"].lstrip('v')
        except Exception as e:
            logging.error(f"Erro na API: {str(e)}")
            raise

    def _comparar_versoes(self, nova_versao):
        # Nova versão corrigida
        versao_atual = tuple(map(int, self.versao_atual.lstrip('v').split('.')))
        versao_nova = tuple(map(int, nova_versao.lstrip('v').split('.')))
        return versao_nova > versao_atual

    async def _mostrar_dialogo_atualizacao(self, nova_versao):
        if not self.dialogo_ativo:
            self.dialogo = ft.AlertDialog(
                modal=True,
                title=ft.Text("Atualização Disponível"),
                content=ft.Column([
                    ft.Text(f"Versão Atual: v{self.versao_atual}"),
                    ft.Text(f"Nova Versão: v{nova_versao}"),
                    ft.ProgressRing(width=50, height=50, visible=False)
                ], tight=True),
                actions=[
                    ft.TextButton("Instalar Agora", on_click=lambda e: self._iniciar_atualizacao(nova_versao)),
                    ft.TextButton("Lembrar Depois", on_click=self._fechar_dialogo)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            
            self.page.dialog = self.dialogo
            self.dialogo.open = True
            self.dialogo_ativo = True
            await self.page.update_async()

    async def _iniciar_atualizacao(self, nova_versao):
        try:
            self._toggle_loading(True)
            caminho_zip = await self._baixar_atualizacao(nova_versao)
            await self._verificar_assinatura(caminho_zip)
            await self._aplicar_atualizacao(caminho_zip)
            await self._reiniciar_aplicativo()
        except Exception as e:
            await self._mostrar_erro(f"Falha na atualização: {str(e)}")
            self._toggle_loading(False)

    async def _baixar_atualizacao(self, versao):
        try:
            Path("temp").mkdir(exist_ok=True)
            download_url = f"{REPO_URL}/archive/refs/tags/v{versao}.zip"
            response = requests.get(download_url, stream=True, timeout=15)
            
            caminho_zip = Path("temp") / f"update_v{versao}.zip"
            with open(caminho_zip, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return caminho_zip
        except Exception as e:
            logging.error(f"Erro no download: {str(e)}")
            raise

    async def _verificar_assinatura(self, caminho_zip):
        try:
            # Baixar assinatura
            assinatura_url = f"{REPO_URL}/releases/download/v{self.versao_atual}/update.sig"
            response = requests.get(assinatura_url, timeout=10)
            assinatura = response.content
            
            # Verificar assinatura
            with open(caminho_zip, "rb") as f:
                dados = f.read()
                self.chave_publica.verify(
                    assinatura,
                    dados,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
        except InvalidSignature as e:
            logging.error("Assinatura inválida!")
            raise ValueError("Falha na verificação de segurança: Assinatura digital inválida") from e  # ✅ Use ValueError
        except Exception as e:
            logging.error(f"Erro na verificação: {str(e)}")
            raise

    async def _aplicar_atualizacao(self, caminho_zip):
        try:
            with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                zip_ref.extractall("temp")
            
            source_dir = next(Path("temp").iterdir())
            for item in source_dir.glob("*"):
                if item.is_dir():
                    shutil.copytree(item, item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, item.name)
        except Exception as e:
            logging.error(f"Erro ao aplicar atualização: {str(e)}")
            raise

    async def _reiniciar_aplicativo(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    async def _mostrar_erro(self, mensagem):
        try:
            if self.page and not self.page._closed:  # ← Verificação crítica
                await self.page.show_snack_bar(
                    ft.SnackBar(
                        ft.Text(mensagem),
                        bgcolor=ft.colors.RED
                    )
                )
            logging.error(mensagem)
        except Exception as e:
            logging.error(f"Erro ao exibir mensagem: {str(e)}")

    def _toggle_loading(self, loading):
        if self.dialogo:
            self.dialogo.content.controls[2].visible = loading
            self.page.update()

    def _fechar_dialogo(self, e=None):
        if self.dialogo:
            self.dialogo.open = False
            self.dialogo_ativo = False
            self.page.update()

def main(page: ft.Page):
    atualizador = Atualizador(page)
    page.add(ft.Text("Verificando atualizações..."))
    page.update()
    page.on_load = atualizador.verificar_atualizacoes

if __name__ == "__main__":
    # Para testes locais
    ft.app(target=main)