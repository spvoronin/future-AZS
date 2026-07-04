from fastapi import APIRouter
import psycopg2
import os
from dotenv import load_dotenv
from schemas.schem import UserCreate, UserLogin

load_dotenv()

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
CONNECT = os.getenv("CONNECT")

router_users = APIRouter(
    prefix="/users",
    tags=["Всё, что связано с пользователями"]
)


@router_users.get("")
async def get_all_users():
    try:
        data_res = []
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('select id, phone, email, first_name, number_of_car from users order by id desc')
            data_all_users = cursor.fetchall()
        for records in data_all_users:
            data_res.append({"id": records[0], "phone": records[1], "email": records[2], "first_name": records[3],
                             "number_of_car": records[4]})
        return data_res
    except Exception as e:
        print(f'info: ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


@router_users.get("/{user_id}")
async def get_one_user(user_id: int):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('select id, phone, email, first_name, number_of_car from users where id=%s', (str(user_id),))
            data_one_user = cursor.fetchone()
            if data_one_user is None:
                return {"status": "error", "message": "Пользователь не найден"}
        data_res = {"id": data_one_user[0], "phone": data_one_user[1], "email": data_one_user[2],
                    "first_name": data_one_user[3], "number_of_car": data_one_user[4]}
        return data_res
    except Exception as e:
        print(f'info: ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


@router_users.post("/register")
async def add_new_user(data_about_new_user: UserCreate):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                'insert into users(phone, email, password_hash, first_name, number_of_car) values (%s, %s, %s, %s, %s)',
                (data_about_new_user.phone, data_about_new_user.email, data_about_new_user.password_hash,
                 data_about_new_user.first_name, data_about_new_user.number_of_car))
            cursor.execute('select id from users order by id desc')
            new_id = cursor.fetchone()[0]
        return {"status": "ok", "code": 201, "new_id": new_id, "phone": data_about_new_user.phone,
                "email": data_about_new_user.email, "first_name": data_about_new_user.first_name,
                "number_of_car": data_about_new_user.number_of_car}
    except Exception as e:
        print(f'info: ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


@router_users.put("/{user_is}")
async def update_data_about_user(user_is: int = 0, phone: str | None = None, email: str | None = None,
                                 first_name: str | None = None, number_of_car: str | None = None):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            if phone:
                cursor.execute("update users set phone=%s where id=%s", (phone, str(user_is)))
            if email:
                cursor.execute("update users set email=%s where id=%s", (email, str(user_is)))
            if first_name:
                cursor.execute("update users set first_name=%s where id=%s", (first_name, str(user_is)))
            if number_of_car:
                cursor.execute("update users set number_of_car=%s where id=%s", (number_of_car, str(user_is)))
        return {"status": "ok", "code": 204}
    except Exception as e:
        print(f'info: ошибка {e}')
        return {"status": "error", "message": "Не удалось обновить данные пользователя"}
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


@router_users.post("/login")
async def login_user(data_for_login: UserLogin):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('select phone, first_name, number_of_car from users where email = %s and password_hash = %s',
                           (data_for_login.email, data_for_login.password_hash))
            ans = cursor.fetchone()
            data_about_user = ans if ans else None
        if (data_about_user):
            return {'phone': data_about_user[0], 'first_name': data_about_user[1], 'number_of_car' : data_about_user[
                2], 'email' : data_for_login.email}
        else:
            return {'message' : 'Unauthorized', 'code' : 401}
    except Exception as e:
        print(f'info: ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')
