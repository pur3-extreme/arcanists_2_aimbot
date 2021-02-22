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
min_v = 176.71
max_v = 559.76+min_v
default_radius = 100
g = 441.79473198085058122053071945108

def update_mouse_pos():
    mouse_pos_field.config(text = pag.position())
    swag.after(1, update_mouse_pos)

def coords_to_angle():
    coords = pag.position()
    center = get_float_tuple(user_field)
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

    if (power, angle) != ('impossible', 'impossible'):
        return

    angle = float(custom_angle_field.get())
    power = float(custom_power_field.get())
    (x, y) = angle_to_coords(angle, default_radius)

    pag.mouseDown(x, y, button = 'left')
    time.sleep(power * max_power / 1000)
    pag.mouseUp(button = 'left')

def calculate():

    power, angle = get_angle_power()
    if (power, angle) != ('impossible', 'impossible'):
        angle, power = (f"{angle:.5f}", f"{power:.5f}")

    desired_angle_field.config(text = angle)
    desired_power_field.config(text = power)

    custom_angle_field.delete(0, len(custom_angle_field.get()))
    custom_angle_field.insert(0, angle)

    custom_power_field.delete(0, len(custom_power_field.get()))
    custom_power_field.insert(0, power)

def get_angle_power():
    mode = mode_field.cget('text')

    try: 
        t = float(time_field.get())
    except: 
        time_field.delete(0, len(time_field.get()))
        time_field.insert(0, 'invalid time')
        return 'impossible', 'impossible'
    
    xu, yu = get_float_tuple(user_field)
    xt, yt = get_float_tuple(target_field)
    x, y = (xt - xu, yu - yt)

    if mode == 'time':
        # https://math.stackexchange.com/a/273432
        v = (((x**2) + (y + (0.5 * g * t**2))**2)**0.5) / t
        angle = math.acos((x / (v * t)))
    elif mode == 'mousepos':
        xm, ym = pag.position()
        angle = math.atan2(yu - ym, xm - xu)
        v = ((g*x**2)/(x*math.sin(2*angle)-2*y*math.cos(angle)**2))**0.5
    elif mode == 'minv':
        v = ((y+(y**2+x**2)**0.5)*g)**0.5
        # this can happen because there are no constraints on v
        if v < min_v:
            v = min_v*1.01 # not using MIN_V helps a bit with accuracy
            angle = math.atan2(((v**2)+(v**4-g*(g*x**2+2*y*v**2))**0.5)/(g*x),1)
            if x<0: angle -= math.pi
        else:
            angle = (math.pi/2)-0.5*(math.pi/2-math.atan2(y,x))
            if x<0 and y<0: angle -= math.pi
    elif mode == 'maxv':
        v = max_v*0.99 # not using MAX_V helps a bit with accuracy
        # there's another solution which will shoot it straight
        angle = math.atan2(((v**2)+(v**4-g*(g*x**2+2*y*v**2))**0.5)/(g*x),1)
        if x<0: angle -= math.pi

    angle = math.degrees(angle) % 360
    power = get_power(v)

    if type(power) == complex or power < 0 or power > 1:
        return 'impossible', 'impossible'
    return power, angle

def get_power(v_init):
    power = (v_init - 176.71) / 559.76
    return power

def get_float_tuple(field):

    (x, y) = field.get().split(" ")
    int_tuple = (float(x), float(y))

    return int_tuple


current_keys = {keyboard.Key.shift:0}
def on_press(key):
    current_keys[key] = 1
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
        mode_field.config(text = 'time')
    if key == keyboard.Key.f6:
        mode_field.config(text = 'mousepos')
    if key == keyboard.Key.f7:
        mode_field.config(text = 'minv')
    if key == keyboard.Key.f8:
        mode_field.config(text = 'maxv')
def on_release(key):
    current_keys[key] = 0

swag = tk.Tk()
frame1 = tk.Frame(swag, padx = 10, pady = 10)
mouse_pos_field = tk.Label(frame1, bg = "grey80", fg = "black", width = 8)
mouse_pos_label = tk.Label(frame1, text = "Position")
time_field = tk.Entry(frame1, bg = "grey40", fg = "white", width = 10)
time_label = tk.Label(frame1, text = "Time")
mode_field = tk.Label(frame1, text = 'time', bg = "grey80", fg = "black", width = 8)
mode_label = tk.Label(frame1, text = "Mode")
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
    mouse_pos_field.grid(row = 1, column = 0, padx = 3)
    mouse_pos_label.grid(row = 0, column = 0)
    time_field.grid(row = 1, column = 2, padx = 3)
    time_label.grid(row = 0, column = 2)
    mode_field.grid(row = 1, column = 1, padx = 3)
    mode_label.grid(row = 0, column = 1)
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
        
    listener = keyboard.Listener(on_press = lambda key: on_press(key), on_release = lambda key: on_release(key))
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
