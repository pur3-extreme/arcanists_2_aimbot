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

def main():
           
    swag = tk.Tk()
    frame1 = tk.Frame(swag, padx = 10, pady = 10)
    fire_button = tk.Button(frame1, text = "Fire", command = lambda: fire(custom_angle_field, custom_power_field, user_field), bg = "grey30", fg = "white")
    calculate_button = tk.Button(frame1, text = "Calculate", command = lambda: calculate(custom_angle_field, custom_power_field, time_field, desired_angle_field, desired_power_field, get_float_tuple(user_field), get_float_tuple(target_field)), bg = "grey30", fg = "white")
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
    update_mouse_pos(swag, mouse_pos_field)
    update_mouse_angle(swag, mouse_angle_field, user_field)

    def on_press(key):
        if key == keyboard.Key.f1:
            user_field.delete(0, len(user_field.get()))
            user_field.insert(0, pag.position())
        if key == keyboard.Key.f2:
            target_field.delete(0, len(target_field.get()))
            target_field.insert(0, pag.position())
        if key == keyboard.Key.f3:
            calculate(custom_angle_field, custom_power_field, time_field, desired_angle_field, desired_power_field, get_float_tuple(user_field), get_float_tuple(target_field))
        if key == keyboard.Key.f4:
            fire(custom_angle_field, custom_power_field, user_field)
        if key == keyboard.Key.f5:
            time_field.focus()
        
    listener = keyboard.Listener(on_press = lambda key: on_press(key))
    listener.start()

    swag.mainloop()

def update_mouse_pos(app, pos_field, event = 0):
    pos_field.config(text = pag.position())
    app.after(1, lambda: update_mouse_pos(app, pos_field))

def update_mouse_angle(app, angle_field, user_field, event = 0):
    angle_field.config(text = coords_to_angle(get_center(user_field)))
    app.after(1, lambda: update_mouse_angle(app, angle_field, user_field))

def coords_to_angle(center):
    coords = pag.position()
    (x, y) = (coords[0] - center[0], center[1] - coords[1])

    angle = math.degrees(math.atan2(y, x))
    if angle < 0:
        angle = angle + 360
    return f'{angle:.2f}'

def angle_to_coords(angle, radius, user_field):
    x = math.cos(math.radians(angle)) * radius
    y = math.sin(math.radians(angle)) * radius
    (x, y) = relative_to_absolute_coords(user_field, (x, y))
    return (x, y)

def get_center(user_field):
    
    try: 
        (x, y) = user_field.get().split(" ")
        center = (int(x), int(y))
    except: 
        return default_center

    if x == '' or y == '':
        return default_center
    return center

def relative_to_absolute_coords(user_field, rel_coords):
    (c_x, c_y) = get_center(user_field)
    (rel_x, rel_y) = rel_coords

    (abs_x, abs_y) = (c_x + rel_x, c_y - rel_y)
    return (abs_x, abs_y)

def fire(angle_field, power_field, user_field):

    angle, power = (angle_field.get(), power_field.get())

    if angle == 'impossible' or power == 'impossible':
        return

    angle = float(angle_field.get())
    power = float(power_field.get())
    (x, y) = angle_to_coords(angle, default_radius, user_field)

    pag.mouseDown(x, y, button = 'left')
    time.sleep(power * max_power / 1000)
    pag.mouseUp(button = 'left')

def calculate(angle_field, power_field, time_field, angle_label, power_label, user, target):
    t = float(time_field.get())
    
    power, angle = get_angle_power(user, target, t)
    if power != 'impossible' and angle != 'impossible':
        angle, power = (f"{angle:.5f}", f"{power:.5f}")

    angle_label.config(text = angle)
    power_label.config(text = power)

    angle_field.delete(0, len(angle_field.get()))
    angle_field.insert(0, angle)

    power_field.delete(0, len(power_field.get()))
    power_field.insert(0, power)

def get_angle_power(user, target, t):
    xu, yu = user
    xt, yt = target
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
