import flet as ft
from config import TEMA

def aplicar_tema(theme):
    """Aplica o tema baseado na configuração."""
    if theme == "Escuro":
        return {
            "background_color": ft.colors.GREY_900,
            "primary_color": ft.colors.BLUE_GREY_800,
            "secondary_color": ft.colors.BLUE_GREY_700,
            "text_color": ft.colors.WHITE,
            "button_color": ft.colors.BLUE_700,
            "button_text_color": ft.colors.WHITE,
            "timer_background_color": ft.colors.GREY_800,
            "progress_bar_color": ft.colors.BLUE_500,
            "progress_bar_color_good": ft.colors.GREEN_700,
            "progress_bar_color_warning": ft.colors.ORANGE_700,
            "progress_bar_color_danger": ft.colors.RED_700,
            "border_color": ft.colors.GREY_700,
            "shadow_color": ft.colors.BLACK54,
            "overlay_color": ft.colors.with_opacity(0.8, ft.colors.GREY_900),
            "text_color_warning": ft.colors.ORANGE_300,
            "text_color_danger": ft.colors.RED_300,
            "gradient_colors": [ft.colors.GREY_900, ft.colors.GREY_800],
            "hover_color": ft.colors.BLUE_400,
            "accent_color": ft.colors.ORANGE_400,
            "error_color": ft.colors.RED_500,
            "success_color": ft.colors.GREEN_500,
            "disabled_color": ft.colors.GREY_400,
        }
    else:  # Tema Claro
        return {
            "background_color": ft.colors.WHITE,
            "primary_color": ft.colors.BLUE_50,
            "secondary_color": ft.colors.WHITE,
            "text_color": ft.colors.GREY_900,
            "button_color": ft.colors.BLUE_500,
            "button_text_color": ft.colors.WHITE,
            "timer_background_color": ft.colors.GREY_100,
            "progress_bar_color": ft.colors.GREEN_600,
            "progress_bar_color_good": ft.colors.GREEN_700,
            "progress_bar_color_warning": ft.colors.ORANGE_700,
            "progress_bar_color_danger": ft.colors.RED_700,
            "border_color": ft.colors.GREY_300,
            "shadow_color": ft.colors.BLACK12,
            "overlay_color": ft.colors.with_opacity(0.5, ft.colors.GREY_900),
            "text_color_warning": ft.colors.ORANGE_300,
            "text_color_danger": ft.colors.RED_300,
            "gradient_colors": [ft.colors.BLUE_50, ft.colors.WHITE],
            "hover_color": ft.colors.BLUE_400,
            "accent_color": ft.colors.ORANGE_400,
            "error_color": ft.colors.RED_500,
            "success_color": ft.colors.GREEN_500,
            "disabled_color": ft.colors.GREY_400,
        }
