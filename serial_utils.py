from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from datetime import datetime, timedelta
import base64
import os

# Caminhos dos arquivos de chave
PRIVATE_KEY_PATH = "private_key.pem"
PUBLIC_KEY_PATH = "public_key.pem"
SERIAL_FILE_PATH = "serial.txt"

def gerar_serial(usuario_id, validade_dias):
    """Gera um novo serial assinado com a chave privada."""
    validade = (datetime.now() + timedelta(days=validade_dias)).strftime("%Y-%m-%d")
    dados = f"{usuario_id}:{validade}".encode()

    # Carregar a chave privada
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    # Assina os dados com a chave privada
    assinatura = private_key.sign(
        dados,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Codificar a assinatura em base64 para facilitar o envio
    serial_codificado = base64.urlsafe_b64encode(assinatura).decode()

    # Combine os dados originais com a assinatura em base64
    serial_final = base64.urlsafe_b64encode(dados + b"." + assinatura).decode()

    return serial_final

def validar_serial(serial, usuario_id):
    """Valida o serial com a chave pública."""
    try:
        # Carregar a chave pública
        with open(PUBLIC_KEY_PATH, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        # Decodificar o serial e separar os dados da assinatura
        serial_decodificado = base64.urlsafe_b64decode(serial.encode())
        dados, assinatura = serial_decodificado.split(b".", 1)

        # Verificar a assinatura com a chave pública
        public_key.verify(
            assinatura,
            dados,
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

def salvar_serial(serial):
    """Salva o serial em um arquivo local."""
    with open(SERIAL_FILE_PATH, "w") as f:
        f.write(serial)

def carregar_serial():
    """Carrega o serial salvo localmente."""
    if os.path.exists(SERIAL_FILE_PATH):
        with open(SERIAL_FILE_PATH, "r") as f:
            return f.read().strip()
    return ""

def obter_validade_serial():
    """Obtém a validade do serial salvo."""
    serial = carregar_serial()
    if serial:
        try:
            dados_decodificados = base64.urlsafe_b64decode(serial.encode()).decode()
            # Supondo que a validade esteja codificada no serial
            usuario_id, validade = dados_decodificados.split(":")
            return validade
        except Exception as e:
            return f"Erro ao obter validade: {e}"
    return "Nenhum serial encontrado"
