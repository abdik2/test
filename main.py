import flet as ft
import httpx
import threading

API_URL = "https://profind-backend.onrender.com"

def main(page: ft.Page):
    page.title = "ProFind Messenger"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 700

    current_user = {"id": None, "username": None}

    # Индикатор статуса сервера
    server_status_badge = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=12, height=12, stroke_width=2),
            ft.Text("Проверяем сервер...", size=12, color=ft.colors.YELLOW_400)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        padding=8,
        bgcolor=ft.colors.GREY_900,
        border_radius=8,
        width=300
    )

    username_input = ft.TextField(label="Имя пользователя", width=280, border_radius=10)
    password_input = ft.TextField(label="Пароль", password=True, can_reveal_password=True, width=280, border_radius=10)
    status_text = ft.Text(value="", color=ft.colors.RED_400)

    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    message_input = ft.TextField(label="Введите сообщение...", expand=True, border_radius=10)

    def check_server():
        try:
            res = httpx.get(f"{API_URL}/health", timeout=15.0)
            if res.status_code == 200:
                server_status_badge.content = ft.Row([
                    ft.Container(width=10, height=10, border_radius=5, bgcolor=ft.colors.GREEN_400),
                    ft.Text("Сервер Онлайн", size=12, color=ft.colors.GREEN_400)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8)
            else:
                raise Exception()
        except:
            server_status_badge.content = ft.Row([
                ft.Container(width=10, height=10, border_radius=5, bgcolor=ft.colors.RED_400),
                ft.Text("Сервер спит или недоступен", size=12, color=ft.colors.RED_400)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8)
        page.update()

    threading.Thread(target=check_server, daemon=True).start()

    def load_messages():
        chat_list.controls.clear()
        try:
            res = httpx.get(f"{API_URL}/messages/{current_user['id']}", timeout=5.0)
            if res.status_code == 200:
                for msg in res.json():
                    is_me = msg["sender_id"] == current_user["id"]
                    align = ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START
                    bg_color = ft.colors.BLUE_900 if is_me else ft.colors.GREY_800
                    
                    chat_list.controls.append(
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(msg["text"], color=ft.colors.WHITE),
                                    padding=10,
                                    border_radius=10,
                                    bgcolor=bg_color,
                                    max_width=250
                                )
                            ],
                            alignment=align
                        )
                    )
                page.update()
        except Exception as e:
            print("Ошибка загрузки сообщений:", e)

    def send_click(e):
        if not message_input.value.strip():
            return
        try:
            res = httpx.post(
                f"{API_URL}/messages",
                json={"sender_id": current_user["id"], "receiver_id": current_user["id"], "text": message_input.value},
                timeout=5.0
            )
            if res.status_code == 200:
                message_input.value = ""
                load_messages()
        except Exception as e:
            print("Ошибка отправки:", e)

    def show_chat():
        page.clean()
        # Исправлено: AppBar задается через page.appbar, а не через page.add
        page.appbar = ft.AppBar(
            title=ft.Text(f"Чат: {current_user['username']}"),
            bgcolor=ft.colors.SURFACE_VARIANT
        )
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.add(
            ft.Column([
                ft.Container(content=chat_list, expand=True, padding=10),
                ft.Row([
                    message_input,
                    ft.IconButton(icon=ft.icons.SEND, on_click=send_click, icon_color=ft.colors.BLUE_400)
                ], padding=10)
            ], expand=True)
        )
        load_messages()

    def handle_login(e):
        try:
            res = httpx.post(f"{API_URL}/login", params={"username": username_input.value, "password": password_input.value}, timeout=5.0)
            if res.status_code == 200:
                data = res.json()
                current_user["id"] = data["id"]
                current_user["username"] = data["username"]
                show_chat()
            else:
                status_text.value = res.json().get("detail", "Ошибка входа")
                page.update()
        except Exception as ex:
            status_text.value = "Нет связи с сервером"
            page.update()

    def handle_register(e):
        try:
            res = httpx.post(f"{API_URL}/register", params={"username": username_input.value, "password": password_input.value}, timeout=5.0)
            if res.status_code == 200:
                status_text.value = "Успешно! Теперь войдите."
                status_text.color = ft.colors.GREEN_400
                page.update()
            else:
                status_text.value = res.json().get("detail", "Ошибка регистрации")
                page.update()
        except Exception as ex:
            status_text.value = "Нет связи с сервером"
            page.update()

    page.add(
        ft.Column([
            ft.Text("ProFind Messenger", size=24, weight=ft.FontWeight.BOLD),
            server_status_badge,
            ft.Container(height=10),
            username_input,
            password_input,
            status_text,
            ft.Row([
                ft.ElevatedButton("Войти", on_click=handle_login, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE),
                ft.OutlinedButton("Регистрация", on_click=handle_register)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.app(target=main)