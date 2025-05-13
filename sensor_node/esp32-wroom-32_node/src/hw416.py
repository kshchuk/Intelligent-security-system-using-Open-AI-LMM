import machine
import time

class HW416:
    def __init__(self, pin_no, callback, debounce_ms=200):
        """
        :param pin_no:       ESP32 GPIO number (e.g. 14)
        :param callback:     function(state: bool) called on motion start/stop
        :param debounce_ms:  ignore edges occurring within this many ms
        """
        # Configure OUT pin as input (no internal pull)
        self.pin = machine.Pin(pin_no, machine.Pin.IN)
        self.cb = callback
        self.debounce_ms = debounce_ms
        self._last = 0

        # Attach IRQ on rising and falling edges
        self.pin.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING,
                     handler=self._irq)

    def _irq(self, pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last) < self.debounce_ms:
            return                  # ignore bounce
        self._last = now

        state = bool(pin.value())  # True=motion, False=idle
        self.cb(state)             # deliver to user
