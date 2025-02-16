import flet as ft
import sqlite3
import os
import sys
from datetime import datetime, timedelta
from config import resource_path
from serial_utils import gerar_serial, salvar_serial

# Atualizando caminho do arquivo private_key.pem usando o resource_path
PRIVATE_KEY_PATH = resource_path("private_key.pem")

def get_database_path():
    if hasattr(sys, '_MEIPASS'):
        # Quando for executado como um executável compilado
        return os.path.join(sys._MEIPASS, 'database.db')
    else:
        # Quando estiver rodando no ambiente de desenvolvimento
        return os.path.join(os.path.abspath("."), 'database.db')

DATABASE_PATH = get_database_path()

def gerenciar_usuarios(page: ft.Page, usuario_logado):
    """Função para exibir e gerenciar os usuários cadastrados no sistema."""
    
    # Ajustes da página (fundo branco, centralizado)
    page.title = "Gerenciamento de Usuários"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.colors.WHITE

    # =========================================================================
    #                          Funções de Banco e Lógica
    # =========================================================================
    def carregar_usuarios(filtro_nome=None):
        """
        Carrega todos os usuários do banco de dados.
        Se 'filtro_nome' for fornecido, faz uma busca pelo nome do usuário.
        """
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        if filtro_nome:
            cursor.execute("""
                SELECT id, usuario, data_expiracao, admin, serial 
                FROM usuarios 
                WHERE usuario LIKE ?
            """, (f"%{filtro_nome}%",))
        else:
            cursor.execute("SELECT id, usuario, data_expiracao, admin, serial FROM usuarios")
        usuarios_ = cursor.fetchall()
        conn.close()
        return usuarios_

    def salvar_usuario(usuario_id, usuario_, admin_):
        """Salva alterações de nome/admin de um usuário."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET usuario = ?, admin = ? WHERE id = ?",
            (usuario_, admin_, usuario_id)
        )
        conn.commit()
        conn.close()

    def atualizar_senha_usuario(usuario_id, nova_senha):
        """Atualiza apenas a senha do usuário especificado."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET senha = ? WHERE id = ?",
            (nova_senha, usuario_id)
        )
        conn.commit()
        conn.close()

    def deletar_usuario(usuario_id):
        """Exclui um usuário, com confirmação."""
        def confirmar_exclusao(e):
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
            conn.commit()
            conn.close()

            fechar_dialogo(page)
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Usuário {usuario_id} deletado com sucesso!"), 
                open=True
            )
            page.update()
            gerenciar_usuarios(page, usuario_logado)

        # Diálogo de confirmação
        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(f"Tem certeza de que deseja excluir o usuário {usuario_id}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: fechar_dialogo(page)),
                ft.TextButton("Excluir", on_click=confirmar_exclusao, style=ft.ButtonStyle(bgcolor=ft.colors.RED_300))
            ],
        )
        page.dialog.open = True
        page.update()

    def editar_usuario(e, usuario_id):
        """Abre o diálogo para editar dados de um usuário (nome/admin)."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, admin FROM usuarios WHERE id = ?", (usuario_id,))
        usuario_, admin_ = cursor.fetchone()
        conn.close()

        usuario_input = ft.TextField(label="Usuário", value=usuario_)
        admin_checkbox = ft.Checkbox(label="Admin", value=bool(admin_))

        def salvar_alteracoes(e):
            salvar_usuario(usuario_id, usuario_input.value, admin_checkbox.value)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Usuário atualizado com sucesso!"), 
                open=True
            )
            page.update()
            gerenciar_usuarios(page, usuario_logado)

        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Editar Usuário {usuario_id}"),
            content=ft.Column([
                usuario_input,
                admin_checkbox,
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Salvar", on_click=salvar_alteracoes),
                ft.TextButton("Cancelar", on_click=lambda _: fechar_dialogo(page))
            ],
        )
        page.dialog.open = True
        page.update()

    def modificar_senha(e, usuario_id):
        """Abre o diálogo para modificar a senha de um usuário."""
        nova_senha_input = ft.TextField(label="Nova Senha", password=True, can_reveal_password=True)
        
        def salvar_nova_senha(e):
            if not nova_senha_input.value.strip():
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Por favor, insira uma senha válida."),
                    open=True
                )
                page.update()
                return
            atualizar_senha_usuario(usuario_id, nova_senha_input.value)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Senha modificada com sucesso!"),
                open=True
            )
            fechar_dialogo(page)
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Modificar Senha"),
            content=nova_senha_input,
            actions=[
                ft.TextButton("Salvar", on_click=salvar_nova_senha),
                ft.TextButton("Cancelar", on_click=lambda _: fechar_dialogo(page))
            ],
        )
        page.dialog.open = True
        page.update()

    def adicionar_usuario(e):
        """Abre o diálogo para adicionar um novo usuário."""
        usuario_input = ft.TextField(label="Usuário")
        senha_input = ft.TextField(label="Senha", password=True, can_reveal_password=True)
        admin_checkbox = ft.Checkbox(label="Admin")

        def salvar_novo_usuario(e):
            if not usuario_input.value.strip() or not senha_input.value.strip():
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Usuário e senha não podem ficar em branco."), 
                    open=True
                )
                page.update()
                return

            data_expiracao = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (usuario, senha, admin, data_expiracao) 
                VALUES (?, ?, ?, ?)
            """, (usuario_input.value, senha_input.value, admin_checkbox.value, data_expiracao))
            conn.commit()
            conn.close()

            fechar_dialogo(page)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Novo usuário criado com sucesso!"), 
                open=True
            )
            page.update()
            gerenciar_usuarios(page, usuario_logado)

        page.dialog = ft.AlertDialog(
            title=ft.Text("Adicionar Novo Usuário"),
            content=ft.Column([
                usuario_input,
                senha_input,
                admin_checkbox,
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Salvar", on_click=salvar_novo_usuario),
                ft.TextButton("Cancelar", on_click=lambda _: fechar_dialogo(page))
            ],
        )
        page.dialog.open = True
        page.update()

    def verificar_status_licenca(data_expiracao):
        """Verifica se a licença está ativa ou expirada."""
        if data_expiracao:
            try:
                validade = datetime.strptime(data_expiracao, '%Y-%m-%d')
                if datetime.now() > validade:
                    return "Expirado"
                else:
                    return "Ativo"
            except ValueError:
                return "Data Inválida"
        return "Sem Licença"

    def gerar_e_ativar_serial(usuario_id, usuario_):
        """Gera e ativa um serial para o usuário e exibe o serial gerado e validade."""
        try:
            serial = gerar_serial(usuario_, 365)  # Válido por 365 dias
            salvar_serial(serial)  # Salva o serial gerado (ex.: em arquivo)

            nova_data_expiracao = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuarios SET data_expiracao = ?, serial = ? WHERE id = ?",
                (nova_data_expiracao, serial, usuario_id)
            )
            conn.commit()
            conn.close()

            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Serial gerado e ativado para {usuario_}!"), 
                open=True
            )
            page.dialog = ft.AlertDialog(
                title=ft.Text("Serial Gerado"),
                content=ft.Text(f"Serial: {serial}\nValidade: {nova_data_expiracao}"),
                actions=[
                    ft.TextButton("Fechar", on_click=lambda _: fechar_dialogo(page))
                ],
            )
            page.dialog.open = True
            page.update()

        except FileNotFoundError as fnf_error:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Erro: {fnf_error}"), 
                open=True
            )
            page.update()

    def fechar_dialogo(page_):
        """Função para fechar qualquer diálogo aberto."""
        page_.dialog.open = False
        page_.update()

    def voltar_menu(e):
        """Volta para o menu principal passando o usuário logado."""
        from menu_principal import mostrar_menu
        mostrar_menu(page, usuario_logado)

    # =========================================================================
    #                        Constrói a lista de usuários
    # =========================================================================

    # Campo para filtrar usuários
    filtro_input = ft.TextField(
        hint_text="Filtrar por nome de usuário",
        width=300,
        on_submit=lambda e: recarregar_lista_usuarios(filtro_input.value),
    )

    def recarregar_lista_usuarios(filtro=None):
        """Recarrega a tela com base no filtro de pesquisa."""
        gerenciar_usuarios_filtrado(page, usuario_logado, filtro)

    def gerenciar_usuarios_filtrado(page_, usuario_, filtro):
        # Recarrega o layout inteiro (tratando como "sub-função" para passar o filtro)
        usuarios_ = carregar_usuarios(filtro_nome=filtro)

        usuarios_containers = []
        for u in usuarios_:
            usuario_id = u[0]
            nome_user = u[1]
            data_exp = u[2]
            is_admin = u[3]
            serial_ = u[4]

            status_licenca = verificar_status_licenca(data_exp)
            admin_text = "Sim" if is_admin else "Não"
            serial_texto = serial_ if serial_ else "Nenhum"

            # Linha com as informações do usuário
            info_text = ft.Text(
                f"ID: {usuario_id} | Usuário: {nome_user} | Licença: {status_licenca} | Admin: {admin_text}",
                tooltip=f"Serial: {serial_texto}",
                size=16,
                color=ft.colors.BLACK54
            )

            # Botões de ação
            editar_btn = ft.IconButton(
                icon=ft.icons.EDIT,
                tooltip="Editar Usuário",
                icon_color=ft.colors.BLUE,
                on_click=lambda e, uid=usuario_id: editar_usuario(e, uid)
            )
            mudar_senha_btn = ft.IconButton(
                icon=ft.icons.LOCK,
                tooltip="Modificar Senha",
                icon_color=ft.colors.PURPLE,
                on_click=lambda e, uid=usuario_id: modificar_senha(e, uid)
            )
            deletar_btn = ft.IconButton(
                icon=ft.icons.DELETE,
                tooltip="Deletar Usuário",
                icon_color=ft.colors.RED,
                on_click=lambda e, uid=usuario_id: deletar_usuario(uid)
            )
            gerar_serial_btn = ft.IconButton(
                icon=ft.icons.KEY,
                tooltip="Gerar Serial e Ativar",
                icon_color=ft.colors.GREEN,
                on_click=lambda e, uid=usuario_id, uname=nome_user: gerar_e_ativar_serial(uid, uname)
            )

            row_acoes = ft.Row(
                controls=[info_text, editar_btn, mudar_senha_btn, gerar_serial_btn, deletar_btn],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                wrap=True
            )

            # "Cartão" do usuário
            usuario_card = ft.Container(
                content=row_acoes,
                padding=ft.Padding(10, 10, 10, 10),
                margin=ft.margin.symmetric(vertical=5),
                bgcolor=ft.colors.BLUE_GREY_50,
                border_radius=10,
            )
            usuarios_containers.append(usuario_card)

        usuarios_lista = ft.Column(
            controls=usuarios_containers,
            spacing=5,
            scroll=ft.ScrollMode.AUTO
        )

        # Reconstrói layout principal
        page_.clean()
        page_.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Gerenciamento de Usuários",
                            size=24,
                            weight="bold",
                            color=ft.colors.BLUE_GREY_900
                        ),
                        ft.Row(
                            controls=[
                                filtro_input,
                                ft.ElevatedButton(
                                    "Filtrar",
                                    icon=ft.icons.SEARCH,
                                    on_click=lambda _: recarregar_lista_usuarios(filtro_input.value),
                                    bgcolor=ft.colors.BLUE_GREY_700,
                                    color=ft.colors.WHITE
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        ft.Divider(color=ft.colors.BLUE_GREY_300),
                        usuarios_lista,
                        ft.Divider(),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Adicionar Usuário",
                                    icon=ft.icons.PERSON_ADD,
                                    bgcolor=ft.colors.BLUE_GREY_700,
                                    color=ft.colors.WHITE,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=20),
                                        padding=ft.padding.symmetric(horizontal=20, vertical=15)
                                    ),
                                    on_click=adicionar_usuario
                                ),
                                ft.ElevatedButton(
                                    "Voltar",
                                    icon=ft.icons.ARROW_BACK,
                                    bgcolor=ft.colors.BLUE_GREY_700,
                                    color=ft.colors.WHITE,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=20),
                                        padding=ft.padding.symmetric(horizontal=20, vertical=15)
                                    ),
                                    on_click=voltar_menu
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                padding=30,
                border_radius=20,
                shadow=ft.BoxShadow(
                    spread_radius=2,
                    blur_radius=15,
                    color=ft.colors.BLACK26,
                    offset=ft.Offset(2, 2),
                ),
                bgcolor=ft.colors.WHITE,
                width=900  # Ajuste conforme desejar
            )
        )
        page_.update()

    # Carrega a lista inicialmente (sem filtro)
    gerenciar_usuarios_filtrado(page, usuario_logado, filtro=None)
