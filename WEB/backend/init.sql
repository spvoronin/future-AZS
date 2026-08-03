create table region
(
    -- Уникальный айди региона
    id SERIAL PRIMARY KEY,

    -- Название региона
    region_name TEXT NOT NULL
);

create table station
(
    -- Уникальный id АЗС
    id SERIAL PRIMARY KEY,

    -- Адрес АЗС
    address TEXT NOT NULL,

    -- Рейтинг АЗС
    rating INT NOT NULL,

    -- Айди
    region_id INT,

    -- Внешний ключ на таблицу с регионами
    CONSTRAINT fk_region_id
        FOREIGN KEY(region_id)
        REFERENCES region(id)
        ON DELETE SET NULL
);

create table users
(
    -- Уникальный id пользователя
    id SERIAL PRIMARY KEY,

    -- Номер телефона
    phone VARCHAR(20) NOT NULL UNIQUE,

    -- Почта для чеков и уведомлений
    email VARCHAR(100) NOT NULL UNIQUE,

    -- Хэш пароля
    password_hash VARCHAR(255) NOT NULL,

    -- Имя клиента
    first_name VARCHAR(50) NOT NULL,

    -- Время пинга
    time_ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Номер автомобиля пользователя
    number_of_car VARCHAR(20) NOT NULL,

    -- Статус администратора
    is_admin BOOLEAN DEFAULT False
);

create table pumps
(
    -- Уникальный id колонки
    id SERIAL PRIMARY KEY,

    -- Айди АЗС
    station_id INT NOT NULL,

    -- Номер колонки на заправке
    pump_number INT NOT NULL,

    -- Статус колонки idle(свободна), dispensing(налив), error(сбой)
    status VARCHAR(20) DEFAULT 'idle',

    -- Доступна ли колонка
    is_active BOOLEAN NOT NULL,

    -- Не может быть двух пар станция-номер_колонки
    CONSTRAINT unique_pump_per_station
        UNIQUE (station_id, pump_number),

    -- Внешний ключ на таблицу с АЗС
    CONSTRAINT fk_station_id_PU
        FOREIGN KEY (station_id)
        REFERENCES station(id)
        ON DELETE CASCADE
);

create table tanks
(
    -- уникальный id резервуара(одного раздела)
    id SERIAL PRIMARY KEY,

    -- айди АЗС
    station_id INT NOT NULL,

    -- номер резервуара
    tank_number INT NOT NULL,

    -- номер раздела в резервуаре
    compartment_number INT NOT NULL,

     -- вид топлива
    fuel_type VARCHAR(20) NOT NULL,

    -- объём раздела резервуара
    max_capacity REAL NOT NULL,

    -- настоящий объём в процентах
    current_liters REAL NOT NULL,

    -- температура раздела
    temperature REAL NOT NULL,

    -- время пинга
    time_ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Уникальный набор (id станции, номера резервуара, номера раздела)
    CONSTRAINT unique_compartment
        UNIQUE (station_id, tank_number, compartment_number),

    -- Внешний ключ на таблицу с АЗС
    CONSTRAINT fk_station_id_TA
        FOREIGN KEY (station_id)
        REFERENCES station(id)
        ON DELETE CASCADE
);

create table prices
(
    -- Айди региона
    region_id INT NOT NULL,

    -- Тип топлива
    fuel_type VARCHAR(20) NOT NULL,

     -- Цена
    price_per_liter REAL NOT NULL,

    -- Время пинга
    time_ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Все пары айди_региона-тип_топлива уникальны
    PRIMARY KEY (region_id, fuel_type),

    -- Внешний ключ на таблицу с регионами
    CONSTRAINT fk_region_PR
        FOREIGN KEY(region_id)
        REFERENCES region(id)
        ON DELETE CASCADE
);

