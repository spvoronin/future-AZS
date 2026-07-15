import cv2
import easyocr
import psycopg2
import requests
from PIL import Image
import io
import numpy as np

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
                    cursor.execute('insert into images(image_data, cam_id) values (%s, %s)', (psycopg2.Binary(response.content), id_cam))
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
                cursor.execute('select image_id, image_data from images where cam_id=%s order by image_id desc', (id_cam,))
                res = cursor.fetchone()
                data = res[1]
                image_id = res[0]

                nparr = np.frombuffer(data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                gr = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                num = self.num_cas.detectMultiScale(gr, scaleFactor=1.1, minNeighbors=5)

                for x, y, w, h in num:
                    # Рисуем синюю рамку на оригинальной картинке вокруг найденного номера
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

                    # Вырезаем область номера (ROI).
                    # Вырезаем из ЦВЕТНОЙ оригинальной картинки, так как EasyOCR лучше распознает цвета.
                    roi_plate = img[y:y + h, x:x + w]
                    roi_plate = cv2.resize(roi_plate, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
                    # Отправляем вырезанный кусочек номера в EasyOCR
                    result = self.reader.readtext(roi_plate)
                    if not result:
                        continue
                    # EasyOCR возвращает список. Для каждого найденного слова он выдает:
                    # [координаты_границ, сам_текст, уверенность_в_распознавании]
                    # Очищаем полученный текст от случайных пробелов
                    car_number = "".join(result[0][1].split())
                    cursor.execute('insert into number_of_car(image_id, number_car) values (%s, %s)', (image_id, car_number))
                    return car_number.upper()
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()
                print('info: коннект закрыт')