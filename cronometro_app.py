import flet as ft
import threading
import time
from datetime import datetime, timezone, timedelta
from cronometro import Cronometro
from config import RUTA_START_SOUND, RUTA_END_SOUND, TEMA, RUTA_LOGO

class CronometroControl(ft.UserControl):
    def __init__(self, page, usuario, on_voltar=None):
        super().__init__()
        self.page = page
        self.usuario = usuario
        self.on_voltar = on_voltar
        self.cronometro = Cronometro()

        # Flags de controle e variáveis extras para UX
        self.stop_data_timer = False
        self.stop_progress_timer = False
        self.pulsando = False  # Para animação de pulso
        self.minimal_mode = False  # Modo minimalista que oculta controles
        self.historico_tempos = []  # Guarda os últimos tempos configurados

        # Configuração inicial da janela, tema e dimensões
        self.page.window.full_screen = True
        self.theme = TEMA
        self.update_dimensions()
        self.apply_theme()

        # Adiciona handler para redimensionamento da janela
        self.page.on_resize = self.resize_handler

        # Configuração do cronômetro e elementos visuais
        self.cronometro.definir_duracao(5 * 60)
        self.tempo_configurado = 5
        self.som_fim_tocado = False

        self.contador_tempo = ft.Text(
            value="05:00",
            size=self.contador_size,
            weight="bold",
            color=self.text_color,
            text_align=ft.TextAlign.CENTER,
            animate_scale=300  # Animação de escala (usada também na animação de início)
        )

        self.tempo_configurado_texto = ft.Text(
            value=f"Tempo: {self.tempo_configurado} minutos",
            size=20,
            color=self.text_color,
            text_align=ft.TextAlign.CENTER
        )

        # --- Implementação corrigida da barra de progresso ---
        self.barra_progresso_container = ft.Container(
            width=self.progress_bar_width,
            height=40,
            border_radius=20,
            bgcolor=ft.colors.GREY_800 if self.theme == "Escuro" else ft.colors.GREY_300,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            padding=0,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLACK54,
                offset=ft.Offset(0, 3)
            )
        )

        self.barra_progresso_interna = ft.Container(
            width=0,
            height=40,
            border_radius=20,
            animate=ft.animation.Animation(800, "easeOutQuint"),
            gradient=ft.LinearGradient(
                begin=ft.alignment.center_left,
                end=ft.alignment.center_right,
                colors=[ft.colors.GREEN_ACCENT, ft.colors.AMBER]
            )
        )

        self.barra_indicador = ft.Container(
            width=40,
            height=40,
            bgcolor=ft.colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.colors.BLACK54,
                offset=ft.Offset(0, 3)
            ),
            alignment=ft.alignment.center,
            content=ft.Icon(ft.icons.TIMER, size=20, color=ft.colors.BLACK87),
            animate_position=ft.animation.Animation(600, "easeOutBack"),
            animate_scale=ft.animation.Animation(400, "easeOutBack")
        )

        self.container_barra_progresso = ft.Stack(
            controls=[
                self.barra_progresso_container,
                ft.Container(
                    content=ft.Stack([
                        self.barra_progresso_interna,
                        self.barra_indicador
                    ]),
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    border_radius=20
                )
            ]
        )
        # --- Fim da implementação corrigida ---

        self.data_hora_texto = ft.Text(
            value=self.obter_data_hora(),
            size=60,
            color=self.text_color,
            weight="bold",
            text_align=ft.TextAlign.CENTER
        )

        # Áudios
        self.start_audio = ft.Audio(src=RUTA_START_SOUND)
        self.end_audio = ft.Audio(src=RUTA_END_SOUND)
        self.page.overlay.extend([self.start_audio, self.end_audio])

        # Atalhos de teclado
        self.page.on_keyboard_event = self.handle_key_event

        # Inicializa variável para otimização de atualizações
        self.ultimo_progresso = 0

        # Monta o layout inicial
        self.page.add(self.build())
        self.start_data_timer()

    def resize_handler(self, event):
        """Handler chamado quando a janela é redimensionada."""
        self.update_dimensions()
        self.page.clean()
        self.page.add(self.build())
        self.page.update()

    def update_dimensions(self):
        largura_janela = self.page.window.width
        self.logo_size = largura_janela * 0.2
        self.contador_size = max(250, largura_janela * 0.06)
        self.button_width = max(50, largura_janela * 0.06)
        self.button_height = max(30, largura_janela * 0.02)
        self.button_spacing = max(5, largura_janela * 0.01)
        self.progress_bar_width = largura_janela * 0.85

    def apply_theme(self):
        if self.theme == "Escuro":
            self.primary_color = ft.colors.BLUE_GREY_900
            self.secondary_color = ft.colors.BLUE_GREY_50
            self.text_color = ft.colors.WHITE
            self.button_color = ft.colors.BLUE_GREY_700
            self.button_text_color = ft.colors.WHITE
            self.timer_background_color = ft.colors.BLACK
            self.progress_bar_color = ft.colors.LIGHT_GREEN_700
            self.gradient_colors = [ft.colors.BLUE_GREY_900, ft.colors.BLUE_GREY_700]
        else:
            self.primary_color = ft.colors.BLUE_GREY_50
            self.secondary_color = ft.colors.WHITE
            self.text_color = ft.colors.BLACK
            self.button_color = ft.colors.BLUE_GREY_300
            self.button_text_color = ft.colors.BLACK
            self.timer_background_color = ft.colors.WHITE
            self.progress_bar_color = ft.colors.GREEN_700
            self.gradient_colors = [ft.colors.LIGHT_BLUE_100, ft.colors.WHITE]

    def obter_data_hora(self):
        return datetime.now(timezone(timedelta(hours=-3))).strftime("%d de %B de %Y, %H:%M:%S")

    def start_data_timer(self):
        def tick():
            if self.stop_data_timer:
                return
            self.atualizar_data_hora()
            threading.Timer(1.0, tick).start()
        tick()

    def atualizar_data_hora(self):
        self.data_hora_texto.value = self.obter_data_hora()
        self.data_hora_texto.update()

    def build(self):
        self.update_dimensions()
        self.apply_theme()
        self.page.title = "Aplicação Cronômetro"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        if self.minimal_mode:
            controls = [
                ft.Container(
                    content=ft.Image(src=RUTA_LOGO, width=self.logo_size, height=self.logo_size),
                    alignment=ft.alignment.top_center,
                    padding=ft.padding.only(top=-100, bottom=10)
                ),
                self.data_hora_texto,
                ft.Container(
                    content=ft.Column(
                        controls=[self.contador_tempo],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                    border_radius=ft.border_radius.all(10),
                    bgcolor=self.timer_background_color,
                    shadow=ft.BoxShadow(
                        spread_radius=5,
                        blur_radius=20,
                        color=ft.colors.BLACK26,
                        offset=ft.Offset(0, 4)
                    )
                ),
                ft.Container(height=10),
                self.container_barra_progresso,
                ft.Container(height=10),
                self.create_button("Sair do Modo Minimalista", ft.icons.CANCEL, self.toggle_minimal_mode, tooltip="Exibe todos os controles")
            ]
        else:
            historico_dropdown = None
            if self.historico_tempos:
                historico_dropdown = ft.Dropdown(
                    label="Histórico de Tempos",
                    width=150,
                    options=[ft.dropdown.Option(f"{t} minutos") for t in sorted(self.historico_tempos)],
                    on_change=lambda e: self.selecionar_tempo(e.control.value),
                    tooltip="Selecione um tempo previamente usado"
                )
            controls = [
                ft.Container(
                    content=ft.Image(src=RUTA_LOGO, width=self.logo_size, height=self.logo_size),
                    alignment=ft.alignment.top_center,
                    padding=ft.padding.only(top=-100, bottom=10)
                ),
                ft.Container(
                    content=self.data_hora_texto,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=-100, bottom=5)
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[self.contador_tempo, self.tempo_configurado_texto],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                    border_radius=ft.border_radius.all(10),
                    bgcolor=self.timer_background_color,
                    shadow=ft.BoxShadow(
                        spread_radius=5,
                        blur_radius=20,
                        color=ft.colors.BLACK26,
                        offset=ft.Offset(0, 4)
                    )
                ),
                ft.Container(height=10),
                self.container_barra_progresso,
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        self.create_button("Iniciar", ft.icons.PLAY_ARROW, self.iniciar, tooltip="Inicia o cronômetro"),
                        self.create_button("Pausar", ft.icons.PAUSE, self.pausar, tooltip="Pausa o cronômetro"),
                        self.create_button("Retomar", ft.icons.PLAY_ARROW, self.retomar, tooltip="Retoma o cronômetro"),
                        self.create_button("Reiniciar", ft.icons.RESTART_ALT, self.reiniciar, tooltip="Reinicia o cronômetro"),
                        self.create_button("Parar", ft.icons.STOP, self.confirm_parar, tooltip="Pede confirmação para parar o cronômetro")
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=self.button_spacing,
                    wrap=True
                ),
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        self.create_button("Voltar", ft.icons.ARROW_BACK, self.voltar_menu, width_multiplier=2, tooltip="Volta ao menu principal"),
                        self.create_button("Tela Cheia", ft.icons.FULLSCREEN, self.toggle_full_screen, tooltip="Alterna modo tela cheia"),
                        self.create_button("Tema", ft.icons.BRIGHTNESS_4, self.toggle_theme, tooltip="Alterna entre temas"),
                        self.create_button("Atalhos", ft.icons.INFO, self.mostrar_atalhos, tooltip="Exibe os atalhos de teclado"),
                        self.create_button("Tempo", "⏱️", self.abrir_dialogo_tempo, tooltip=f"Configura o tempo (atual: {self.tempo_configurado} minutos)"),
                        self.create_button("Modo Minimalista", ft.icons.VIDEOCAM_OFF, self.toggle_minimal_mode, tooltip="Oculta controles durante a contagem")
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=self.button_spacing,
                    wrap=True
                ),
                historico_dropdown if historico_dropdown else ft.Container()
            ]
        return ft.Container(
            content=ft.Column(
                controls=controls,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            ),
            padding=80,
            border_radius=30,
            shadow=ft.BoxShadow(
                spread_radius=5,
                blur_radius=25,
                color=ft.colors.BLACK26,
                offset=ft.Offset(2, 4)
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=self.gradient_colors
            ),
            alignment=ft.alignment.top_center
        )

    def create_button(self, text, icon, on_click, width_multiplier=1, tooltip=""):
        if isinstance(icon, str):
            icon_widget = ft.Text(value=icon, size=self.button_height)
        else:
            icon_widget = ft.Icon(icon=icon, size=self.button_height)
        btn = ft.ElevatedButton(
            text=text,
            icon=icon_widget,
            on_click=on_click,
            width=self.button_width * width_multiplier,
            height=self.button_height,
            bgcolor=self.button_color,
            color=self.button_text_color,
            tooltip=tooltip,
            animate_opacity=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                overlay_color=ft.colors.TRANSPARENT
            )
        )
        btn_container = ft.Container(
            content=btn,
            shadow=ft.BoxShadow(
                spread_radius=4,
                blur_radius=25,
                color=ft.colors.BLACK26,
                offset=ft.Offset(2, 4)
            )
        )
        btn.on_hover = lambda e: self.animar_botao(btn_container, e.data == "true")
        return btn_container

    def animar_botao(self, container, hover):
        container.scale = 1.1 if hover else 1
        container.update()

    def abrir_dialogo_tempo(self, e):
        def definir_tempo(e):
            try:
                minutos = int(minutos_input.value)
                if minutos <= 0:
                    raise ValueError
                self.cronometro.definir_duracao(minutos * 60)
                self.contador_tempo.value = f"{minutos:02}:00"
                self.tempo_configurado = minutos
                self.tempo_configurado_texto.value = f"Tempo: {self.tempo_configurado} minutos"
                if minutos not in self.historico_tempos:
                    self.historico_tempos.append(minutos)
                dialog.open = False
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Cronômetro configurado para {minutos} minutos"), open=True)
                )
                self.page.update()
            except ValueError:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Por favor, insira um valor válido de minutos."), open=True)
                )
        minutos_input = ft.TextField(
            label="Minutos",
            value=str(self.tempo_configurado),
            width=100,
            height=50,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        dialog = ft.AlertDialog(
            title=ft.Text("Definir Tempo Manual"),
            content=minutos_input,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialogo(e, dialog)),
                ft.TextButton("Definir", on_click=definir_tempo),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def fechar_dialogo(self, e, dialog):
        dialog.open = False
        self.page.update()

    def selecionar_tempo(self, valor):
        try:
            minutos = int(valor.split()[0])
            self.cronometro.definir_duracao(minutos * 60)
            self.contador_tempo.value = f"{minutos:02}:00"
            self.tempo_configurado = minutos
            self.tempo_configurado_texto.value = f"Tempo: {self.tempo_configurado} minutos"
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Cronômetro configurado para {minutos} minutos"), open=True)
            )
            self.page.update()
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Erro ao selecionar tempo: {str(ex)}"), open=True)
            )

    def mostrar_atalhos(self, e):
        dialog = ft.AlertDialog(
            title=ft.Text("Atalhos de Teclado"),
            content=ft.Text(
                "Atalhos de Teclado:\n"
                "- Iniciar: Enter\n"
                "- Pausar: Espaço\n"
                "- Reiniciar: R\n"
                "- Retomar: C"
            ),
            actions=[ft.TextButton("Fechar", on_click=lambda e: self.fechar_dialogo(e, dialog))],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def enviar_notificacao(self):
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text("Tempo esgotado!"), open=True)
        )
        self.tocar_som_fim()

    def tocar_som_inicio(self):
        self.start_audio.play()

    def tocar_som_fim(self):
        self.end_audio.play()

    def start_progress_timer(self):
        def tick():
            if self.stop_progress_timer:
                return
            self.atualizar_progresso()
            threading.Timer(0.05, tick).start()
        tick()

    # Função de atualização de cores corrigida
    def atualizar_cores_progresso(self, progresso):
        # Transição de cores suave
        if progresso < 0.5:
            color1 = ft.colors.GREEN_ACCENT
            color2 = ft.colors.LIGHT_GREEN_ACCENT_200
        elif progresso < 0.75:
            color1 = ft.colors.AMBER
            color2 = ft.colors.DEEP_ORANGE_300
        else:
            color1 = ft.colors.RED_ACCENT_400
            color2 = ft.colors.DEEP_ORANGE_ACCENT_700

        # Atualiza gradiente com animação
        self.barra_progresso_interna.gradient = ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=[color1, color2]
        )
        
        # Efeito de pulso no indicador
        if progresso > 0.9 and not self.pulsando:
            self.barra_indicador.scale = 1.2
            self.barra_indicador.update()
            self.pulsando = True
        elif progresso <= 0.9 and self.pulsando:
            self.barra_indicador.scale = 1.0
            self.barra_indicador.update()
            self.pulsando = False

        # Atualiza cor do texto
        self.contador_tempo.color = color1

    def hsl_to_rgb(self, h, s, l):
        """Converte valores HSL para RGB"""
        s /= 100
        l /= 100
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        return r, g, b

    def atualizar_progresso(self):
        restante = self.cronometro.tempo_restante()
        if restante <= 0:
            if not self.som_fim_tocado:
                self.enviar_notificacao()
                self.som_fim_tocado = True
            def reiniciar_apos_delay():
                try:
                    self.reiniciar(None)
                except Exception as ex:
                    self.page.show_snack_bar(
                        ft.SnackBar(content=ft.Text(f"Erro no reinício: {str(ex)}"), open=True)
                    )
            threading.Timer(5.0, reiniciar_apos_delay).start()
            self.stop_progress_timer = True
            return

        progresso = 1 - (restante / self.cronometro.duracao)
        nova_largura = self.progress_bar_width * progresso
        
        # Atualiza apenas se houver mudança relevante
        if abs(nova_largura - self.barra_progresso_interna.width) > 1:
            self.barra_progresso_interna.width = nova_largura
            self.barra_indicador.left = min(nova_largura - 20, self.progress_bar_width - 40)
            
            self.atualizar_cores_progresso(progresso)
            
            self.barra_progresso_interna.update()
            self.barra_indicador.update()
            
        # Atualização contínua do contador
        self.contador_tempo.value = f"{int(restante//60):02}:{int(restante%60):02}"
        self.contador_tempo.update()

    def iniciar_animacao_pulso(self):
        """Inicia a animação de pulso para alertar que o tempo está acabando."""
        self.pulsando = True
        def animar():
            while self.pulsando:
                self.contador_tempo.opacity = 0.5
                self.contador_tempo.scale = 1.05
                self.contador_tempo.update()
                time.sleep(0.5)
                self.contador_tempo.opacity = 1
                self.contador_tempo.scale = 1
                self.contador_tempo.update()
                time.sleep(0.5)
        threading.Thread(target=animar, daemon=True).start()

    def parar_animacao_pulso(self):
        """Para a animação de pulso e restaura os valores padrão."""
        self.pulsando = False
        self.contador_tempo.opacity = 1
        self.contador_tempo.scale = 1
        self.contador_tempo.update()

    def reiniciar(self, e):
        try:
            self.cronometro.reiniciar()
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Cronômetro reiniciado"), open=True)
            )
            self.contador_tempo.value = f"{int(self.tempo_configurado):02}:00"
            self.contador_tempo.color = self.text_color
            self.contador_tempo.update()
            self.barra_progresso_interna.width = 0
            self.barra_progresso_interna.update()
            self.barra_indicador.left = 0
            self.barra_indicador.update()
            self.som_fim_tocado = False
            self.stop_progress_timer = True
            time.sleep(0.05)
            self.stop_progress_timer = False
            self.parar_animacao_pulso()
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Erro ao reiniciar: {str(ex)}"), open=True)
            )
        self.page.update()

    def iniciar(self, e):
        try:
            self.cronometro.iniciar()
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Cronômetro iniciado"), open=True)
            )
            self.tocar_som_inicio()
            self.som_fim_tocado = False
            self.contador_tempo.scale = 1.2
            self.contador_tempo.update()
            time.sleep(0.1)
            self.contador_tempo.scale = 1
            self.contador_tempo.update()
            self.stop_progress_timer = True
            time.sleep(0.05)
            self.stop_progress_timer = False
            self.start_progress_timer()
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Erro ao iniciar: {str(ex)}"), open=True)
            )
        self.page.update()

    def pausar(self, e):
        try:
            self.cronometro.pausar()
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Cronômetro pausado"), open=True)
            )
            self.stop_progress_timer = True
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Erro ao pausar: {str(ex)}"), open=True)
            )
        self.page.update()

    def confirm_parar(self, e):
        """Exibe um pop-up de confirmação antes de parar o cronômetro."""
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmação"),
            content=ft.Text("Deseja realmente parar o cronômetro?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialogo(e, dialog)),
                ft.TextButton("Confirmar", on_click=lambda e: self.parar(e))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def parar(self, e):
        try:
            self.cronometro.parar()
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Cronômetro parado"), open=True)
            )
            self.contador_tempo.value = f"{int(self.tempo_configurado):02}:00"
            self.contador_tempo.color = self.text_color
            self.contador_tempo.update()
            self.barra_progresso_interna.width = 0
            self.barra_progresso_interna.update()
            self.barra_indicador.left = 0
            self.barra_indicador.update()
            self.som_fim_tocado = False
            self.stop_progress_timer = True
            self.parar_animacao_pulso()
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Erro ao parar: {str(ex)}"), open=True)
            )
        self.page.update()

    def retomar(self, e):
        try:
            self.cronometro.iniciar()
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Cronômetro retomado"), open=True)
            )
            self.stop_progress_timer = True
            time.sleep(0.05)
            self.stop_progress_timer = False
            self.start_progress_timer()
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Erro ao retomar: {str(ex)}"), open=True)
            )
        self.page.update()

    def handle_key_event(self, e: ft.KeyboardEvent):
        actions = {"enter": self.iniciar, " ": self.pausar, "r": self.reiniciar, "c": self.retomar}
        if e.key.lower() in actions:
            actions[e.key.lower()](e)

    def toggle_theme(self, e):
        self.theme = "Claro" if self.theme == "Escuro" else "Escuro"
        self.apply_theme()
        self.page.clean()
        self.page.add(self.build())
        self.page.update()

    def toggle_full_screen(self, e):
        self.page.window.full_screen = not self.page.window.full_screen
        self.page.update()

    def toggle_minimal_mode(self, e):
        """Alterna entre o modo completo e o modo minimalista."""
        self.minimal_mode = not self.minimal_mode
        self.page.clean()
        self.page.add(self.build())
        self.page.update()

    def voltar_menu(self, e):
        if self.cronometro.em_andamento:
            self.cronometro.parar()
        self.stop_data_timer = True
        self.stop_progress_timer = True
        self.page.overlay.clear()
        from menu_principal import mostrar_menu
        mostrar_menu(self.page, self.usuario)

    def voltar(self):
        if self.on_voltar:
            self.on_voltar()
