from multiprocessing import Process #built in module since 2.6
import time #built in module
import math #built in module
import pygame #pip install pygame
import pyaudio #pip install pyaudio
import serial #pip install pyserial
import keyboard #pip install keyboard
#define frequency ranges of the bands....not done
fm=["FA",100000000,108000000,10000] #need to append a 0 for < 100mhz
noaa=["FA",162545000,162557000,1000]
ten_meter=["FA0",28000000,29700000,5000]
twenty_meter=["FA0",14000000,14350000,1000]
forty_meter=["FA00",7000000,7300000, 1000]
eighty_meter=["FA00",3000000,4000000, 1000]
two_meter=["FA",144000000,148000000,10000]
seventy_centimeter=["FA",420000000,450000000,100000]
band_to_scan=fm #todo add switch for user input
global space_bar #todo check which variables need to be global
space_bar=True
LAST_STATION=0
global p
com_port_id = 0
p = pyaudio.PyAudio()
y_pos=0
sound_values = []
screen_width = 1000
screen_height = 600
scan_area_width=screen_width
scan_area_height=screen_height-300
sine_area_width=screen_width
sine_area_height=500
x_axis_increment=(band_to_scan[2]-band_to_scan[1])/10
#todo rename functions
def get_microphone_input_level():
    data = stream.read(1024)
    rms = 0
    for i in range(0, len(data), 2):
        sample = int.from_bytes(data[i:i+2], byteorder='little', signed=True)
        rms += sample * sample
    rms = math.sqrt(rms / (512))
    return rms
def find_max_min(arr, n):
    arr.append(1850) #todo check init values on different of sound cards
    arr.append(10)
    max = arr[0]
    min = arr[0]
    for i in range(1, n):
        if arr[i] > max:
            max = arr[i]
        if arr[i] < min:
            min = arr[i]
    return max, min
def draw_graph(rgb_value, x_pos, y_pos,frequency): #todo rename this function
    progress_color = (0,255,0)
    progress_x_pos=x_pos+3
    signal_color=(rgb_value,rgb_value,rgb_value)
    pygame.draw.rect(screen, (0,0,0), pygame.Rect(x_pos, y_pos, 10, 10))
    pygame.draw.rect(screen, (0,0,255), pygame.Rect(0, y_pos+1, 1000, 1))
    pygame.draw.rect(screen, signal_color, pygame.Rect(x_pos, y_pos, 20, 20))
    if rgb_value > 100:
        global LAST_STATION
        LAST_STATION=frequency
        text_surface = str(frequency)[:7]
        #to do add . appropriately for different bands
        #text_surface='.'.join(text_surface[i:i+3] for i in range(0, len(text_surface), 3)) 
        text_surface="Current Frequency: " + text_surface
        text_surface=lcd_font.render(text_surface,False,(0,255,0))
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(0,285, 1000, 15))
        screen.blit(text_surface,(0,285))
    pygame.display.flip()
def draw_sine_wave(amplitude):
    pygame.draw.rect(screen, (0,0,0), pygame.Rect(0,300, 1000, 300))
    sine_font = pygame.font.SysFont('Tahoma', 25)           
    sine_font = sine_font.render("UP/DOWN ARROW TO TUNE", True, (0,255,0))
    text_rect = sine_font.get_rect(center=(screen_width/2, screen_height-500/2))
    screen.blit(sine_font, text_rect)
    points = []
    if amplitude > 10:
        for x in range(screen_width):
            y = (sine_area_height) + int(amplitude * math.sin(x * 0.1))
            points.append((x,y))
    else:
        points.append((0, (sine_area_height)))
        points.append((sine_area_width, (sine_area_height)))
    pygame.draw.lines(screen, (255,255,255), False, points, 2)
    pygame.display.flip()
