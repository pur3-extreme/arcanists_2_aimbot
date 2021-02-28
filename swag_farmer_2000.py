import pyautogui as pag
import tkinter as tk
import math
import random
import time
from pynput import keyboard

default_center = (960, 540)
default_time = 1.5
max_power = 2110
min_v = 176.71
max_v = 559.76+min_v
default_radius = 100
g = 441.79473198085058122053071945108
# g = 442
y_offset = 0
dot_rad = 2
scribble = True
traj = 'nil'

def update_mouse_pos():
    mouse_pos_field.config(text = pag.position())
    swag.after(1, update_mouse_pos)

# def coords_to_angle():
#     coords = pag.position()
#     center = get_float_tuple(user_field)
#     (x, y) = (coords[0] - center[0], center[1] - coords[1])

#     angle = math.degrees(math.atan2(y, x))
#     if angle < 0:
#         angle = angle + 360
#     return f'{angle:.2f}'

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
    togc = scribble
    if togc: 
        toggle_canvas()

    angle, power = (custom_angle_field.get(), custom_power_field.get())

    if (power, angle) == ('impossible', 'impossible'):
        return

    angle = float(custom_angle_field.get())
    power = float(custom_power_field.get())
    (x, y) = angle_to_coords(angle, default_radius)

    pag.mouseDown(x, y, button = 'left')
    time.sleep(power * max_power / 1000)
    pag.mouseUp(button = 'left')

    if togc:
        toggle_canvas()

def calculate():

    power, angle = get_angle_power()
    if (power, angle) != ('impossible', 'impossible'):
        angle, power = (f"{angle:.5f}", f"{power:.5f}")
    else: 
        if traj != 'nil':
            draw_canvas.itemconfig(traj, fill = 'red')

    set_dot(draw_t, target_field)
    set_dot(draw_u, user_field)

    desired_angle_field.config(text = angle)
    desired_power_field.config(text = power)

    custom_angle_field.delete(0, len(custom_angle_field.get()))
    custom_angle_field.insert(0, angle)

    custom_power_field.delete(0, len(custom_power_field.get()))
    custom_power_field.insert(0, power)

def get_angle_power():
    global traj
    mode = mode_field.cget('text')

    try: 
        t = float(time_field.get())
    except: 
        time_field.delete(0, len(time_field.get()))
        time_field.insert(0, 'invalid time')
        return 'impossible', 'impossible'
    
    xu, yu = get_float_tuple(user_field)
    xt, yt = get_float_tuple(target_field)
    try:
        x, y = (xt - xu, yu - yt)
    except: 
        return 'impossible', 'impossible'

    if mode == 'time':
        # https://math.stackexchange.com/a/273432
        v = (((x**2) + (y + (0.5 * g * t**2))**2)**0.5) / t
        angle = math.acos((x / (v * t)))
    elif mode == 'mousepos':
        xm, ym = pag.position()
        angle = math.atan2(yu - ym, xm - xu)
        try:
            v = ((g*x**2)/(x*math.sin(2*angle)-2*y*math.cos(angle)**2))**0.5
        except ZeroDivisionError: 
            return 'impossible', 'impossible'
    elif mode == 'minv':
        v = ((y+(y**2+x**2)**0.5)*g)**0.5
        # this can happen because there are no constraints on v
        if v < min_v:
            v = min_v*1.01 # not using MIN_V helps a bit with accuracy
            try: 
                angle = math.atan2(((v**2)+(v**4-g*(g*x**2+2*y*v**2))**0.5)/(g*x),1)
            except ZeroDivisionError: 
                return 'impossible', 'impossible'
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

    if traj != 'nil':
        draw_canvas.delete(traj)
    t_points = generate_pts(xu, x, yu, v, math.radians(angle))
    if len(t_points) > 1:
        traj = draw_canvas.create_line(t_points, '-fill', 'blue')

    return power, angle

def get_power(v_init):
    power = (v_init - 176.71) / 559.76
    return power

