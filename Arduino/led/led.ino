#define LED_PIN 5
#define LED_NUM 120
#include <FastLED.h>
CRGB leds[LED_NUM];

void setup() {
  delay(1500); // Защитная пауза при старте

  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, LED_NUM);
  FastLED.setBrightness(50);
  
  FastLED.clear();
  
  delay(1000);
  fill_solid(leds, LED_NUM, CRGB(255, 147, 41));
  FastLED.show();
}

void loop() {
}