import pyautogui as pag
import tkinter as tk
import math
import random
import time
from pynput import keyboard
import PIL

default_center = (960, 540)
default_time = 1.5
max_power = 2110
default_radius = 100
g = 441.79473198085058122053071945108

def on_press(key):
    if key == keyboard.Key.f1:
        user_field.delete(0, len(user_field.get()))
        user_field.insert(0, pag.position())
    if key == keyboard.Key.f2:
        target_field.delete(0, len(target_field.get()))
        target_field.insert(0, pag.position())
    if key == keyboard.Key.f3:
        calculate()
    if key == keyboard.Key.f4:
        fire()
    if key == keyboard.Key.f5:
        time_field.focus()

def update_mouse_pos():
    mouse_pos_field.config(text = pag.position())
    swag.after(1, update_mouse_pos)

def update_mouse_angle():
    mouse_angle_field.config(text = coords_to_angle(get_center()))
    swag.after(1, update_mouse_angle)

def coords_to_angle(center):
    coords = pag.position()
    (x, y) = (coords[0] - center[0], center[1] - coords[1])

    angle = math.degrees(math.atan2(y, x))
    if angle < 0:
        angle = angle + 360
    return f'{angle:.2f}'

def angle_to_coords(angle, radius):
    x = math.cos(math.radians(angle)) * radius
    y = math.sin(math.radians(angle)) * radius
    (x, y) = relative_to_absolute_coords(x, y)
    return (x, y)

def get_center():
    try: 
        (x, y) = user_field.get().split(" ")
        center = (int(x), int(y))
    except: 
        return default_center

    if x == '' or y == '':
        return default_center
    return center

def relative_to_absolute_coords(rel_x, rel_y):
    (c_x, c_y) = get_center()

    (abs_x, abs_y) = (c_x + rel_x, c_y - rel_y)
    return (abs_x, abs_y)

def fire():

    angle, power = (custom_angle_field.get(), custom_power_field.get())

    if angle == 'impossible' or power == 'impossible':
        return

    angle = float(custom_angle_field.get())
    power = float(custom_power_field.get())
    (x, y) = angle_to_coords(angle, default_radius)

    pag.mouseDown(x, y, button = 'left')
    time.sleep(power * max_power / 1000)
    pag.mouseUp(button = 'left')

def calculate():
    power, angle = get_angle_power()
    if power != 'impossible' and angle != 'impossible':
        angle, power = (f"{angle:.5f}", f"{power:.5f}")

    desired_angle_field.config(text = angle)
    desired_power_field.config(text = power)

    custom_angle_field.delete(0, len(custom_angle_field.get()))
    custom_angle_field.insert(0, angle)

    custom_power_field.delete(0, len(custom_power_field.get()))
    custom_power_field.insert(0, power)

def get_angle_power():
    t = float(time_field.get())
    xu, yu = get_float_tuple(user_field)
    xt, yt = get_float_tuple(target_field)
    x, y = (xt - xu, yu - yt)

    v = (((x**2) + (y + (0.5 * g * t**2))**2)**0.5) / t
    power = get_power(v)
    angle = math.acos((x / (v * t)))
    angle = math.degrees(angle) % 360

    if power < 0 or power > 1:
        return 'impossible', 'impossible'
    return power, angle

def get_power(v_init):
    power = (v_init - 176.71) / 559.76
    return power

def get_float_tuple(field):

    (x, y) = field.get().split(" ")
    int_tuple = (float(x), float(y))

    return int_tuple

swag = tk.Tk()
frame1 = tk.Frame(swag, padx = 10, pady = 10)
fire_button = tk.Button(frame1, text = "Fire", command = fire, bg = "grey30", fg = "white")
calculate_button = tk.Button(frame1, text = "Calculate", command = calculate, bg = "grey30", fg = "white")
mouse_pos_field = tk.Label(frame1, bg = "grey80", fg = "black", width = 8)
mouse_pos_label = tk.Label(frame1, text = "Position")
time_field = tk.Entry(frame1, bg = "grey40", fg = "white", width = 10)
time_label = tk.Label(frame1, text = "Time")
mouse_angle_field = tk.Label(frame1, bg = "grey80", fg = "black", width = 8)
mouse_angle_label = tk.Label(frame1, text = "Angle")
custom_angle_field = tk.Entry(frame1, bg = "grey40", fg = "white", width = 10)
custom_angle_label = tk.Label(frame1, text = "Custom Angle")
desired_angle_field = tk.Label(frame1, bg = "grey80", fg = "black", width = 8)
desired_angle_label = tk.Label(frame1, text = "Suggested Angle")
custom_power_field = tk.Entry(frame1, bg = "grey40", fg = "white", width = 10)
custom_power_label = tk.Label(frame1, text = "Custom Power")
desired_power_field = tk.Label(frame1, bg = "grey80", fg = "black", width = 8)
desired_power_label = tk.Label(frame1, text = "Suggested Power")
user_field = tk.Entry(frame1, bg = "grey40", fg = "white", width = 10)
user_label = tk.Label(frame1, text = "User Position")
target_field = tk.Entry(frame1, bg = "grey40", fg = "white", width = 10)
target_label = tk.Label(frame1, text = "Target Position")

