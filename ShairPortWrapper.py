#Using a process in a subclass Chapter 3: Process Based #Parallelism

import multiprocessing
import subprocess
import os


class ShairPortWrapper():

    def __init__(self):
        print "************** Running Shairport Airplay interface"
        self.processHandle = subprocess.Popen(["/usr/bin/shairport-sync"])

    def stop(self):
        self.processHandle.terminate()

    def wait(self):
        self.processHandle.wait()
