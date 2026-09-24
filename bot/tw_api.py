import requests

BASE_URL = "https://api.timeweb.ru"
TIMEOUT = 10


def get_token(login, password, app_key):
    response = requests.post(
        f"{BASE_URL}/v1.2/access",
        auth=(login, password),
        headers={"x-app-key": app_key},
        timeout=TIMEOUT,
    )
    return response.json()["token"]

def _get(path, app_key, token):
         response = requests.get(
             f"{BASE_URL}{path}",
             headers={"x-app-key": app_key, "Authorization": f"Bearer {token}"},
             timeout=TIMEOUT,
         )
         return response.json()

def get_balance(login, app_key, token):
    return _get(f'/v1.1/finances/accounts/{login}', app_key, token)


def get_sites(login, app_key, token):
    return _get(f'/v1.1/sites/{login}', app_key, token)
   

def get_domains(login, app_key, token):
    return _get(f'/v1/accounts/{login}/domains', app_key, token)
