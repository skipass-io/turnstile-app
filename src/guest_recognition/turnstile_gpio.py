import time
from gpiozero import LED


class TurnstileGPIO:

    def __init__(self):
        self.channel_1 = LED("GPIO9")

    def open_gate(self):
        self.channel_1.on()

    def close_gate(self):
        self.channel_1.off()
