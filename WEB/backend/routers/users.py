from fastapi import APIRouter, HTTPException, status as http_status, Depends
import os
from dotenv import load_dotenv
from schemas.schem import UserCreate, UserLogin
from database import get_db_pool
import asyncpg
import jwt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

router_users = APIRouter(
    prefix="/users",
    tags=["Всё, что связано с пользователями"]
)


@router_users.get("")
async def get_all_users(pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = '''SELECT
                        id,
                        phone,
                        email,
                        first_name,
                        number_of_car
                FROM users
                ORDER BY id DESC'''
        rows = await connection.fetch(query)
        return [dict(row) for row in rows]


@router_users.get("/{user_id}")
async def get_one_user(user_id: int,
                       pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = '''SELECT
                        id,
                        phone,
                        email,
                        first_name,
                        number_of_car
                   FROM users
                   WHERE id=$1'''
        user = await connection.fetchrow(query, user_id)

        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        return dict(user)


@router_users.post("/register", status_code=http_status.HTTP_201_CREATED)
async def add_new_user(data_about_new_user: UserCreate,
                       pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = '''INSERT INTO users(phone, email, password_hash, first_name, number_of_car)
                   VALUES ($1, $2, $3, $4, $5)
                   RETURNING id'''
        new_id = await connection.fetchval(
            query,
            data_about_new_user.phone,
            data_about_new_user.email,
            data_about_new_user.password_hash,
            data_about_new_user.first_name,
            data_about_new_user.number_of_car
        )
        return {
            "status": "ok",
            "code": 201,
            "new_id": new_id,
            "phone": data_about_new_user.phone,
            "email": data_about_new_user.email,
            "first_name": data_about_new_user.first_name,
            "number_of_car": data_about_new_user.number_of_car
        }


@router_users.put("/{user_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def update_data_about_user(user_id: int,
                                 phone: str | None = None,
                                 email: str | None = None,
                                 first_name: str | None = None,
                                 number_of_car: str | None = None,
                                 pool: asyncpg.Pool = Depends(get_db_pool)):
    fields = []
    values = []
    idx = 1

    update_data = {
        "phone": phone,
        "email": email,
        "first_name": first_name,
        "number_of_car": number_of_car
    }

    for key, val in update_data.items():
        if val is not None:
            fields.append(f"{key} = ${idx}")
            values.append(val)
            idx += 1

    async with pool.acquire() as connection:
        query = '''SELECT
                        id
                   FROM users
                   WHERE id=$1'''
        res = await connection.fetchval(query, user_id)

        if not res:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        if not fields:
            return None

        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ${idx}"
        await connection.execute(query, *values, user_id)

        return None


@router_users.post("/login")
async def login_user(data_for_login: UserLogin,
                     pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = '''SELECT
                        phone,
                        first_name,
                        number_of_car,
                        is_admin
                   FROM users
                   WHERE email = $1 and password_hash = $2'''

        user = await connection.fetchrow(
            query,
            data_for_login.email,
            data_for_login.password_hash
        )

        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        user_role = "admin" if user["is_admin"] else "simple"
        payload = {"sub": data_for_login.email, "role": user_role}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return {
            'token': token,
            'role': user_role,
            'phone': user["phone"],
            'first_name': user["first_name"],
            'number_of_car': user["number_of_car"],
            'email': data_for_login.email
        }
