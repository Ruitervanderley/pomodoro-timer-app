import flet as ft
import threading
import time
import locale
from config import RUTA_LOGO
from datetime import datetime, timezone, timedelta
from cronometro_app import CronometroControl
from verify_license import obter_validade_serial
from configuracoes import configuracoes_page
from usuarios import gerenciar_usuarios

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

def mostrar_menu(page: ft.Page, usuario):
    """Função principal que exibe o menu do aplicativo."""

    page.theme_mode = "light"
    page.bgcolor = None
    page.title = "Menu Principal"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.spacing = 0

    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.BLUE_GREY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    page.update()

    def obter_data_hora():
        now = datetime.now(timezone(timedelta(hours=-3)))
        return now.strftime("%d de %B de %Y, %H:%M:%S")

    def atualizar_data_hora():
        while True:
            time.sleep(1)
            data_hora.value = obter_data_hora()
            data_hora.update()
            page.update()

    def iniciar(e):
        page.clean()
        cronometro_control = CronometroControl(page, usuario, on_voltar=lambda: mostrar_menu(page, usuario))
        page.add(cronometro_control)

    def sair(e):
        page.window_close()

    def handle_resize(e):
        ajustar_layout()
        page.update()

    def ajustar_layout():
        largura_janela = page.window.width
        altura_janela = page.window.height
        main_container.width = min(largura_janela * 0.95, 1300)
        main_container.height = min(altura_janela * 0.9, 900)
        logo_size = max(250, largura_janela * 0.18)
        logo_image.width = logo_size
        logo_image.height = logo_size

        button_width = max(160, min(largura_janela * 0.22, 300))
        button_height = 65
        for btn in buttons:
            btn.content.width = button_width
            btn.content.height = button_height

        main_container.update()

    validade_serial = obter_validade_serial(usuario)
    data_hora = ft.Text(
        value=obter_data_hora(),
        size=22,
        color=ft.colors.BLUE_GREY_900,
        weight="bold"
    )
    validade_texto = ft.Text(
        value=f"Validade: {validade_serial}",
        size=18,
        color=ft.colors.BLUE_GREY_900,
        weight="bold",
    )

    cabecalho = ft.Row(
        controls=[
            ft.Row([
                ft.Icon(ft.icons.CALENDAR_MONTH, color=ft.colors.BLUE_GREY_700, size=28),
                data_hora
            ], spacing=10),
            validade_texto,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    logo_image = ft.Image(
        src=RUTA_LOGO,
        fit=ft.ImageFit.CONTAIN,
        opacity=0.95,
        rotate=ft.transform.Rotate(0.01)
    )

    def create_button(text, icon, on_click):
        return ft.Container(
            content=ft.ElevatedButton(
                text=text,
                icon=icon,
                on_click=on_click,
                bgcolor=ft.colors.BLUE_GREY_700,
                color=ft.colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=25),
                    padding=ft.padding.symmetric(horizontal=25, vertical=18),
                    elevation=6,
                    overlay_color=ft.colors.WHITE10,
                    animation_duration=300,
                ),
                tooltip=text
            ),
            shadow=ft.BoxShadow(
                spread_radius=5,
                blur_radius=15,
                color=ft.colors.BLACK12,
                offset=ft.Offset(2, 5),
            ),
        )

    buttons = [
        create_button("Iniciar Cronômetro", ft.icons.PLAY_ARROW, iniciar),
        create_button("Configurações", ft.icons.SETTINGS, lambda e: configuracoes_page(page)),
        create_button("Gerenciar Usuários", ft.icons.PERSON, lambda e: gerenciar_usuarios(page, usuario)),
        create_button("Sair", ft.icons.EXIT_TO_APP, sair)
    ]

    botoes_row = ft.Row(
        controls=buttons,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        wrap=True
    )

    main_container = ft.Container(
        content=ft.Column(
            controls=[
                cabecalho,
                ft.Divider(color=ft.colors.BLUE_GREY_300, thickness=1),
                ft.Container(height=10),
                ft.Container(content=logo_image, alignment=ft.alignment.center),
                ft.Text(
                    value="Menu Principal",
                    size=40,
                    weight="bold",
                    color=ft.colors.BLUE_GREY_900,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Divider(color=ft.colors.BLUE_GREY_300, thickness=1),
                botoes_row
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30
        ),
        bgcolor=ft.colors.WHITE,
        border_radius=35,
        padding=40,
        shadow=ft.BoxShadow(
            spread_radius=10,
            blur_radius=25,
            color=ft.colors.BLACK26,
            offset=ft.Offset(4, 8),
        ),
        alignment=ft.alignment.center,
        width=900,
        height=600,
    )

    page.clean()
    page.add(main_container)

    threading.Thread(target=atualizar_data_hora, daemon=True).start()
    page.on_resize = handle_resize
    ajustar_layout()
    page.update()
