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
    } else {
      Serial.print("Ошибка, код = ");
      Serial.print(client.state());
      Serial.println(" Пробуем снова через 5 секунд");
      delay(5000);
    }
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
}