# exercise3.py
from machine import Pin, PWM
import neopixel
from time import ticks_ms, ticks_diff, sleep_ms

# --- MULTIPLE VIRTUAL GROUNDS ---
Pin(14, Pin.OUT).value(0) # Ground for PIR
Pin(12, Pin.OUT).value(0) # Ground for NeoPixels / Buzzer

btn1 = Pin(15, Pin.IN, Pin.PULL_UP)
pir = Pin(27, Pin.IN)
red = Pin(18, Pin.OUT)
yellow = Pin(17, Pin.OUT)
green = Pin(16, Pin.OUT)
buzzer = PWM(Pin(25), freq=1000, duty_u16=0)
np = neopixel.NeoPixel(Pin(26), 8)

DISARMED, ARMING, ARMED, ALARM = 0, 1, 2, 3
current_state = DISARMED
btn1_flag, motion_flag = False, False
last_btn_time, alarm_count = 0, 0
start_time, state_timer, blink_timer = ticks_ms(), ticks_ms(), ticks_ms()

def clear_all_outputs():
    red.off(); yellow.off(); green.off(); buzzer.duty_u16(0)
    for i in range(8): np[i] = (0,0,0)
    np.write()

def set_traffic_light(color):
    red.value(color == "red")
    yellow.value(color == "yellow")
    green.value(color == "green")

def btn1_isr(pin):
    global last_btn_time, btn1_flag
    now = ticks_ms()
    if ticks_diff(now, last_btn_time) > 200:
        btn1_flag = True; last_btn_time = now

def pir_isr(pin):
    global motion_flag
    if current_state == ARMED: motion_flag = True

btn1.irq(handler=btn1_isr, trigger=Pin.IRQ_FALLING)
pir.irq(handler=pir_isr, trigger=Pin.IRQ_RISING)

def transition_to(new_state, state_name):
    global current_state, state_timer
    elapsed_s = ticks_diff(ticks_ms(), start_time) / 1000.0
    state_labels = {DISARMED: "DISARMED", ARMING: "ARMING", ARMED: "ARMED", ALARM: "ALARM"}
    print("[{:.1f} s] {} -> {}".format(elapsed_s, state_labels[current_state], state_name))
    clear_all_outputs()
    current_state = new_state
    state_timer = ticks_ms()

toggle_state = False

try:
    while True:
        now = ticks_ms()
        if btn1_flag:
            btn1_flag = False
            if current_state == DISARMED: transition_to(ARMING, "ARMING")
            else: transition_to(DISARMED, "DISARMED")

        if current_state == ARMING:
            if ticks_diff(now, state_timer) >= 10000:
                motion_flag = False
                transition_to(ARMED, "ARMED")
            elif ticks_diff(now, blink_timer) >= 500:
                blink_timer = now; toggle_state = not toggle_state
                set_traffic_light("yellow" if toggle_state else "off")
                buzzer.duty_u16(16384 if toggle_state else 0)

        elif current_state == ARMED:
            set_traffic_light("green")
            np[0] = (0, 10, 0); np.write()
            if motion_flag:
                motion_flag = False; alarm_count += 1
                transition_to(ALARM, "ALARM")

        elif current_state == ALARM:
            set_traffic_light("red")
            if ticks_diff(now, state_timer) >= 30000:
                transition_to(ARMED, "ARMED")
            elif ticks_diff(now, blink_timer) >= 250:
                blink_timer = now; toggle_state = not toggle_state
                buzzer.freq(880 if toggle_state else 660)
                buzzer.duty_u16(32768)
                for i in range(8): np[i] = (40, 0, 0) if toggle_state else (0,0,0)
                np.write()

except KeyboardInterrupt:
    btn1.irq(handler=None); pir.irq(handler=None); clear_all_outputs(); buzzer.deinit()
    print("Final Alarm Count:", alarm_count)
