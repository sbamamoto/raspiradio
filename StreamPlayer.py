#Using a process in a subclass Chapter 3: Process Based #Parallelism

import multiprocessing
import subprocess
import os

class StreamPlayer():

    def __init__(self, station):
        (type,url) = station
        print "************** Now Playing: %s"%url
        if type == "STREAM":
            self.processHandle = subprocess.Popen(["/usr/bin/mpg123", url])
        else:
            self.processHandle = subprocess.Popen(["/usr/bin/mpg123", "-@", url])

    def stop(self):
        self.processHandle.terminate()

    def wait(self):
        self.processHandle.wait()
