import os
from pathlib import Path

FILES = {
    "requirements.txt": r"""
flet==0.21.0
httpx==0.27.0
""",

    "api.py": r"""
import httpx

class ProFindAPIClient:
    def __init__(self, base_url: str = "https://profind-backend.onrender.com"):
        self.base_url = base_url.rstrip("/")

    def register(self, username: str, password: str):
        try:
            response = httpx.post(f"{self.base_url}/register", params={"username": username, "password": password}, timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json().get("detail", "Ошибка регистрации")}
        except Exception as e:
            return {"error": f"Ошибка соединения с сервером: {str(e)}"}

    def login(self, username: str, password: str):
        try:
            response = httpx.post(f"{self.base_url}/login", params={"username": username, "password": password}, timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json().get("detail", "Неверный логин или пароль")}
        except Exception as e:
            return {"error": f"Ошибка соединения с сервером: {str(e)}"}

    def send_message(self, sender_id: int, receiver_id: int, text: str):
        try:
            response = httpx.post(
                f"{self.base_url}/messages",
                json={"sender_id": sender_id, "receiver_id": receiver_id, "text": text},
                timeout=10.0
            )
            return response.status_code == 200
        except:
            return False

    def get_messages(self, user_id: int):
        try:
            response = httpx.get(f"{self.base_url}/messages/{user_id}", timeout=10.0)
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
""",

    "main.py": r"""
import flet as ft
from api import ProFindAPIClient

api = ProFindAPIClient()

def main(page: ft.Page):
    page.title = "ProFind Messenger"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 700

    # Глобальное состояние пользователя
    current_user = {"id": None, "username": None}

    # Элементы интерфейса авторизации
    username_input = ft.TextField(label="Имя пользователя", width=280, border_radius=10)
    password_input = ft.TextField(label="Пароль", password=True, can_reveal_password=True, width=280, border_radius=10)
    status_text = ft.Text(value="", color=ft.colors.RED_400)

    # Элементы чата
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    message_input = ft.TextField(label="Введите сообщение...", expand=True, border_radius=10)

    def load_messages():
        chat_list.controls.clear()
        messages = api.get_messages(current_user["id"])
        for msg in messages:
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

    def send_click(e):
        if not message_input.value.strip():
            return
        # Для теста отправляем сообщение сами себе или в общий поток
        success = api.send_message(
            sender_id=current_user["id"],
            receiver_id=current_user["id"], 
            text=message_input.value
        )
        if success:
            message_input.value = ""
            load_messages()

    def show_chat_screen():
        page.clean()
        page.add(
            ft.AppBar(
                title=ft.Text(f"Профиль: {current_user['username']}"),
                bgcolor=ft.colors.SURFACE_VARIANT
            ),
            ft.Container(content=chat_list, expand=True, padding=10),
            ft.Row(
                [
                    message_input,
                    ft.IconButton(icon=ft.icons.SEND, on_click=send_click, icon_color=ft.colors.BLUE_400)
                ],
                padding=10
            )
        )
        load_messages()

    def handle_login(e):
        res = api.login(username_input.value, password_input.value)
        if "error" in res:
            status_text.value = res["error"]
            page.update()
        else:
            current_user["id"] = res["id"]
            current_user["username"] = res["username"]
            show_chat_screen()

    def handle_register(e):
        res = api.register(username_input.value, password_input.value)
        if "error" in res:
            status_text.value = res["error"]
            page.update()
        else:
            status_text.value = "Успешно! Теперь войдите."
            status_text.color = ft.colors.GREEN_400
            page.update()

    # Экран авторизации
    page.add(
        ft.Column(
            [
                ft.Text("ProFind Messenger", size=24, weight=ft.FontWeight.BOLD),
                ft.VerticalSpace(20) if hasattr(ft, "VerticalSpace") else ft.Container(height=20),
                username_input,
                password_input,
                status_text,
                ft.Row(
                    [
                        ft.ElevatedButton("Войти", on_click=handle_login, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE),
                        ft.OutlinedButton("Регистрация", on_click=handle_register)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
              horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
"""
}

def generate_client():
    print("🚀 Генерирую файлы клиента ProFind Messenger...")
    for filename, content in FILES.items():
        path = Path(filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"✅ Создан файл: {filename}")
    print("\n🎉 Готово! Установи зависимости и запускай.")

if __name__ == "__main__":
    generate_client()