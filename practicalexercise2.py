# exercise2.py
# PS/CSC/24/0071
from machine import Pin, PWM
from time import ticks_ms, ticks_diff, sleep_ms

print("STARTING EXERCISE 2")

v_gnd = Pin(14, Pin.OUT)
v_gnd.value(0) 


red_pwm = PWM(Pin(21), freq=1000, duty_u16=0)
green_pwm = PWM(Pin(22), freq=1000, duty_u16=0)
blue_pwm = PWM(Pin(23), freq=1000, duty_u16=0)
buzzer = PWM(Pin(25), freq=1000, duty_u16=0)


btn1 = Pin(0, Pin.IN, Pin.PULL_UP)  
btn2 = Pin(4, Pin.IN, Pin.PULL_UP)  


colors_list = [
    (255, 0, 0),     
    (0, 255, 0),     
    (0, 0, 255),     
    (255, 255, 0), 
    (0, 255, 255),   
    (255, 0, 255)   
]
color_names = ["red", "green", "blue", "yellow", "cyan", "magenta"]
brightness_levels = [25, 50, 75, 100]

color_idx = 0
bright_idx = 0

last_press_1 = 0
last_press_2 = 0

color_changed = False
bright_changed = False


def set_color(color, level):
    r, g, b = color
    # Convert 0-255 color scaling and % brightness into 16-bit duty cycle (0-65535)
    r_16 = int((r * 65535 / 255) * (level / 100))
    g_16 = int((g * 65535 / 255) * (level / 100))
    b_16 = int((b * 65535 / 255) * (level / 100))
    
    red_pwm.duty_u16(r_16)
    green_pwm.duty_u16(g_16)
    blue_pwm.duty_u16(b_16)

# --- (b) Short Interrupt Handlers ---
def btn1_handler(pin):
    global last_press_1, color_changed
    now = ticks_ms()
    if ticks_diff(now, last_press_1) > 200: # 200ms debounce tracking
        color_changed = True
        last_press_1 = now

def btn2_handler(pin):
    global last_press_2, bright_changed
    now = ticks_ms()
    if ticks_diff(now, last_press_2) > 200:
        bright_changed = True
        last_press_2 = now

# Attach falling-edge interrupts
btn1.irq(handler=btn1_handler, trigger=Pin.IRQ_FALLING)
btn2.irq(handler=btn2_handler, trigger=Pin.IRQ_FALLING)

# Load baseline state
set_color(colors_list[color_idx], brightness_levels[bright_idx])
print("System Ready! Colour: {}, Brightness: {}%".format(color_names[color_idx], brightness_levels[bright_idx]))

# --- (c) Main Loop Behaviour ---
try:
    while True:
        if color_changed:
            color_changed = False
            color_idx = (color_idx + 1) % len(colors_list)
            set_color(colors_list[color_idx], brightness_levels[bright_idx])
            print("Colour: {}, Brightness: {}%".format(color_names[color_idx], brightness_levels[bright_idx]))
            
            # 100 ms beep at 1000 Hz
            buzzer.freq(1000)
            buzzer.duty_u16(32768)
            sleep_ms(100)
            buzzer.duty_u16(0)

        if bright_changed:
            bright_changed = False
            bright_idx = (bright_idx + 1) % len(brightness_levels)
            set_color(colors_list[color_idx], brightness_levels[bright_idx])
            print("Colour: {}, Brightness: {}%".format(color_names[color_idx], brightness_levels[bright_idx]))
            
            # 100 ms beep at 1500 Hz
            buzzer.freq(1500)
            buzzer.duty_u16(32768)
            sleep_ms(100)
            buzzer.duty_u16(0)
            
        sleep_ms(10) # Tiny delay to reduce CPU overhead smoothly

except KeyboardInterrupt:
    # --- (d) Safe Shutdown ---
    btn1.irq(handler=None)
    btn2.irq(handler=None)
    
    red_pwm.duty_u16(0)
    green_pwm.duty_u16(0)
    blue_pwm.duty_u16(0)
    buzzer.duty_u16(0)
    
    red_pwm.deinit()
    green_pwm.deinit()
    blue_pwm.deinit()
    buzzer.deinit()
    print("Exercise 2 safely stopped.")
