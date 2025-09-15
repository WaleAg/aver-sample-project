import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
DEMO_TOKEN = os.getenv("DEMO_BEARER_TOKEN", "mysecrettoken")

def verify_bearer(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    if token != DEMO_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token
