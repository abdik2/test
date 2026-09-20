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
