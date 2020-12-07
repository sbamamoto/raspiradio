#!/usr/bin/python


import os, time
import multiprocessing
from StreamPlayer import StreamPlayer
from ShairPortWrapper import ShairPortWrapper
from Rotary import Rotary
import subprocess

#
TUNING_THRESHOLD = 2

VOLUME_STEP = 10

power_state = 0                 #OFF

p=0
i=0

shairport_process = 0

threshold = 0                   # threshold, to switch channels
tuning = 0

lights=subprocess.Popen(["sudo", "python", "/home/pi/radio/lights.py"],stdin=subprocess.PIPE,stdout=subprocess.PIPE);


tuning_noise_active = False

stations = [("STREAM","http://stream.spreeradio.de/spree-live/mp3-128/kontakt/"),
            ("LIST","http://www.radioeins.de/live.m3u"),
            ("STREAM","http://topradio-de-hz-fal-stream08-cluster01.radiohost.de:80/rs2_mp3-128"),
            ("LIST","http://play.rockantenne.de/rockantenne.m3u"),
            ("STREAM","http://musicbird.leanstream.co/JCB031-MP3"),
            ("LIST","http://berlin.starfm.de/player/pls/berlin_pls_mp3.php"),
            ("STREAM","http://stream.104.6rtl.com/rtl-live/mp3-128"),
            ("STREAM", "http://klang.center:8080/paradiso.bln.mp3")]

tunings = ["/home/pi/radio/tuning.mp3"]

def toggle_power():
    global power_state
    global p
    global threshold
    global lights
    global shairport_process

    if power_state == 0:
        lights.stdin.write("ON\n")
        lights.stdin.flush()
        power_state = 1
    elif power_state ==1:
        lights.stdin.write("OFF\n")
        lights.stdin.flush()
        power_state = 0
        threshold = 0
        p.stop()
    elif power_state == 2:
        shairport_process.stop()
        lights.stdin.write("ON\n")
        lights.stdin.flush()
        power_state = 1


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
        p = StreamPlayer(("STREAM", tunings[0]))
    else:
        p = StreamPlayer(url)
    print "sleeping"
    p.wait()


def next_station(direction):
    global i
    global stations

    i += direction

    if i < 0:
        i = len(stations)-1
    elif i > len(stations)-1:
        i = 0

def tune_up():
    senderChange(1)

def tune_down():
    senderChange(0)

def switch_shairport():
    global lights
    global p
    global power_state
    global shairport_process

    if power_state == 1:
        power_state = 2
        lights.stdin.write("BLUE\n")
        lights.stdin.flush()
        p.stop()
        shairport_process = ShairPortWrapper()
        print "Activating Share Port"
    elif power_state == 2:
        shairport_process.stop()
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

    if threshold > 10:                                                         # starte naechsten Kanal
        print "********* next channel"
        next_station(1)
        threshold = 0                                                           # tuning abgeschlossen
        tuning_noise_active = False
        p.stop()

    elif threshold < -10:                                                      # starte vorigen Kanal
        print "********** prev channel"
        next_station(-1)
        threshold = 0
        tuning_noise_active = False
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
    tuning_knob.register(pressed=switch_shairport, onchange=valueChanged)

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
