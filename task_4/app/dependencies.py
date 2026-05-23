from fastapi import Header, HTTPException, status, Depends
from app.storage import storage

def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default="user")
):
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="x_user_id header required")
    
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid x_user_id")
    
    return {
        "id": user_id,
        "role": x_user_role,
    }

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin acces required")
    
    return user

def get_storage():
    return storage