import flet as ft

def main(page: ft.Page):
    def tocar_som():
        try:
            audio = ft.Audio(src="assets/start_sound.wav", autoplay=True)
            page.overlay.append(audio)
            page.update()
        except Exception as e:
            print(f"Erro ao reproduzir áudio: {e}")

    page.add(ft.ElevatedButton("Tocar Som", on_click=lambda _: tocar_som()))

ft.app(target=main)
