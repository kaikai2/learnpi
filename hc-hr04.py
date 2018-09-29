# Chip : Pi ping (GPIO)
# VCC = 2/4 (5V)
# Trig = 18 (GPIO24)
pinTrig = 18
# Echo = 16 (GPIO23)
pinEcho = 16
# GND = 6 (Ground)

import RPi.GPIO as GPIO
import pyaudio
import time
import math
from numpy import linspace,sin,pi,int16
import numpy
import threading
import bisect
import random

def initHC_hr04():
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(pinTrig, GPIO.OUT)
    GPIO.setup(pinEcho, GPIO.IN)

def trigHC_hr04(maxDistance):
    GPIO.output(pinTrig, GPIO.LOW)
    time.sleep(0.000005)
    GPIO.output(pinTrig, GPIO.HIGH)
    time.sleep(0.000010)
    GPIO.output(pinTrig, GPIO.LOW)

    timeout = int(maxDistance / 171.5 * 1000)
    
    channel = GPIO.wait_for_edge(pinEcho, GPIO.RISING, timeout=timeout)
    if channel is None:
        return 0
    begin = time.time()
    channel = GPIO.wait_for_edge(pinEcho, GPIO.FALLING, timeout=timeout)
    if channel is None:
        return 0
    return 171.5 * (time.time() - begin)

pa = None;
s = None;

def init_audio(rate=8000):
  global pa,s
  print "init_audio: Create PyAudio object"
  pa = pyaudio.PyAudio()
  print "init_audio: Open stream"
  s = pa.open(output=True,
            channels=1,
            rate=rate,
            format=pyaudio.paInt16,
            output_device_index=pa.get_default_output_device_info()['index'])
  print "init_audio: audio stream initialized"


def close_audio():
  global pa,s
  print "close_audio: Closing stream"
  s.close()
  print "close_audio: Terminating PyAudio Object"
  pa.terminate()


def note(freq, len, amp=5000, rate=8000):
 t = linspace(0,len,len*rate)
 l1 = len*rate * 0.1
 l2 = len*rate * 0.5
 l3 = len*rate - l1-l2
 ampk = numpy.concatenate((linspace(0,1,l1), linspace(1,0.8,l2), linspace(0.8,0,l3)))
 data = sin(2*pi*freq*t)*ampk*amp
 return data.astype(int16) # two byte integers                                                                      

def tone(freq=440.0, tonelen=0.5, amplitude=5000, rate=8000):
  global s
  # generate sound
  tone = note(freq, tonelen, amplitude, rate)
  s.write(tone)

halfStep = 2 ** (1.0/12)
tuneFreq = [440 * (halfStep ** p) for p in range(-12*2, 12*2)]
print(tuneFreq)
def alignToTone(freq):
    global tuneFreq
    i = bisect.bisect_left(tuneFreq, freq)
    if i < len(tuneFreq):
        return tuneFreq[i]
    return 440.0

class ToneThread(threading.Thread):
    def __init__(self):
        self.freq = 0
        self.exit = False
        init_audio()
        threading.Thread.__init__(self)
        
    def run(self):
        curFreq = 0
        try:
            while not self.exit:
                playFreq = alignToTone(curFreq)
                tone(playFreq, 0.5 * [1,2,4][int(random.random() * 3)] )
                print(self.freq, curFreq, playFreq)
                curFreq = (curFreq + self.freq) / 2.0
                #if self.freq > curFreq:
                #    curFreq += 1
                #else:
                #    curFreq -= 1
        except Exception as e:
            print(e)
        finally:
            close_audio()
            
def main():
    tuneThread = ToneThread()

    tuneThread.start();
    initHC_hr04()

    try:
        i = 0
        while True:
            i +=1
            distance = trigHC_hr04(10)
            freq = -1
            if distance > 0.1 and distance < 5: # more than 10 cm
                freq = (distance / 5) * (4186 - 27.5) + 27.5
                tuneThread.freq = freq
            #print(distance, freq)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
        tuneThread.exit = True
        tuneThread.join()


main()
