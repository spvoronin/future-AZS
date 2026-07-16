void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Подключение к Wi-Fi: ");
  Serial.println(SECRET_SSID);

  WiFi.begin(SECRET_SSID, SECRET_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi подключен! IP: " + WiFi.localIP().toString());
}

void reconnect() {
  // Цикл, пока не подключимся к MQTT
  while (!client.connected()) {
    Serial.print("Попытка подключения к MQTT...");
    // Пытаемся подключиться с твоим логином и паролем
    if (client.connect("ESP32Client_AZS", SECRET_MQTT_USER, SECRET_MQTT_PASS)) {
      Serial.println("Успешно!");

      client.subscribe("BV/SAF/1");
      Serial.println("Подписка на топик BV/SAF/1 оформлена.");
      client.subscribe("BV/SAF/cam/response");
      Serial.println("Подписка на топик BV/SAF/cam/response оформлена.");
    } else {
      Serial.print("Ошибка, код = ");
      Serial.print(client.state());
      Serial.println(" Пробуем снова через 5 секунд");
      delay(5000);
    }
  }
}


void sendTelemetryMQTT(String time_timestamp) {
  // Выделяем память под JSON-документ (300 байт с запасом)
  StaticJsonDocument<300> doc;

  // Заполняем по твоему шаблону
  doc["key"] = "info_about_sensor_SAF";
  doc["uuid"] = SECRET_DEVICE_UUID;
  doc["timestamp"] = time_timestamp;
  doc["electric_current"] = currentData.current_mA;
  doc["flame"] = currentData.flame;
  doc["gas"] = currentData.gaz;
  doc["ambient_humidity"] = currentData.airHumidity;
  doc["ambient_temperature"] = currentData.airTemp;
  doc["tank_temperature"] = round(currentData.fuelTemp * 100.0) / 100.0;
  doc["water_level"] = currentData.fuelLevel;

  // Конвертируем JSON в текстовую строку
  String jsonString;
  serializeJson(doc, jsonString);

  // Выводим в Serial для контроля
  Serial.print("Отправка пакета: ");
  Serial.println(jsonString);

  // Если связь с брокером есть - публикуем в топик из secrets.h
  if (client.connected()) {
    client.publish(SECRET_TOPIC_PUB, jsonString.c_str());
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Пришло сообщение в топик: ");
  Serial.println(topic);

  // Собираем входящую строку
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Содержимое: ");
  Serial.println(message);

  //Проверяем топик
  if (String(topic) == "BV/SAF/1") {
    if (message == "change") {
      bool newRelayState = !digitalRead(RELAY_PIN);
      digitalWrite(RELAY_PIN, newRelayState);

      currentData.relay = newRelayState;

      Serial.print("Реле: ");
      Serial.println(currentData.relay ? "ВКЛ (HIGH)" : "ВЫКЛ (LOW)");
    }
  }

  if (String(topic) == "BV/SAF/cam/response") {
    // Устанавливаем цвета: черный текст на белом фоне (чтобы затирать старые буквы)
    tft.setTextColor(ST77XX_BLACK, ST77XX_WHITE);
    tft.setTextSize(2);
    
    tft.setCursor(y_start, x_start + shift * 7); // 
    tft.print(message);

    tft.print("        "); 
  }
}