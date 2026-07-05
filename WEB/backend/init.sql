create table region
(
id serial primary key, -- уникальный айди региона
region_name text -- название региона
);

create table station
(
id serial primary key, -- уникальный id АЗС
adress text not null, -- адрес АЗС
rating int not null, -- рейтинг АЗС
region_id int, -- айди
CONSTRAINT fk_region_id FOREIGN KEY(region_id) REFERENCES region(id) on delete cascade
);

create table users
(
id serial primary key,
phone varchar(20) not null unique, -- Номер телефона
email varchar(100) unique, -- Почта для чеков и уведомлений
password_hash varchar(255) not null, -- Хэш пароля
first_name varchar(50), -- Имя клиента created_at
time timestamp default current_timestamp, -- время пинга
number_of_car varchar(20) not null
);

create table pumps
(
id serial primary key, -- уникальный id колонки
station_id int not null, -- айди АЗС
pump_number int not null, -- номер колонки на заправке
status varchar(20) DEFAULT 'idle', -- статус колонки idle(свободна), dispensing(налив), error(сбой)
is_active boolean, -- доступна ли колонка
CONSTRAINT unique_pump_per_station UNIQUE (station_id, pump_number), -- не может быть двух пар станция-номер_колонки
constraint fk_station_id_PU foreign key (station_id) references station(id) on delete cascade
);

create table tanks
(
id serial primary key, -- уникальный id резервуара(одного раздела)
station_id int not null, -- айди АЗС
tank_number int not null, -- номер резервуара
compartment_number int not null, -- номер раздела в резервуаре
fuel_type varchar(20) not null, -- вид топлива
max_capacity real not null, -- объём раздела резервуара
current_liters int not null, -- настоящий объём в процентах
temperature real not null, -- температура раздела
time timestamp default current_timestamp, -- время пинга
CONSTRAINT unique_compartment UNIQUE (station_id, tank_number, compartment_number), -- уникальный набор id станции, номера резервуара, номера раздела
constraint fk_station_id_TA foreign key (station_id) references station(id) on delete cascade
);

create table prices
(
region_id int not null, -- айди региона
fuel_type varchar(20) not null, -- тип топлива
price_per_liter real not null, -- цена
time timestamp default current_timestamp, -- время пинга
primary key (region_id, fuel_type),
CONSTRAINT fk_region_PR FOREIGN KEY(region_id) REFERENCES region(id) on delete cascade
);

create table transactions
(
id serial primary key, -- уникальный id транзакции
pump_id int not null, -- номер колонки
fuel_type varchar(20) not null, -- тип топлива
requested_liters real not null, -- сколько литров заказано
status varchar(20) DEFAULT 'pending', -- статус транзакции pending(ожидание оплаты), progress(налив), completed(завершено)
time timestamp default current_timestamp, -- время пинга
user_id int not null, -- id пользователя
CONSTRAINT fk_pump_id FOREIGN KEY(pump_id) REFERENCES pumps(id), -- внешний ключ с айди колонки
constraint fk_user_id_TR foreign key (user_id) references users(id) on delete cascade
);

create table loyalty_cards
(
id serial primary key, -- id карты лояльности
user_id int not null, -- id пользователя
card_number varchar(30) not null unique, -- номер карты
bonus_balance int default 0, -- баланс карты
discount_percent real default 0.0, -- персональный процент карты
status varchar(20) default 'active', -- active, blocked
time timestamp default current_timestamp, -- время пинга
constraint fk_user_id_LC foreign key (user_id) references users(id) on delete cascade
);