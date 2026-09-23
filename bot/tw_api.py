import requests

BASE_URL = "https://api.timeweb.ru"
TIMEOUT = 10

def get_token(login, password, app_key):
    response = requests.post(
        f'{BASE_URL}/v1.2/access',
        auth=(login, password),
        headers={"x-app-key": app_key},
        timeout=TIMEOUT, 
    )
    return response.json()["token"]