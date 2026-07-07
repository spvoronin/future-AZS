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
    } else {
      Serial.print("Ошибка, код = ");
      Serial.print(client.state());
      Serial.println(" Пробуем снова через 5 секунд");
      delay(5000);
    }
  }
}