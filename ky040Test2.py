#!/usr/bin/python

from Rotary import Rotary
import time

## Define Callback functions
def cwTurn():
    print("CW Turn")

def ccwTurn():
    print("CCW Turn")

def buttonPushed():
    print("Button Pushed")

def valueChanged(count):
    print(count) ## Current Counter value

## Initialise (clk, dt, sw, ticks)
obj = Rotary(5,6,13,2)

 ## Register callbacks
obj.register(increment=cwTurn, decrement=ccwTurn)

## Register more callbacks
obj.register(pressed=buttonPushed, onchange=valueChanged)

## Start monitoring the encoder
obj.start()

try:
    while True:
        time.sleep(0.1)

# Aufraeumarbeiten nachdem das Programm beendet wurde
except KeyboardInterrupt:
    obj.stop()