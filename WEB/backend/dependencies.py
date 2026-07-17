from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# Импортируй свой SECRET_KEY, который использовал при генерации токена
SECRET_KEY = os.getenv("SECRET_KEY")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # вернет словарь, например: {"sub": "user@mail.ru", "role": "simple"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Время сессии истекло. Войдите заново."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или поврежденный токен доступа"
        )


# 2. Проверяем, является ли пользователь админом (подходит для помпы)
def verify_admin(current_user: dict = Depends(get_current_user)):
    user_role = current_user.get("role")

    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # 403 — Доступ запрещен
            detail="У вас нет прав администратора для управления этим устройством"
        )
    return current_user