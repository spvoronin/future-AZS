import cv2
import easyocr
import psycopg2
import requests
from PIL import Image
import io
import numpy as np
import re

# 1. Инициализируем EasyOCR для распознавания русского и английского текста.
# gpu=False означает, что нейросеть будет работать на процессоре (так надежнее для старта).
# ВНИМАНИЕ: При самом первом запуске EasyOCR автоматически скачает маленькие языковые модели 
# из интернета (около 20-30 МБ). Придется подождать секунд 10-20, дальше всё будет работать мгновенно.
class photo_processing:
    def __init__(self, HOST, NAME_USER, PASSWORD, DATABASE, CONNECT, url, uuid):
        self.host = HOST
        self.name_user = NAME_USER
        self.password = PASSWORD
        self.database = DATABASE
        self.connect = CONNECT
        self.url = url
        self.uuid = uuid

        self.reader = easyocr.Reader(['ru', 'en'], gpu=False)
        self.num_cas = cv2.CascadeClassifier(r'haarcascade_russian_plate_number.xml')

    def save_photo(self):
        connection = psycopg2.connect(host=self.host, user=self.name_user, password=self.password,
                                      database=self.database)
        connection.autocommit = True
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                with connection.cursor() as cursor:
                    cursor.execute('select cam_id from cam where uuid=%s', (self.uuid,))
                    fet = cursor.fetchone()
                    id_cam = fet[0] if fet else 0
                    if id_cam == 0:
                        cursor.execute('insert into cam(uuid) values (%s) returning cam_id', (self.uuid,))
                        id_cam = cursor.fetchone()[0]
                    cursor.execute('insert into images(image_data, cam_id) values (%s, %s)',
                                   (psycopg2.Binary(response.content), id_cam))
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()
                print('info: коннект закрыт')

    def analiz_num(self):
        connection = psycopg2.connect(host=self.host, user=self.name_user, password=self.password,
                                      database=self.database)
        connection.autocommit = True

        try:
            with connection.cursor() as cursor:
                cursor.execute('select cam_id from cam where uuid=%s', (self.uuid,))
                id_cam = cursor.fetchone()[0]
                cursor.execute('select image_id, image_data from images where cam_id=%s order by image_id desc limit 1',
                               (id_cam,))
                res = cursor.fetchone()
                data = res[1]
                image_id = res[0]
                byte_data = bytes(data)
                nparr = np.frombuffer(byte_data, np.uint8)

                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (0, 0), fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
                gray = cv2.convertScaleAbs(gray, alpha=1.3, beta=10)

                result = self.reader.readtext(gray)
                print(f"DEBUG: Сырой результат со всей картинки: {result}")

                if not result:
                    return "ФОРМАТ_НЕ_РАСПОЗНАН"

                all_text = "".join([block[1] for block in result]).upper().replace(" ", "")
                clean_text = re.sub(r'[^A-ZА-Я0-9]', '', all_text)
                print(f"DEBUG: Сырой текст после очистки: '{clean_text}'")

                translit_map = {
                    'A': 'А', 'B': 'В', 'E': 'Е', 'K': 'К', 'M': 'М',
                    'H': 'Н', 'O': 'О', 'P': 'Р', 'C': 'С', 'T': 'Т',
                    'Y': 'У', 'X': 'Х', 'Z': '2'
                }
                normalized_text = "".join([translit_map.get(char, char) for char in clean_text])
                print(f"DEBUG: Текст после нормализации: '{normalized_text}'")

                # --- УМНОЕ ИСПРАВЛЕНИЕ ОШИБОК О/0 ПО ПОЗИЦИЯМ ГОСТА ---
                # Если длина текста подходит под стандартный номер (например, 8-9 символов: буква+3 цифры+2 буквы+регион)
                # Структура: [Буква] [3 символа] [2 Буквы] [Регион (2-3 цифры)]

                fixed_text = normalized_text

                # Попробуем выделить структуру с помощью регулярного выражения с группами,
                # чтобы точечно исправить нули на О и наоборот.
                # Шаблон захватывает: (1 буква)(3 знака)(2 буквы)(регион)
                match_struct = re.match(r'^([A-ZА-Я0-9])([A-ZА-Я0-9]{3})([A-ZА-Я0-9]{2})(\d{2,3})$', fixed_text)

                if match_struct:
                    p1, p2, p3, region = match_struct.groups()

                    # 1. Первая позиция ВСЕГДА буква: если там цифра (например, '0'), меняем на 'О'
                    if p1 in '0123456789':
                        p1 = 'О'  # Самая частая ошибка для О007ОО

                    # 2. Вторая часть (3 символа) — это цифры. Если там пролезли буквы 'О', меняем их на '0'
                    p2 = p2.replace('О', '0')

                    # 3. Третья часть (2 символа) — это буквы. Если там нули '0', меняем их на 'О'
                    p3 = p3.replace('0', 'О')

                    fixed_text = f"{p1}{p2}{p3}{region}"
                    print(f"DEBUG: Текст после структурного исправления О/0: '{fixed_text}'")

                # Финальный паттерн для проверки ГОСТа
                pattern = r'[А-ВЕКМНОРСТУХ]\d{3}[А-ВЕКМНОРСТУХ]{2}\d{2,3}'
                match = re.search(pattern, fixed_text)

                if match:
                    valid_number = match.group(0)
                    print(f"DEBUG: Успешно найден номер: {valid_number}")
                    cursor.execute(
                        'insert into number_of_car(image_id, number_car) values (%s, %s) ON CONFLICT (number_car) do update set image_id = EXCLUDED.image_id',
                        (image_id, valid_number)
                    )
                    return valid_number.upper()

                return "404_BAD_REQUEST"
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()
                print('info: коннект закрыт')