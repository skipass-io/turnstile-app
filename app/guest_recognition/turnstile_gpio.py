import time

import RPi.GPIO as GPIO


class TurnstileGPIO:
    def _setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.channel_gate, GPIO.OUT)
        time.sleep(self.sleep_time)

    def _cleanup(self):
        time.sleep(self.sleep_time)
        GPIO.cleanup()


    def _connect_to_relay(self):
        GPIO.output(self.channel_gate, GPIO.HIGH)
        time.sleep(self.sleep_time)
        time.sleep(self.sleep_time)
        GPIO.output(self.channel_gate, GPIO.LOW)        


    def open_gate(self):
        self._setup()        
        self._connect_to_relay()
        self._cleanup()
        
    def __init__(self):
        self.channel_gate = 21
        self.sleep_time = 0.25
