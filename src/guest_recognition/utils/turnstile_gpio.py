import time
from gpiozero import LED
from core import settings


class TurnstileGPIO:

    def __init__(self):
        self.channel_1 = LED(settings.turnstile.gpio.pin_gate)

    def open_gate(self):
        self.channel_1.on()

    def close_gate(self):
        self.channel_1.off()
