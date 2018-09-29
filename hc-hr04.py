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


def initHC_hr04():
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(pinTrig, GPIO.OUT)
    GPIO.setup(pinEcho, GPIO.IN)

def trigHC_hr04():
    GPIO.output(pinTrig, GPIO.LOW)
    time.sleep(0.000005)
    GPIO.output(pinTrig, GPIO.HIGH)
    time.sleep(0.000010)
    GPIO.output(pinTrig, GPIO.LOW)
    begin = time.time()
    channel = GPIO.wait_for_edge(pinEcho, GPIO_RISING, timeout=5000)
    if channel is None:
        return 0
    return 340 / (time.time() - begin)

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
            output_device_index=pa.get_default_output_device_info()['index']])
  print "init_audio: audio stream initialized"


def close_audio():
  global pa,s
  print "close_audio: Closing stream"
  s.close()
  print "close_audio: Terminating PyAudio Object"
  pa.terminate()


def note(freq, len, amp=5000, rate=8000):
 t = linspace(0,len,len*rate)
 data = sin(2*pi*freq*t)*amp
 return data.astype(int16) # two byte integers                                                                      

def tone(freq=440.0, tonelen=0.5, amplitude=5000, rate=8000):
  global s
  # generate sound
  tone = note(freq, tonelen, amplitude, rate)

  s.write(tone)


def main():
    init_audio()

    initHC_hr04()

    try:
        while True:
            distance = trigHC_hr04()
            if distance > 0.1: # more than 10 cm                
                tone(distance * 440)
    except e:
        GPIO.cleanup()
        close_audio()
