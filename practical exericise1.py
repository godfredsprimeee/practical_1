# exercise1.py
#PS/CSC/24/0071

from machine import Pin, time_pulse_us
from time import sleep, sleep_ms, sleep_us

print("STARTING EXERCISE 1")

pir_gnd = Pin(14, Pin.OUT)       
pir_gnd.value(0)
sonar_gnd = Pin(12, Pin.OUT)     
sonar_gnd.value(0)


button = Pin(0, Pin.IN, Pin.PULL_UP)  
pir = Pin(27, Pin.IN)                 

trig = Pin(32, Pin.OUT)                
echo = Pin(33, Pin.IN)                 

red = Pin(18, Pin.OUT)                 
green = Pin(16, Pin.OUT)               

def read_cm():
    trig.value(0)
    sleep_us(2)
    trig.value(1)
    sleep_us(10)
    trig.value(0)
    

    pulse = time_pulse_us(echo, 1, 30000)
    if pulse < 0:
        return -1
    return (pulse * 0.0343) / 2

print("PIR warming up... Stand perfectly still for 30 seconds.")
sleep(30)
print("PIR ready! Verification test is active.")

try:
    while True:
        
        is_pressed = not button.value() 
        
        motion_detected = pir.value() == 1

        distance = read_cm()
        
        
        print("Distance: {:.1f} cm | Button: {} | PIR: {}".format(
            distance, 
            "PRESSED" if is_pressed else "RELEASED", 
            "MOTION!" if motion_detected else "STILL"
        ))
        
    
        if distance >= 0:
            # Red turns ON below 20 cm OR if the BOOT button is pressed/PIR detects motion
            red.value(distance < 20 or is_pressed or motion_detected)
            # Green turns ON at 20 cm or greater
            green.value(distance >= 20 and not is_pressed and not motion_detected)
        else:
            # If sensor returns error (-1), shut down lights to avoid mistakes
            red.off()
            green.off()
            
        sleep_ms(200) # Fast updates

except KeyboardInterrupt:
    red.off()
    green.off()
    print("Exercise 1 terminated safely.")
    
