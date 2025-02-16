import flet as ft
from datetime import datetime
import locale
import pygame
import json
import os
import logging
import asyncio

# Paleta de cores extraída da logo
logo_primary_color = "#1A532D"  # Verde das folhas
logo_secondary_color = "#654321"  # Marrom do tronco
logo_text_color = "#000000"  # Preto do círculo
logo_background_color = "#FFFFFF"  # Branco do fundo
logo_accent_color = "#4B4B4B"  # Cinza escuro para o fundo do cronômetro

# Configurar a localidade para português do Brasil
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

# Inicialização do mixer PyGame para reprodução de som
pygame.mixer.init()

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"
SESSION_FILE = "session.json"

class CronometroApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.bg_color = logo_background_color  # Usando a cor de fundo da logo como fundo do app
        self.fg_color = logo_text_color  # Usando a cor do texto da logo
        self.button_color = logo_primary_color  # Usando a cor principal da logo para os botões
        self.hover_color = logo_secondary_color  # Usando a cor secundária da logo para hover
        self.bg_image_path = ""
        self.logo_path = "/mnt/data/logo.png"
        self.sounds = {"start": None, "alert": None, "end": None}
        self.icons = {
            "tribune": None,
            "free_speech": None,
            "final_considerations": None,
            "manual_time": None,
            "config": None,
            "rest": None,
            "exit": None
        }
        self.icon_buttons = {}
        self.running = False
        self.current_time = 0

        # Definir cores da logo como atributos da instância
        self.logo_secondary_color = logo_secondary_color
        self.logo_background_color = logo_background_color
        self.logo_primary_color = logo_primary_color
        self.logo_text_color = logo_text_color
        self.logo_accent_color = logo_accent_color

        self.build()

    def build(self):
        self.page.title = "Cronômetro Câmara Municipal de Ouvidor"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.bgcolor = self.bg_color

        self.load_config()
        self.setup_login_screen()
        self.load_session()

        self.page.on_resize = self.on_page_resize

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.bg_color = config.get("bg_color", self.bg_color)
                self.fg_color = config.get("fg_color", self.fg_color)
                self.button_color = config.get("button_color", self.button_color)
                self.hover_color = config.get("hover_color", self.hover_color)
                self.bg_image_path = config.get("bg_image_path", self.bg_image_path)
                self.logo_path = config.get("logo_path", self.logo_path)
                self.sounds = config.get("sounds", self.sounds)
                self.icons = config.get("icons", self.icons)
            logger.info("Configurações carregadas com sucesso.")
        else:
            self.save_config()

    def save_config(self):
        config = {
            "bg_color": self.bg_color,
            "fg_color": self.fg_color,
            "button_color": self.button_color,
            "hover_color": self.hover_color,
            "bg_image_path": self.bg_image_path,
            "logo_path": self.logo_path,
            "sounds": self.sounds,
            "icons": self.icons
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info("Configurações salvas com sucesso.")

    def load_session(self):
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                session = json.load(f)
                if session.get("logged_in"):
                    self.setup_main_menu()
            logger.info("Sessão carregada com sucesso.")
        else:
            logger.info("Nenhuma sessão encontrada.")

    def save_session(self, logged_in: bool):
        session = {
            "logged_in": logged_in
        }
        with open(SESSION_FILE, 'w') as f:
            json.dump(session, f, indent=4)
        logger.info("Sessão salva com sucesso.")

    def setup_login_screen(self):
        self.page.controls.clear()

        self.logo = ft.Image(src=self.logo_path)
        self.title_label = ft.Text(value="Nome do Software", size=24, color=self.fg_color)
        self.date_time_label = ft.Text(value="", size=16, color=self.fg_color)

        self.username_label = ft.Text(value="Usuário:", size=16, color=self.fg_color)
        self.username_entry = ft.TextField(width=300, border_color=self.fg_color, color=self.logo_secondary_color, text_style=ft.TextStyle(color=self.logo_secondary_color))

        self.password_label = ft.Text(value="Senha:", size=16, color=self.fg_color)
        self.password_entry = ft.TextField(width=300, border_color=self.fg_color, password=True, color=self.logo_secondary_color, text_style=ft.TextStyle(color=self.logo_secondary_color))

        self.login_button = ft.ElevatedButton(text="Entrar", on_click=self.login, bgcolor=self.button_color, color=self.logo_background_color)

        self.page.add(
            ft.Column(
                controls=[
                    self.logo,
                    self.title_label,
                    self.date_time_label,
                    self.username_label,
                    self.username_entry,
                    self.password_label,
                    self.password_entry,
                    self.login_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        )
        self.page.update()

    def login(self, e):
        username = self.username_entry.value
        password = self.password_entry.value
        if username == "admin" and password == "admin":
            self.save_session(logged_in=True)
            self.setup_main_menu()
        else:
            self.page.overlay.append(
                ft.AlertDialog(
                    title="Erro",
                    content=ft.Text("Credenciais inválidas!"),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: self.page.overlay.clear())
                    ]
                )
            )
            self.page.update()

    def setup_main_menu(self, e=None):
        self.page.controls.clear()

        self.logo = ft.Image(src=self.logo_path)
        self.date_time_label = ft.Text(value="", size=16, color=self.fg_color)

        buttons = [
            ("Tribuna", self.start_tribune_timer),
            ("Palavra Livre", self.start_free_speech_timer),
            ("Tempo Manual", self.set_manual_time),
            ("Configurações", self.open_config),
            ("Descanso de Tela", self.show_rest_screen),
            ("Sair", self.logout)
        ]
        button_controls = []
        for text, command in buttons:
            button_controls.append(ft.ElevatedButton(text=text, on_click=command, bgcolor=self.button_color, color=self.logo_background_color))

        self.page.add(
            ft.Column(
                controls=[
                    ft.Container(
                        content=self.logo,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=button_controls,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        alignment=ft.alignment.top_center,
                        padding=ft.padding.all(10)
                    ),
                    self.date_time_label
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        )
        self.page.update()

    def logout(self, e):
        self.save_session(logged_in=False)
        self.setup_login_screen()

    async def update_date_time(self):
        while True:
            current_time = datetime.now().strftime("%d de %B de %Y, %H:%M:%S")
            self.date_time_label.value = current_time
            self.page.update()
            await asyncio.sleep(1)

    def on_page_resize(self, event):
        self.page.update()

    def start_tribune_timer(self, e):
        self.start_timer(300)

    def start_free_speech_timer(self, e):
        self.start_timer(300)

    def start_final_considerations_timer(self, e):
        self.start_timer(300)

    def start_aporte_timer(self, e):
        self.start_timer(300)

    def set_manual_time(self, e):
        manual_time = ft.ask("Tempo Manual", "Insira o tempo em segundos:", ft.number_input)
        if manual_time:
            self.start_timer(manual_time)

    def start_timer(self, seconds: int):
        self.page.controls.clear()
        self.current_time = seconds
        self.timer_label = ft.Text(
            value=f"{seconds//60:02}:{seconds%60:02}",
            size=180,
            color="red",
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.BOLD
        )
        timer_container = ft.Container(
            content=self.timer_label,
            width=500,
            height=500,
            alignment=ft.alignment.center,
            bgcolor=self.logo_accent_color,
            border_radius=250,
        )

        buttons = [
            ("Iniciar", self.start_countdown),
            ("Pausar", self.pause_timer),
            ("Parar", self.stop_timer),
            ("Reiniciar", lambda e: self.reset_timer(seconds)),
            ("Voltar", self.setup_main_menu),
            ("Aporte", self.start_aporte_timer),
            ("Considerações Finais", self.start_final_considerations_timer)
        ]
        button_controls = []
        for text, command in buttons:
            button_controls.append(ft.ElevatedButton(text=text, on_click=command, bgcolor=self.button_color, color=self.logo_background_color))

        self.page.add(
            ft.Column(
                controls=[
                    ft.Container(
                        content=timer_container,
                        alignment=ft.alignment.center,
                        padding=ft.padding.all(20)
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=button_controls,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        alignment=ft.alignment.bottom_center,
                        padding=ft.padding.all(10)
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        )
        self.page.update()

    def start_countdown(self, e):
        if not self.running:
            self.running = True
            asyncio.run(self.update_timer())

    async def update_timer(self):
        while self.running:
            if self.current_time > 0:
                minutes, seconds = divmod(self.current_time, 60)
                self.timer_label.value = f"{minutes:02}:{seconds:02}"
                self.page.update()
                self.current_time -= 1
                await asyncio.sleep(1)
            else:
                self.timer_label.value = "00:00"
                self.running = False
                self.page.update()
                if self.sounds["end"]:
                    self.sounds["end"].play()
        if self.sounds["alert"]:
            self.sounds["alert"].play()

    def stop_timer(self, e):
        self.running = False
        if self.sounds["end"]:
            self.sounds["end"].play()

    def pause_timer(self, e):
        self.running = False

    def reset_timer(self, seconds: int):
        self.current_time = seconds
        self.timer_label.value = f"{seconds//60:02}:{seconds%60:02}"
        self.running = False
        self.page.update()

    def show_rest_screen(self, e):
        self.page.controls.clear()
        self.logo_label = ft.Image(src=self.logo_path)
        self.session_label = ft.Text(value="Sessão Plenária", size=48, color=self.fg_color)
        self.date_time_label = ft.Text(value="", size=24, color=self.fg_color)
        self.back_button = ft.ElevatedButton(text="Voltar", on_click=self.setup_main_menu, bgcolor=self.button_color, color=self.logo_background_color)

        self.page.add(
            ft.Column(
                controls=[
                    self.logo_label,
                    self.session_label,
                    self.date_time_label,
                    self.back_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        )
        self.page.update()

    def select_sound(self, prompt: str) -> str:
        file_picker = ft.FilePicker(on_result=lambda e: self.file_picker_result(e, prompt))
        self.page.overlay.append(file_picker)
        file_picker.pick_files()
        return file_picker

    def file_picker_result(self, e, prompt):
        if e.files:
            return e.files[0].path
        return None

    def open_config(self, e):
        self.page.controls.clear()

        buttons = [
            ("Selecionar Cor de Fundo", self.select_bg_color),
            ("Selecionar Imagem de Fundo", self.select_bg_image),
            ("Selecionar Logo", self.select_logo),
            ("Selecionar Som de Início", lambda e: self.set_sound('start')),
            ("Selecionar Som de Alerta", lambda e: self.set_sound('alert')),
            ("Selecionar Som de Fim", lambda e: self.set_sound('end'))
        ]
        button_controls = []
        for text, command in buttons:
            button_controls.append(ft.ElevatedButton(text=text, on_click=command, bgcolor=self.button_color, color=self.logo_background_color))

        self.theme_label = ft.Text(value="Selecionar Tema", color=self.fg_color)
        self.theme_var = ft.Dropdown(
            options=[
                ft.dropdown.Option("Claro"),
                ft.dropdown.Option("Escuro")
            ],
            value="Claro",
            on_change=self.apply_theme
        )

        self.save_config_button = ft.ElevatedButton(text="Salvar Configurações", on_click=self.save_and_close_config, bgcolor=self.button_color, color=self.logo_background_color)

        self.page.add(
            ft.Column(
                controls=[
                    self.theme_label,
                    self.theme_var,
                    ft.Column(
                        controls=button_controls,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self.save_config_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        )
        self.page.update()

    def select_bg_color(self, e):
        dialog = ft.AlertDialog(
            title="Selecionar Cor de Fundo",
            content=ft.ColorPicker(),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.on_color_picked(e, dialog)),
                ft.TextButton("Cancel", on_click=lambda e: dialog.close()),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def on_color_picked(self, e, dialog):
        color_code = dialog.content.color
        if color_code:
            self.bg_color = color_code
            self.page.update()
            self.apply_theme(e)
        dialog.open = False
        self.page.update()

    def select_bg_image(self, e):
        file_picker = ft.FilePicker(on_result=self.file_picker_result)
        self.page.overlay.append(file_picker)
        file_picker.pick_files(file_types=[ft.file_picker.FileType(type="image")])

    def select_logo(self, e):
        file_picker = ft.FilePicker(on_result=self.file_picker_result)
        self.page.overlay.append(file_picker)
        file_picker.pick_files(file_types=[ft.file_picker.FileType(type="image")])

    def set_sound(self, sound_type: str, e):
        sound_path = self.select_sound(f"Selecionar Som de {sound_type.capitalize()}")
        if sound_path:
            self.sounds[sound_type] = pygame.mixer.Sound(sound_path)
            self.page.update()

    def apply_theme(self, e):
        theme = self.theme_var.value
        if theme == "Claro":
            self.bg_color = logo_background_color
            self.fg_color = logo_text_color
        else:
            self.bg_color = logo_secondary_color
            self.fg_color = logo_background_color
        self.page.update()

    def save_and_close_config(self, e):
        self.save_config()
        self.setup_main_menu()

def main(page: ft.Page):
    asyncio.run(CronometroApp(page).update_date_time())
    CronometroApp(page)

ft.app(target=main)
