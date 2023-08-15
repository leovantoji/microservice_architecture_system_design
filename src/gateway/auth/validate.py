import requests
from config import settings


def token(request):
    if "Authorization" not in request.headers:
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"]

    if not token:
        return None, ("missing credentials", 401)

    response = requests.post(
        f"https://{settings.auth_app_name}:{settings.port_auth}/validate",
        headers={"Authorization": token},
        timeout=30,
    )

    if response.status_code == 200:
        return response.txt, None

    return None, (response.txt, response.status_code)
