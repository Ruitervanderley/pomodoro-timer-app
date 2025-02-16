import flet as ft
import configparser
from config import salvar_configuracao, carregar_configuracao
from tema import aplicar_tema
from verify_license import obter_validade_serial

def configuracoes_page(page: ft.Page, usuario: str):
    """Constrói a interface de configurações."""

    # Lê config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Carrega valores do config
    start_sound_val = config['DEFAULT'].get('RUTA_START_SOUND', '')
    end_sound_val = config['DEFAULT'].get('RUTA_END_SOUND', '')
    tema_val = config['DEFAULT'].get('TEMA', 'Claro')
    tam_cronometro_val = config['DEFAULT'].get('TAMANHO_CRONOMETRO', '150')

    # Cria TextFields e Dropdown
    start_sound = ft.TextField(label="Som de Início", value=start_sound_val)
    end_sound = ft.TextField(label="Som de Fim", value=end_sound_val)
    tema = ft.Dropdown(
        label="Tema",
        value=tema_val,
        options=[ft.dropdown.Option("Claro"), ft.dropdown.Option("Escuro")],
    )
    tamanho_cronometro = ft.TextField(label="Tamanho do Cronômetro", value=tam_cronometro_val)

    def salvar_configuracoes(e):
        """Salva config e retorna ao menu."""
        config['DEFAULT'] = {
            'RUTA_LOGO': 'assets/logo.png',
            'RUTA_START_SOUND': start_sound.value,
            'RUTA_ALERT_SOUND': 'assets/alert_sound.wav',
            'RUTA_END_SOUND': end_sound.value,
            'TEMA': tema.value,
            'TAMANHO_CRONOMETRO': tamanho_cronometro.value
        }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        page.snack_bar = ft.SnackBar(content=ft.Text("Configurações salvas!"), open=True)
        page.update()
        voltar_menu(page, usuario)

    def voltar_menu(page_, usuario_):
        from menu_principal import mostrar_menu
        mostrar_menu(page_, usuario_)

    page.clean()
    # Monta layout
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(value="Configurações", size=32, weight="bold"),
                    start_sound,
                    end_sound,
                    tema,
                    tamanho_cronometro,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Salvar",
                                on_click=salvar_configuracoes,
                                width=200,
                                height=50,
                                bgcolor=ft.colors.BLUE_GREY_700,
                                color=ft.colors.WHITE,
                            ),
                            ft.ElevatedButton(
                                "Voltar",
                                on_click=lambda e: voltar_menu(page, usuario),
                                width=200,
                                height=50,
                                bgcolor=ft.colors.BLUE_GREY_700,
                                color=ft.colors.WHITE,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=50,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.colors.BLACK,
                offset=ft.Offset(2, 2)
            ),
            alignment=ft.alignment.center
        )
    )
    page.update()
