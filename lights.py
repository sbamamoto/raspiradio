#!/usr/bin/python

import time
from neopixel import *
import argparse
import sys

# LED strip configuration:
LED_COUNT      = 3       # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0
LED_STRIP      = ws.WS2812_STRIP 
#LED_STRIP      = ws.SK6812W_STRIP


# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)

# Intialize the library (must be called once before other functions).
strip.begin()

try:
  for i in range(4):
    strip.setPixelColor(0, Color(0, 200, 0))
    strip.setPixelColor(1, Color(0, 200, 0))
    strip.setPixelColor(2, Color(0, 200, 0))
    strip.show()
    time.sleep(1)
    strip.setPixelColor(0, Color(0, 0, 0))
    strip.setPixelColor(1, Color(0, 0, 0))
    strip.setPixelColor(2, Color(0, 0, 0))
    strip.show()
    time.sleep(0.5)

  while True:
      line = raw_input ()
      if line == "ON":
        strip.setPixelColor(0, Color(255, 200, 0))
        strip.setPixelColor(1, Color(255, 200, 0))
        strip.setPixelColor(2, Color(255, 200, 0))
        strip.show()
      elif line == "BLUE":
        strip.setPixelColor(0, Color(0, 0, 255))
        strip.setPixelColor(1, Color(0, 0, 255))
        strip.setPixelColor(2, Color(0, 0, 255))
        strip.show()
      elif line == "QUIT":
        strip.setPixelColor(0, Color(0, 0, 0))
        strip.setPixelColor(1, Color(0, 0, 0))
        strip.setPixelColor(2, Color(0, 0, 0))
        strip.show()
        break
      else:
        strip.setPixelColor(0, Color(0, 0, 0))
        strip.setPixelColor(1, Color(0, 0, 0))
        strip.setPixelColor(2, Color(0, 0, 0))
        strip.show()


except KeyboardInterrupt:
  print "Shutting down"
  strip.setPixelColor(0, Color(0, 0, 0))
  strip.setPixelColor(1, Color(0, 0, 0))
  strip.setPixelColor(2, Color(0, 0, 0))
  strip.show()


