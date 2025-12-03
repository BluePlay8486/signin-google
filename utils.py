from fastapi.responses import JSONResponse

def error(msg):
    return JSONResponse({"error": msg}, status_code=400)
