from machine import Pin, Timer

led = Pin(2, Pin.OUT)

# create a Timer (you can choose id=0–3 on ESP32)
timer = Timer(0)

def blink_cb(t):
    # toggle LED state
    led.value(not led.value())

def start_blink(interval_ms):
    """
    Start blinking LED on GPIO 2 every interval_ms milliseconds.
    Returns the Timer object so you can stop it later with timer.deinit().
    """
    timer.init(
        period=interval_ms,        # blink period in ms
        mode=Timer.PERIODIC,       # periodic callback
        callback=blink_cb
    )
    return timer

def stop_blink(t):
    """
    Stop blinking.
    """
    t.deinit()