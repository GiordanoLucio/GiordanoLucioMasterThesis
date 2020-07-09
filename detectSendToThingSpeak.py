# standard modules for object detection
import sensor,image,lcd
import KPU as kpu
# modules for the connection
import usocket, network, time
import lcd, image
from Maix import GPIO
from machine import UART
from fpioa_manager import fm, board_info

#to send rest message to the ThingSpeak platform
import urequests


lcd.init(freq=15000000)
# increases the FPS at the exchange of a higher usage of RAM
sensor.reset(dual_buff=True)
# sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224, 224))
sensor.set_vflip(0)
sensor.run(1)

# classes to be detected
classes = ["person"]
# models to be loaded
tinyYolo = "/sd/models/tinyYoloMerged.kmodel" #16 fps
mbnet75 = "/sd/models/mbnet75Merged.kmodel" #12 fps
mbnet50 = "/sd/models/mbnet50Merged.kmodel" #15fps
mbnet25 = "/sd/models/mbnet25Merged.kmodel" #16fps
# change here which model to load
task=kpu.load(mbnet50)
# Kmodel V4 needs their output to be defined.
# it requires the kpu task, the output_index because Kmodel v4 support multi output
# w,h,channels which must match the shape of the last layer of the model
a = kpu.set_outputs(task, 0,7,7,30)
# the anchors to be used by the yolo v2 algorithm. These are the anchors for standard yolo v2 tiny.
# even though it is possible to recalculate them on our datasets, it wasn't noticed any difference
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)

# initialize the yolo v2 network
a = kpu.init_yolo2(task, 0.25, 0.3, 5, anchor)
# clock is required to print the fps
clock = time.clock()


# for new MaixGO board, if not, remove it
fm.register(0, fm.fpioa.GPIOHS1, force=True)
wifi_io0_en=GPIO(GPIO.GPIOHS1, GPIO.OUT)
wifi_io0_en.value(0)

# En SEP8285
fm.register(8, fm.fpioa.GPIOHS0, force=True)
wifi_en=GPIO(GPIO.GPIOHS0,GPIO.OUT)
fm.register(board_info.WIFI_RX,fm.fpioa.UART2_TX, force=True)
fm.register(board_info.WIFI_TX,fm.fpioa.UART2_RX, force=True)

def wifi_enable(en):
    global wifi_en
    wifi_en.value(en)

def wifi_reset():
    global uart
    wifi_enable(0)
    time.sleep_ms(200)
    wifi_enable(1)
    time.sleep(2)

    uart = UART(UART.UART2,115200,timeout=1000, read_buf_len=4096)
    tmp = uart.read()
    uart.write("AT+UART_CUR=921600,8,1,0,0\r\n")
    print(uart.read())
    uart = UART(UART.UART2,921600,timeout=1000, read_buf_len=10240) # important! baudrate too low or read_buf_len too small will loose data
    uart.write("AT\r\n")
    tmp = uart.read()
    print(tmp)
    if not tmp.endswith("OK\r\n"):
        print("reset fail")
        return None
    try:
        nic = network.ESP8285(uart)
    except Exception:
        return None
    return nic

nic = wifi_reset()
if not nic:
    raise Exception("WiFi init fail")
try:
    wifi_password="PASSWORD"
    nic.connect("SANBERNARDO",wifi_password)
except:
    print('connection failed')

personDetected=0
loopCycle=0
maximum=0
x=0
while(True):
    loopCycle += 1
    clock.tick()
    img = sensor.snapshot()
    a = img.pix_to_ai()
    #run yolo v2 algorithm on the neural network loaded at the beginning with last image as input
    code = kpu.run_yolo2(task, img)

    number_of_person=0
    print("fps: ", clock.fps())
    if code: # if list is not empty
        print("ok, found person...", code)
        for i in code: # for each element found in the image
            number_of_person+=1
            a=img.draw_rectangle(i.rect())
            lcd.draw_string(i.x(), i.y(), classes[i.classid()], lcd.RED, lcd.WHITE)
            lcd.draw_string(i.x(), i.y()+12, '%f1.3'%i.value(), lcd.RED, lcd.WHITE)
            a = lcd.display(img)
    else:
        a = lcd.display(img)
    personDetected += number_of_person
    if personDetected > maximum:
        maximum = personDetected
    assignedToAvoidPrint=img.draw_string(0, 0, "number of person: "+str(number_of_person), scale=1.5)
    # takes 100 frames and send the number of people detected to ThingSpeak and also
    # the Maximum of detection occurred in the same image
    if loopCycle%100==0:
        print("now sending...")
        mediumValue = personDetected/loopCycle
        #c.publish("person", "medium of present: "+str(mediumValue)+" person")
        personDetected=0
        loopCycle=0
        print("medium value: ",mediumValue)
        print("invio richiesta", x)
        thingSpeakKey= "ADD_KEY_HERE"
        url = "http://api.thingspeak.com/update?"+thingSpeakKey+"=&field1=%.2f&field2=%.2f" %(mediumValue,maximum)
        r = urequests.get(url)
        #print(r)
        #print(r.content)
        r.close()
a = kpu.deinit(task)