create table transactions
(
    -- Уникальный id транзакции
    id SERIAL PRIMARY KEY,

    -- Номер колонки
    pump_id INT NOT NULL,

    -- Тип топлива
    fuel_type VARCHAR(20) NOT NULL,

    -- Сколько литров заказано
    requested_liters REAL NOT NULL,

    -- Статус транзакции pending(ожидание оплаты), progress(налив), completed(завершено)
    status VARCHAR(20) DEFAULT 'pending',

    -- Время пинга
    time_ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- id пользователя
    user_id INT NOT NULL,

    -- Внешний ключ на таблицу с ТРК
    CONSTRAINT fk_pump_id
        FOREIGN KEY(pump_id)
        REFERENCES pumps(id)
        ON DELETE CASCADE,

    -- Внешний ключ на таблицу пользователей
    CONSTRAINT fk_user_id_TR
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

create table loyalty_cards
(
    -- id карты лояльности
    id SERIAL PRIMARY KEY,

    -- id пользователя
    user_id INT NOT NULL,

    -- Номер карты
    card_number VARCHAR(30) NOT NULL UNIQUE,

    -- Баланс карты
    bonus_balance INT DEFAULT 0,

    -- Персональный процент карты
    discount_percent REAL DEFAULT 0.0,

    -- Статус карты (active, blocked)
    status VARCHAR(20) DEFAULT 'active',

    -- Время пинга
    time_ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Внешний ключ на таблицу пользователей
    CONSTRAINT fk_user_id_LC
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

create table uuid
(
    -- Номер(айди устройства)
    id SERIAL PRIMARY KEY,

    -- Уникальный код устройства
    uuid TEXT NOT NULL UNIQUE,

    -- Номер станции устройства
    station_id INT NOT NULL,

    -- Внешний ключ на таблицу с АЗС
    CONSTRAINT fk_station_id_UU
        FOREIGN KEY (station_id)
        REFERENCES station(id)
        ON DELETE CASCADE
);

create table sensors
(
    -- Айди записи
    id SERIAL PRIMARY KEY,

    -- Уникальный айди устройства
    uuid TEXT NOT NULL,

    -- Значение тока с AS712
    electric_current REAL NOT NULL,

    -- Датчик пламени
    flame BOOLEAN NOT NULL,

    -- Показания с MQ-2
    gas INT NOT NULL,

    -- Влажность среды с DHT11
    ambient_humidity REAL NOT NULL,

    -- Температура среды с DHT11
    ambient_temperature REAL NOT NULL,

    -- Температура в цистерне
    tank_temperature REAL NOT NULL,

    -- Уровень воды
    water_level INT NOT NULL,

    -- Датчик напряжения
    voltage REAL NOT NULL,

    -- Время пинга
    time_ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Внешний ключ на таблицу с uuid устройств
    CONSTRAINT fk_uuid
        FOREIGN KEY (uuid)
        REFERENCES uuid(uuid)
        ON DELETE CASCADE
);

create table cam
(
    -- Номер камеры в бд
    cam_id SERIAL PRIMARY KEY,

    -- Уникальный айди камеры
    uuid TEXT NOT NULL UNIQUE
);

create table images
(
    -- айди изображения
    image_id SERIAL PRIMARY KEY,

    -- время записи изображения
    image_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- изображение в байтовом виде
    image_data BYTEA NOT NULL,

    -- уникальный айди камеры
    cam_id INT NOT NULL,

    -- Внешний ключ на таблицу с uuid камер
    CONSTRAINT key_cam_id
        FOREIGN KEY(cam_id)
        REFERENCES cam(cam_id)
        ON DELETE CASCADE
);

create table number_of_car
(
    -- айди номера
    id SERIAL PRIMARY KEY,

    -- айди изображения, где находится этот номер
    image_id INT NOT NULL UNIQUE,

    -- сам номер автомобиля
    number_car VARCHAR(20) NOT NULL UNIQUE,

    -- Внешний ключ на таблицу с изображениями
    CONSTRAINT key_img_id
        FOREIGN KEY(image_id)
        REFERENCES images(image_id)
        ON DELETE CASCADE
);