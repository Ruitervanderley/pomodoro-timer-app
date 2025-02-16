import flet as ft
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
import base64
import sqlite3
from config import DATABASE_PATH

def carregar_chave_publica():
    """Carrega a chave pública para verificação da assinatura."""
    with open("public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())
    return public_key

def ajustar_padding_base64(data):
    """Ajusta o padding para uma string codificada em Base64."""
    return data + "=" * ((4 - len(data) % 4) % 4)

def validar_serial(serial, usuario_id):
    """Valida o serial com a chave pública."""
    try:
        public_key = carregar_chave_publica()

        # Ajusta o padding do serial e o decodifica
        serial = ajustar_padding_base64(serial)
        serial_decodificado = base64.urlsafe_b64decode(serial.encode())

        # Dados a serem verificados, exemplo: "{usuario_id}:validade"
        dados_original = f"{usuario_id}:validade".encode()

        # Verifica a assinatura da licença com a chave pública
        public_key.verify(
            serial_decodificado,
            dados_original,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Serial válido.")
        return True
    except Exception as e:
        print(f"Erro ao validar serial: {e}")
        return False

def obter_validade_serial(usuario):
    """Obtém a validade do serial do usuário a partir do banco de dados."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT data_expiracao FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            data_expiracao = resultado[0]
            return data_expiracao
        return "Nenhum serial encontrado"
    except Exception as e:
        return f"Erro ao obter validade: {e}"

def verificar_expiracao_proxima(usuario):
    """Verifica se a licença do usuário está prestes a expirar (dentro de 30 dias)."""
    validade_str = obter_validade_serial(usuario)
    if validade_str and validade_str != "Nenhum serial encontrado":
        try:
            validade = datetime.strptime(validade_str, "%Y-%m-%d")
            dias_para_expirar = (validade - datetime.now()).days
            return dias_para_expirar <= 30  # Expira se restarem 30 dias ou menos
        except ValueError:
            return False
    return False

def ativar_licenca(page: ft.Page, usuario):
    """Abre um diálogo para inserir e validar o serial de licença."""
    def salvar_licenca(e):
        serial = serial_input.value
        if validar_serial(serial, usuario):
            salvar_serial_bd(usuario, serial)
            page.snack_bar = ft.SnackBar(content=ft.Text("Licença ativada com sucesso!"), open=True)
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text("Serial inválido!"), open=True)
        page.update()

    serial_input = ft.TextField(label="Insira o serial")
    ativar_button = ft.ElevatedButton(text="Ativar", on_click=salvar_licenca)

    # Exibe o diálogo de ativação
    page.dialog = ft.AlertDialog(
        title=ft.Text("Ativação de Licença"),
        content=serial_input,
        actions=[ativar_button],
    )
    page.dialog.open = True
    page.update()

def salvar_serial_bd(usuario, serial):
    """Salva o serial do usuário no banco de dados."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET serial = ?, data_expiracao = ? WHERE usuario = ?",
                   (serial, (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'), usuario))
    conn.commit()
    conn.close()