def main():
           
    swag.title("Swag Farmer 2000")
    swag.geometry("400x200")

    frame1.place(anchor = 'center', relx = 0.5, rely = 0.5)
    fire_button.grid(row = 7, column = 0, columnspan = 2, ipadx = 20, pady = 10)
    calculate_button.grid(row = 7, column = 1, columnspan = 2, ipadx = 10, pady = 10)
    mouse_pos_field.grid(row = 1, column = 0, padx = 3)
    mouse_pos_label.grid(row = 0, column = 0)
    time_field.grid(row = 1, column = 2, padx = 3)
    time_label.grid(row = 0, column = 2)
    mouse_angle_field.grid(row = 1, column = 1, padx = 3)
    mouse_angle_label.grid(row = 0, column = 1)
    custom_angle_field.grid(row = 3, column = 1, padx = 3)
    custom_angle_label.grid(row = 2, column = 1)
    desired_angle_field.grid(row = 5, column = 1, padx = 3)
    desired_angle_label.grid(row = 4, column = 1)
    custom_power_field.grid(row = 3, column = 0, padx = 3)
    custom_power_label.grid(row = 2, column = 0)
    desired_power_field.grid(row = 5, column = 0, padx = 3)
    desired_power_label.grid(row = 4, column = 0)
    user_field.grid(row = 3, column = 2, padx = 3)
    user_label.grid(row = 2, column = 2)
    target_field.grid(row = 5, column = 2, padx = 3)
    target_label.grid(row = 4, column = 2)

    user_field.insert(0, default_center)
    time_field.insert(0, default_time)
    update_mouse_pos()
    update_mouse_angle()
        
    listener = keyboard.Listener(on_press = lambda key: on_press(key))
    listener.start()

    swag.mainloop()

print("""                               ##    &&&&&&&%%%* */                             
                      /*,, ##&%%%%%%%%%%%&&%%##%####(*,/                        
                 , ,,###%%%%%%%%%##((((##%&&%%#%%###%%###/**(                   
              ,*.#((/////((##%%%%%&&&%%%#/,,,,/(##%##########*.                 
            @*&&&&&&&&&&&&%%%%%%&%#(*.   *(#(/,   */#%%%#%%###(/&               
          (/%#/**,....(#%%%%&%%#(/,  .(#%%#(///(##(, *(((%%%%#(/*...,,%(        
         * #(,.(%%%%#*. (((%%#(//, .((,,(#,....#(,.,/##((((((((#%%%%###%%(//    
         ,(//*,.,*..*//,,&&%%#/*,,,,../(####((((##%%%%%#(#%%%%%%&&&&&&%%%%(##*. 
       & #(/*(%##%(**/*%&&&%(((##*.,*///***////////((#%%%%%%%####%%&&&&%(/(##(%/
   /(/%%#(///(///****(&&&&%(//(#%%%#,.,,*********/(((//*,,........,*/((((##//(#*
 ./(%%%%&&&%%#/***(#%&&&&&%#(/***/(#&&%(*,...,*/(####%%%%&&&%(*,..    ..,*/**//(
//(%%#((///*///(%##&&&&&&&&%###(/,.,/((#%%&&&&&&&&%%##(/**,,/((*,    ..,,...*///
@%((/*,..*#&%%#//%%#########%%%&%%#/ .**///****,..   .,/#%&%(/,    ,/(*,,..,*///
#(/,..*/#(////*//,/((((((//,.    ,//*.*/(((((((###%&&&%#(*,.      ,/%(*,,,,,*///
.*,... *(***//(/*                 .*(######%&&&%%((/*..   ..,,   *(%#***,.,,*/*,
   **#*,(#%%####(/**,..   .,*//(((##%%%%((//**,.     .,,,,,/*, *(#((,//,.,,**, .
   *%#/./.,*//((/(#%%%%%%%%%(%%(((/*****,.    ..,,*,.//*,,   *((/#/*(/*..,,, ,  
  &,(#/,. .....,..,,.,.,..,,.,,..,, .. ,,*//,*(((///,*,. .,*((((//*#(*,..,      
  /*(#/*,/..*(**,*,..,.,,,.*,***/(/,(#%%(%&&&##//,.  ,(#*//(/(#/*///*,          
  #*(##/,*/#,.*(#&#(%%####(%%%%%&&%(%%%(/*,..    *%%**/(#(/(((//(//**.          
   .#(#(/* /%%.         .  ..                .%&%(*((##/*///////***, .          
   /(((((//,.*#&%#(*,              ,**(#%&@&&#*/##%#/**////////**,,.            
   /#(*(((((((*,...*/(####(#%%%###(/*.,,*/(#####(***///////////*,, .            
   ,#(//(((((#########(((///////((###%%%%#(/********//////////*,,.              
   *##(//////(((((####%%%%%%%%%##(//*************////(((/////*,.                
   #%%%#/////////((/(((((((/////////*****,,***////(((((////**, .                
 * %#%%%####(((((/**///////////***********//((((((((//////*,,                   
 * ######%%%%%%%&&%%%%##(////////////((##%%###((((//////**,..                   
 * #############%%%%%&&&&&&&&&&&&%%%%%%%##(((/////////**,                       
  @,#############((((((##########(((((//////////////*,.                         
   ,((((((((####((((((((((((/////////////////////*,,                            
    ,.//////////((((((((((///////////////////**,                                
      *.,********///////////////////*****,,,..                                  
         ** ,,,,,,,***********,,,,,,,,.. .                                      """)


main()