def main_loop(com_port_id):
    y_pos=0
    f=band_to_scan[1]
    running=True
    global space_bar
    global LAST_STATION
    amplitude = 100
    try:
        ser = serial.Serial(com_port_id, 38400,timeout=1)
        while running:
            pygame.draw.rect(screen, (0,255,0), pygame.Rect(0,305, 1000, 300))
            pause_font = pygame.font.SysFont('Tahoma', 50)           
            pause_font = pause_font.render("SCANNING....PRESS SPACE TO STOP", True, (0,0,0))
            text_rect = pause_font.get_rect(center=(screen_width/2, screen_height-300/2))
            screen.blit(pause_font, text_rect)
            if keyboard.is_pressed(" "):
                pygame.draw.rect(screen, (0,0,0), pygame.Rect(0,300, 1000, 300))
                fStr=str(LAST_STATION)
                fStr=band_to_scan[0]+fStr+";"
                c=fStr.encode()
                ser.write(c)
                time.sleep(1)
                space_bar=not space_bar
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Goodbye!")
                    pygame.quit()            
                    running = False
            if space_bar == True:
                f=f+band_to_scan[3] #increment the frequency with the 3rd value of band array
                if f>band_to_scan[2]:
                    y_pos=y_pos+3
                    f=band_to_scan[1]
                if y_pos>260:
                    y_pos=0
                fStr=str(f)
                fStr=band_to_scan[0]+fStr+";"
                c=fStr.encode()
                ser.write(c)            
                mic_input_level=get_microphone_input_level()
                sound_values.append(mic_input_level)
                n=len(sound_values)
                sound_max,sound_min = find_max_min(sound_values, n)
                max_minus_min=sound_max-sound_min
                if max_minus_min == 0:
                    print("dont div by zero")
                else:  
                    rgb_value=abs(((mic_input_level-sound_min)/(sound_max-sound_min))*255)
                    frequency_normalize=int(((f-band_to_scan[1])/(band_to_scan[2]-band_to_scan[1]))*1000)
                    draw_graph(rgb_value,frequency_normalize,y_pos,f)
            else:
                mic_input_level=get_microphone_input_level()
                amplitude_adjustment = (mic_input_level /99)-100
                amplitude = max(10, amplitude_adjustment)
                draw_sine_wave(amplitude)
                #todo add vertical frequency indicator while navigating through frequencies        
                if keyboard.is_pressed("down arrow"):
                    LAST_STATION=LAST_STATION-band_to_scan[3]
                    fStr=str(LAST_STATION)
                    fStr=band_to_scan[0]+fStr+";"
                    c=fStr.encode()
                    ser.write(c)
                    time.sleep(.1)
                if keyboard.is_pressed("up arrow"):
                    LAST_STATION=LAST_STATION+band_to_scan[3]
                    fStr=str(LAST_STATION)
                    fStr=band_to_scan[0]+fStr+";"
                    c=fStr.encode()
                    ser.write(c)
                    time.sleep(.1)
    except KeyboardInterrupt:
        n=len(sound_values)
        print("keyboard interrupt")
        pygame.quit()
if __name__ == '__main__':
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
    sound_card_id=input("WHICH SOUNDCARD DO YOU WANT TO LISTEN TO? ")
    sound_card_id=int(sound_card_id)
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=sound_card_id, frames_per_buffer=1024)
    pygame.font.init()
    lcd_font = pygame.font.SysFont('Tahoma', 15)
    pygame.display.set_caption("")
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    i = 0
    while i < 11:
        x_axis_label=str(band_to_scan[1]+(x_axis_increment*i))
        #todo add . in different places for bands
        #x_axis_label='.'.join(x_axis_label[i:i+3] for i in range(0, len(x_axis_label), 3))
        x_pos=(scan_area_width/10)*i
        text_surface = lcd_font.render(x_axis_label[:7],False, (0,255,0))
        screen.blit(text_surface,(x_pos,scan_area_height-35))
        i+=1
    com_port_id=input("WHICH COM PORT ex: 3? ")
    com_port_id="COM"+str(com_port_id)
    process = Process(target=main_loop(com_port_id))
    process.start()
    while process.is_alive():
        if keyboard.is_pressed('q'):
            process.terminate()
            pygame.quit()
            break
