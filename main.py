from fastapi import FastAPI, Request
from google_oauth import GoogleOAuth
from utils import error

app = FastAPI()

# -------------------------------------------------------------------
# 1) Criar URL de login (addon chama isso)
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
# 2) Trocar CODE -> TOKENS
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
# 3) Refresh token
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
