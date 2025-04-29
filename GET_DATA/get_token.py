import requests
import json
import time
import os

# 🔹 Forge API Credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# 🔹 Forge API Credentials

AUTH_ENDPOINT = "https://developer.api.autodesk.com/authentication/v2/token"
CURRENT_DIR = os.path.dirname(__file__)
TOKEN_FILE = os.path.join(CURRENT_DIR, "token.json")

def get_access_token():
    """Получает новый токен и сохраняет его в файл."""
    print("🔹 Запрос нового access token...")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "data:read data:write data:create data:search bucket:read bucket:create account:read",
    }
    
    response = requests.post(AUTH_ENDPOINT, headers=headers, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        token_data["expires_at"] = time.time() + token_data["expires_in"] - 60  # Немного раньше, чтобы избежать проблем
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=4)
        print("✅ Новый токен сохранён в token.json")
        return token_data["access_token"]
    else:
        print(f"❌ Ошибка получения токена: {response.status_code}")
        print(response.text)
        return None

def load_token():
    """Загружает сохранённый токен или получает новый, если он устарел."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            token_data = json.load(f)
        
        if time.time() < token_data.get("expires_at", 0):  # Проверяем срок действия
            print("✅ Загружен сохранённый access token")
            return token_data["access_token"]

    # Если токен отсутствует или устарел — получаем новый
    return get_access_token()

if __name__ == "__main__":
    print("🔄 Текущий токен:", load_token())