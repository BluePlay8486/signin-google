from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google_oauth import GoogleOAuth
from utils import error

app = FastAPI()


# -------------------------------------------------------------------
# 0) Rota obrigatória — CloudDrive sempre chama esta primeiro
# -------------------------------------------------------------------
@app.get("/ip")
async def get_ip(request: Request):
    client_ip = request.client.host
    return {"ip": client_ip}


# -------------------------------------------------------------------
# 1) Rota EXIGIDA pelo CloudDrive (essa é a que faltava!)
# -------------------------------------------------------------------
@app.get("/pin")
async def pin(client_id: str, redirect_uri: str):
    """
    CloudDrive chama isso para obter o link de autorização.
    """
    url = GoogleOAuth.build_auth_url(client_id, redirect_uri)

    # CloudDrive espera SEMPRE ESSES CAMPOS:
    return {
        "pin": "",             # CloudDrive não usa PIN real
        "password": "",        # idem
        "verification_url": url
    }


# -------------------------------------------------------------------
# 2) Alternativa opcional (pode manter se quiser compatibilidade)
# -------------------------------------------------------------------
@app.get("/create_pin")
async def create_pin(client_id: str, redirect_uri: str):
    url = GoogleOAuth.build_auth_url(client_id, redirect_uri)

    return {
        "pin": "",
        "password": "",
        "verification_url": url
    }


# -------------------------------------------------------------------
# 3) Trocar CODE → TOKENS (chamado após login Google)
# -------------------------------------------------------------------
@app.post("/token")
async def get_tokens(request: Request):

    data = await request.json()

    required = ["client_id", "client_secret", "redirect_uri", "code"]
    for field in required:
        if field not in data:
            return error(f"Missing field: {field}")

    tokens = GoogleOAuth.exchange_code_for_tokens(
        data["client_id"],
        data["client_secret"],
        data["redirect_uri"],
        data["code"]
    )

    return tokens


# -------------------------------------------------------------------
# 4) Refresh Token
# -------------------------------------------------------------------
@app.post("/refresh")
async def refresh_tokens(request: Request):

    data = await request.json()
    required = ["client_id", "client_secret", "refresh_token"]

    for field in required:
        if field not in data:
            return error(f"Missing field: {field}")

    new_tokens = GoogleOAuth.refresh_token(
        data["client_id"],
        data["client_secret"],
        data["refresh_token"]
    )

    return new_tokens
