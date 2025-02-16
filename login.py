import flet as ft
import sqlite3
import os
import json
from datetime import datetime
from config import RUTA_LOGO, DATABASE_PATH

# Caminho para o arquivo de configurações locais
USER_PREFS_PATH = os.path.join(os.getcwd(), "user_prefs.json")


def carregar_usuario_lembrado():
    """Carrega o usuário e senha lembrados do arquivo JSON."""
    if os.path.exists(USER_PREFS_PATH):
        with open(USER_PREFS_PATH, "r") as f:
            prefs = json.load(f)
            return prefs.get("usuario"), prefs.get("senha")
    return None, None


def salvar_usuario_lembrado(usuario, senha):
    """Salva o usuário e a senha lembrados no arquivo JSON."""
    with open(USER_PREFS_PATH, "w") as f:
        json.dump({"usuario": usuario, "senha": senha}, f)


def limpar_usuario_lembrado():
    """Remove as credenciais salvas."""
    if os.path.exists(USER_PREFS_PATH):
        os.remove(USER_PREFS_PATH)


def login_page(page: ft.Page):
    from menu_principal import mostrar_menu

    page.theme_mode = "light"

    def aplicar_tema():
        page.bgcolor = ft.colors.WHITE
        for control in [usuario, senha]:
            control.border_color = ft.colors.BLUE_GREY_300
            control.color = ft.colors.BLACK
            control.bgcolor = ft.colors.BLUE_GREY_50
        page.update()

    def exibir_mensagem(texto, sucesso=True):
        cor = ft.colors.GREEN if sucesso else ft.colors.RED
        icon = ft.icons.CHECK_CIRCLE if sucesso else ft.icons.ERROR

        page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(icon, color=cor),
                ft.Text(texto, color=cor, weight="bold", size=16),
            ], spacing=10),
            open=True,
            duration=3000,
            bgcolor=ft.colors.BLACK38,
        )
        page.update()

    def verificar_usuario(usuario_input, senha_input):
        if not usuario_input or not senha_input:
            return False, "Preencha todos os campos.", None

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT usuario, senha, data_expiracao FROM usuarios WHERE usuario = ? AND senha = ?",
            (usuario_input, senha_input),
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            try:
                data_expiracao = datetime.strptime(user[2], "%Y-%m-%d")
                if datetime.now() > data_expiracao:
                    return False, "Licença expirada. Renove para continuar.", None
                return True, f"Bem-vindo! Licença válida até {data_expiracao.strftime('%d/%m/%Y')}", user[0]
            except ValueError:
                return False, "Erro na data de expiração.", None

        return False, "Usuário ou senha incorretos.", None

    def login(e):
        valido, mensagem, usuario_logado = verificar_usuario(usuario.value, senha.value)
        if valido:
            if lembrar_senha.value:
                salvar_usuario_lembrado(usuario.value, senha.value)
            else:
                limpar_usuario_lembrado()
            exibir_mensagem(mensagem, sucesso=True)
            mostrar_menu(page, usuario_logado)
        else:
            exibir_mensagem(mensagem, sucesso=False)

    # Carrega o último usuário e senha lembrados
    usuario_lembrado, senha_lembrada = carregar_usuario_lembrado()

    # Campos de entrada
    usuario = ft.TextField(
        label="Usuário",
        prefix_icon=ft.icons.PERSON,
        width=400,
        height=60,
        border_radius=15,
        border_color=ft.colors.BLUE_GREY_300,
        focused_border_color=ft.colors.LIGHT_BLUE_500,
        color=ft.colors.BLACK,
        bgcolor=ft.colors.BLUE_GREY_50,
        value=usuario_lembrado if usuario_lembrado else "",
        on_submit=login
    )

    senha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK,
        width=400,
        height=60,
        border_radius=15,
        border_color=ft.colors.BLUE_GREY_300,
        focused_border_color=ft.colors.LIGHT_BLUE_500,
        color=ft.colors.BLACK,
        bgcolor=ft.colors.BLUE_GREY_50,
        value=senha_lembrada if senha_lembrada else "",
        on_submit=login
    )

    lembrar_senha = ft.Checkbox(
        label="Lembrar credenciais",
        value=bool(usuario_lembrado and senha_lembrada),
        label_style=ft.TextStyle(color=ft.colors.BLUE_GREY_700, size=16),
        fill_color=ft.colors.BLUE_ACCENT,
    )

    login_button = ft.ElevatedButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.LOGIN, size=20),
                ft.Text("Login", size=18)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        on_click=login,
        width=400,
        height=55,
        bgcolor=ft.colors.BLUE_ACCENT,
        color=ft.colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=15),
            elevation=10,
            overlay_color=ft.colors.LIGHT_BLUE_200,
            animation_duration=300,
        ),
    )

    # Layout principal
    page.clean()
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Image(src=RUTA_LOGO, width=300, height=300, opacity=0.9),
                    ft.Text(
                        "Bem-vindo!",
                        size=36,
                        weight="bold",
                        color=ft.colors.BLUE_GREY_900,
                        text_align="center",
                    ),
                    usuario,
                    senha,
                    ft.Row(
                        controls=[lembrar_senha],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    login_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                expand=True,
            ),
            padding=50,
            border_radius=30,
            shadow=ft.BoxShadow(
                spread_radius=12,
                blur_radius=30,
                color=ft.colors.BLACK26,
                offset=ft.Offset(2, 5),
            ),
            alignment=ft.alignment.center,
        )
    )

    aplicar_tema()
