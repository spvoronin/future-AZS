import cv2
import easyocr

# 1. Инициализируем EasyOCR для распознавания русского и английского текста.
# gpu=False означает, что нейросеть будет работать на процессоре (так надежнее для старта).
# ВНИМАНИЕ: При самом первом запуске EasyOCR автоматически скачает маленькие языковые модели 
# из интернета (около 20-30 МБ). Придется подождать секунд 10-20, дальше всё будет работать мгновенно.
print("Инициализация нейросети EasyOCR... Пожалуйста, подождите...")
reader = easyocr.Reader(['ru', 'en'], gpu=False)

# 2. Загружаем каскад Хаара для поиска автомобильного номера.
# Файл haarcascade_russian_plate_number.xml должен лежать в той же папке, что и этот скрипт!
num_cas = cv2.CascadeClassifier(r'C:\Users\Sergey\Documents\future-AZS\WEB\backend\analiz_num\haarcascade_russian_plate_number.xml')

image_path = r'path'
image = cv2.imread(image_path)

if image is None:
    print(f"Ошибка: Не удалось открыть изображение по пути: {image_path}")
    exit()

# 4. Переводим изображение в оттенки серого (это нужно ТОЛЬКО для работы каскада Хаара)
gr = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 5. Ищем рамку автомобильного номера на фото
num = num_cas.detectMultiScale(gr, scaleFactor=1.1, minNeighbors=5)

print(f"\nНайдено потенциальных зон с номерами: {len(num)}")

# 6. Обрабатываем каждую найденную рамку номера
for x, y, w, h in num:
    # Рисуем синюю рамку на оригинальной картинке вокруг найденного номера
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    
    # Вырезаем область номера (ROI). 
    # Вырезаем из ЦВЕТНОЙ оригинальной картинки, так как EasyOCR лучше распознает цвета.
    roi_plate = image[y:y+h, x:x+w]
    
    try:
        # Отправляем вырезанный кусочек номера в EasyOCR
        result = reader.readtext(roi_plate)
        
        # EasyOCR возвращает список. Для каждого найденного слова он выдает:
        # [координаты_границ, сам_текст, уверенность_в_распознавании]
        for (bbox, text, prob) in result:
            # Очищаем полученный текст от случайных пробелов
            car_number = "".join(text.split())
            
            # Выводим финальный текст в консоль
            print(f"Текст сохранен в переменную: {car_number} (Уверенность: {round(prob * 100)}%)")
            
            # Дополнительно: пишем распознанный текст прямо над рамкой машины зелёным цветом
            #cv2.putText(image, car_number, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
    except Exception as e:
        print(f"Не удалось распознать символы внутри рамки: {e}")

# 7. Показываем результат работы программы
# Уменьшаем картинку ровно в 2 раза, чтобы она аккуратно влезла в экран любого монитора
img_res = cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))

print("\nВывод изображения на экран. Нажми любую клавишу в окне картинки, чтобы закрыть программу.")
cv2.imshow('Result', img_res)
cv2.waitKey(0)
cv2.destroyAllWindows()