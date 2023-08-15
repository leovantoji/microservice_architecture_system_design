import requests
from config import settings


def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    basic_auth = (auth.username, auth.password)
    response = requests.post(
        url=f"https://{settings.auth_app_name}:{settings.port_auth}/login",
        auth=basic_auth,
        timeout=30,
    )

    if response.status_code == 200:
        return response.txt, None

    return None, (response.txt, response.status_code)
