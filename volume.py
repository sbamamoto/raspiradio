#!/usr/bin/python


import os, time
import multiprocessing
from StreamPlayer import StreamPlayer
from Rotary import Rotary
import subprocess

#
TUNING_THRESHOLD = 2

VOLUME_STEP = 10

power_state = 0                 #OFF

p=0
i=0

threshold = 0                   # threshold, to switch channels

tuning = 0

lights=subprocess.Popen(["sudo", "python", "/mnt/radio/lights.py"],stdin=subprocess.PIPE,stdout=subprocess.PIPE);


tuning_noise_active = False

stations = [("STREAM","http://stream.104.6rtl.com/rtl-live/mp3-192"),
            ("STREAM","http://streams.antennemv.de/antennemv-live/mp3-192/amv"),
            ("LIST","http://streams.br.de/bayern1_2.m3u"),
            ("STREAM","http://topradio-de-hz-fal-stream09-cluster01.radiohost.de/kissfm_128"),
            ("STREAM","http://klassikr.streamabc.net/klassikradio-simulcast-mp3-hq"),
            ("STREAM","http://stream.jam.fm/jamfm-live/mp3-192")]

tunings = ["tuning.mp3"]

def toggle_power():
    global power_state
    global p
    global threshold
    global lights

    if power_state == 0:
        lights.stdin.write("ON\n")
        lights.stdin.flush()
        power_state = 1
    else:
        lights.stdin.write("OFF\n")
        lights.stdin.flush()
        power_state = 0
        threshold = 0
        p.stop()


def readVolume():
    value = os.popen("amixer get Speaker|grep -o [0-9]*%|sed 's/%//'").read()
    value = value.split('\n')[0]
    return int(value)

def volumeUp():
    print "Volume Up"
    volume = readVolume()
    os.system("sudo amixer set Speaker -- " + str(min(100, max(1, volume + VOLUME_STEP))) + "%")

def volumeDown():
    print "Volume Down"
    volume = readVolume()
    os.system("sudo amixer set Speaker -- " + str(min(100, max(1, volume - VOLUME_STEP))) + "%")

# def rotaryChange(direction):
#     volume_step = 10
#     volume = readVolume()
#     if direction == 1:
#         os.system("sudo amixer set Speaker -- "+str(min(100,max(1,volume + volume_step)))+"%")
#     else:
#         os.system("sudo amixer set Speaker -- "+str(min(100,max(1,volume - volume_step)))+"%")
#

def tuneInStation(url):
    global p
    global tuning_noise_active
    if tuning_noise_active:
        p = StreamPlayer(("STREAM", "/mnt/radio/tuning.mp3"))
    else:
        p = StreamPlayer(url)
    print "sleeping"
    p.wait()


def next_station(direction):
    global i
    global stations

    i += direction

    if i < 0:
        i = 0
    elif i > len(stations):
        i = len(stations)

def tune_up():
    senderChange(1)

def tune_down():
    senderChange(0)

def switch_shareport():
    global lights
    global p
    global power_state

    if power_state == 1:
        power_state = 2
        lights.stdin.write("BLUE\n")
        lights.stdin.flush()
        p.stop()

        print "Activating Shairport"
    elif power_state == 2:
        lights.stdin.write("ON\n")
        lights.stdin.flush()
        power_state = 1

# Wenn nach rechts gedreht wird mehr als zweimal wird der tuning sound eingespielt. Bei 10 Signalen fuer
# die gleiche Richtung wird der naechste Sender aktiviert.
# Ansonsten wird wenn man wieder zurueckdreht der vorhergehende Sender eingestellt, sobald man wieder bei 0 steht.
#
# +10 = naechster Kanal
#
# -10 = vorheriger Kanal
#
# +/-2 start tuning sounds

def senderChange(direction):
    global i
    global threshold
    global p
    global tuning_noise_active

    progress = 0

    if direction == 0:
        progress = -1
    else:
        progress = 1

    threshold += progress

    print "###### Progress %d,  Threshold %d"%(progress,threshold)

    if threshold >= 10:                                                         # starte naechsten Kanal
        print "********* next channel"
        next_station(1)
        p.stop()
        threshold = 0                                                           # tuning abgeschlossen

    elif threshold <= -10:                                                      # starte vorigen Kanal
        print "********** prev channel"
        next_station(-1)
        threshold = 0
        p.stop()

    elif abs(threshold) > TUNING_THRESHOLD:                                     # start tuning sounds
        print "Tuning noise on"
        if not tuning_noise_active:
            tuning_noise_active = True
            p.stop()

    else:
        print "Tuning noise off "
        print tuning_noise_active
        if tuning_noise_active:
            tuning_noise_active = False
            p.stop()

def valueChanged(count):
    print(count) ## Current Counter value

def switchPressed(direction):
     print "button pressed"
     p.stop()
 
 
if __name__ == "__main__":

    ## Initialise (clk, dt, sw, ticks)
    volume_knob = Rotary(5, 6, 13, 2)
    tuning_knob = Rotary(21, 20, 16, 2)

    ## Register callbacks
    volume_knob.register(increment=volumeUp, decrement=volumeDown)
    tuning_knob.register(increment=tune_up, decrement=tune_down)

    ## Register more callbacks
    volume_knob.register(pressed=toggle_power, onchange=valueChanged)
    tuning_knob.register(pressed=switch_shareport, onchange=valueChanged)

    ## Start monitoring the encoder
    volume_knob.start()
    tuning_knob.start()

    try:
        while True:
            if power_state == 1:
                tuneInStation(stations[i])

    finally:
        lights.stdin.write("QUIT\n")
        lights.stdin.flush()
        time.sleep(2)
        print "Detaching GPIOs."
        volume_knob.stop()
        tuning_knob.stop()
