import flet as ft
from login import login_page
from atualizador import Atualizador
import threading
import time
from config import VERSAO_ATUAL

def iniciar_verificador_atualizacoes(page):
    def verificar():
        atualizador = Atualizador(page)
        while True:
            try:
                # Verificação imediata
                page.run_task(atualizador.verificar_atualizacoes)
                
                # Espera 24 horas
                time.sleep(86400)
                
            except Exception as e:
                print(f"Erro no verificador: {str(e)}")

    thread = threading.Thread(target=verificar, daemon=True)
    thread.start()

def main(page: ft.Page):
    # Configurações básicas
    page.title = f"Pomodoro Timer v{VERSAO_ATUAL}"
    page.window_full_screen = True
    page.theme_mode = ft.ThemeMode.DARK
    
    # Inicia verificador de atualizações
    iniciar_verificador_atualizacoes(page)
    
    # Carrega a tela de login
    login_page(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")