def get_float_tuple(field):
    int_tuple = ('impossible', 'impossible')

    try: 
        (x, y) = field.get().split(" ")
        int_tuple = (float(x), float(y))
    except:
        field.delete(0, len(field.get()))
        field.insert(0, 'invalid pos')

    return int_tuple

def set_draw_w():
    if draw_tl.geometry().split('x')[1].split('+')[0] == '1080':
        draw_tl.geometry('400x400')
        draw_tl.update_idletasks()
        draw_tl.overrideredirect(False)
    else: 
        draw_tl.geometry('1920x1080')
        draw_tl.update_idletasks()
        draw_tl.overrideredirect(True)

def set_dot(dot, field):

        x, y = get_float_tuple(field)
        if (x, y) == ('impossible', 'impossible'):
            return
        rootx, rooty = draw_tl.winfo_rootx(), draw_tl.winfo_rooty()
        relx, rely = x - rootx, y - rooty
        draw_canvas.coords(dot, relx-dot_rad, rely-dot_rad, relx+dot_rad, rely+dot_rad)

def toggle_canvas():
    global scribble
    if scribble == True:
        draw_canvas.pack_forget()
        scribble = False
    elif scribble == False: 
        draw_canvas.pack(fill = 'both', expand = True)
        scribble = True


def generate_pts(xu, xd, yu, v, angle):

    def f(x):
        y = -1*(math.tan(angle)*x-((g*x**2)/(2*v**2*math.cos(angle)**2)))+yu-draw_tl.winfo_rooty()
        return y

    return [(xp+xu, min(f(xp), 1080)) for xp in range(0, int(xd), int(math.copysign(1, xd)))]

current_keys = {keyboard.Key.shift:0}
def on_press(key):
    current_keys[key] = 1
    if key == keyboard.Key.f1:
        user_field.delete(0, len(user_field.get()))
        user_field.insert(0, pag.position())
        set_dot(draw_u, user_field)
        calculate()
    if key == keyboard.Key.f2:
        target_field.delete(0, len(target_field.get()))
        target_field.insert(0, pag.position())
        set_dot(draw_t, target_field)
        calculate()
    if key == keyboard.Key.f3:
        toggle_canvas()
    if key == keyboard.Key.f4:
        fire()
    if key == keyboard.Key.f5:
        mode_field.config(text = 'time')
        calculate()
    if key == keyboard.Key.f6:
        mode_field.config(text = 'mousepos')
        calculate()
    if key == keyboard.Key.f7:
        mode_field.config(text = 'minv')
        calculate()
    if key == keyboard.Key.f8:
        mode_field.config(text = 'maxv')
        calculate()
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
set_borderless_button = tk.Button(frame1, text = "Max/Unmax Graphing Window", command = set_draw_w)

draw_tl = tk.Toplevel(swag)
draw_canvas = tk.Canvas(draw_tl)
draw_t = draw_canvas.create_oval(0, 0, 0, 0, '-fill', 'red')
draw_u = draw_canvas.create_oval(0, 0, 0, 0, '-fill', 'green')

def main():
    swag.title("Swag Farmer 2000")
    swag.geometry("400x200")
    draw_tl.title("Arcanists 2")
    draw_tl.attributes('-topmost', True, '-transparentcolor', '#f0f0f0')
    draw_tl.state('zoomed')

    try: 
        draw_tl.iconbitmap('./icons/arc.ico')   
        swag.iconbitmap('./icons/swag.ico')
    except: 
        pass

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
    set_borderless_button.grid(row = 6, column = 1)

    draw_canvas.pack(fill = 'both', expand = True)

    user_field.insert(0, default_center)
    target_field.insert(0, (0, 0))
    time_field.insert(0, default_time)
    update_mouse_pos()

    listener = keyboard.Listener(on_press = on_press, on_release = on_release)
    listener.start()

    # for i in range(100):
    #     x = (1920*i)//100
    #     y = (1080*i)//100
    #     draw_canvas.create_text(x, y, text = f"{i}")

    swag.mainloop()

print("""
                               ##    &&&&&&&%%%* */                             
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
