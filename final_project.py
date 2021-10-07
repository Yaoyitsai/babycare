import picamera
import time
from enum import Enum
import RPi.GPIO as GPIO
import spidev
import struct
import logging
import threading
import math
import numpy as np
import statistics
import os
from scipy.io.wavfile import read
from aubio import source , pitch
import signal
import subprocess
import pandas as pd
from pydub import AudioSegment
import wave
import pyaudio
from scipy.io import wavfile


spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0b11
spi.max_speed_hz = 2000000

def writeByte(reg, val):
    spi.xfer2([reg, val])
def writeRegBytes(reg, vals):
    packet = [0]*(len(vals) +1)
    packet[0] = reg | 0x40
    packet[1:(len(vals)+1)] = vals
    spi.xfer2(packet)
def readByte(reg):
    packet = [0] *2
    packet[0] = reg | 0x80
    reply = spi.xfer2(packet)
    return reply[1]
deviceID = readByte(0x00)
print("ID: %x" % deviceID)
# Select power control register, 0x2D(45)
# 0x08(08) Auto Sleep disable
writeByte(0x2D, 0x00)
time.sleep(0.1)
writeByte(0x2D, 0x08)

# Select data format register, 0x31(49)
# 0x08(08) Self test disabled, 4-wire interface
# Full resolution, Range = +/-2g
writeByte(0x31, 0x08)
time.sleep(0.5)

import RPi.GPIO as GPIO

LED_PIN = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

pwm = GPIO.PWM(LED_PIN, 100)
pwm.start(0)

import sys
import cv2
import pyimgur
from gtts import gTTS
from pygame import mixer

camera = picamera.PiCamera()
#linebox test1
from flask import Flask
app = Flask(__name__)

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

line_bot_api = LineBotApi('agPGreeChJfjVIbWULg6NVWcFdR09vAyJ/x8RVEKuMiDBF30HKuqcyXGft7/LjVS7RcuUJ9U6qrb4EgvhdItnQkOhD6dl8sloEnNZcAgp8cPbBRPUmrQTmXn7j9+i0Qx31nszfOsH6KHM2Oxw7yzjQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('0b5ef7c9a1682fb9b9d0cc098d80afb4')
to = "Ue0d381abcdec51fb163cd349b2d07447"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

CLIENT_ID = "d9732505f680705"
title = "Upload with PyImgur"
im = pyimgur.Imgur(CLIENT_ID)

#for cry
win_s = 4096
hop_s = 512
downsample = 1
samplerate = 44100 // downsample

tolerance = 0.8


deltatime = time.time()


    
pitch_o = pitch("yin", win_s, hop_s, samplerate)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)
#for cry

#cry_flag = False


def thread_cry():
    
    
    while(True):
        
        proc_args = ['arecord', '-D' , 'plughw:2' , '-c1' , '-r' , '44100' , '-f' , 'S32_LE' , '-t' , 'wav' , '-V' , 'mono' , '-v' , 'subprocess1.wav']
        rec_proc = subprocess.Popen(proc_args, shell=False, preexec_fn=os.setsid)
        print("startRecordingArecord()> rec_proc pid= " + str(rec_proc.pid))
        print("startRecordingArecord()> recording started")

        time.sleep(3)
        os.killpg(rec_proc.pid, signal.SIGTERM)
        rec_proc.terminate()
        rec_proc = None
        print("stopRecordingArecord()> Recording stopped")
    
        #frequency_func 
        s = source('subprocess1.wav', samplerate, hop_s)
        
        pitches = []
        confidences = []
        cry_fre = []
        total_frames = 0
        
        while True:
            samples, read = s()
            pitch = pitch_o(samples)[0]
            pitches += [pitch]
            confidence = pitch_o.get_confidence()
            confidences += [confidence]
            total_frames += read
            if read < hop_s: break
            print("Average frequency = " + str(np.array(pitches).mean()) + " hz")
            cry_fre += [np.array(pitches).mean()]
            #if np.array(pitches).mean() > 80 :
                    #sent 哭阿哭阿
                #print("哭阿")
        #print cry sound
        if np.array(cry_fre).mean() > 80:
            print('哭阿哭阿')
            line_bot_api.push_message(to, TextSendMessage(text='your baby is crying!!!!'))
            subprocess.call(["omxplayer","-o","local","-p","/home/pi/Baby-music-box.mp3"])
            #time.sleep(15)
            
            print("stopplaying")
            #line_bot_api.reply_message(event.reply_token,TextSendMessage(text='!!!'))
            #mutex.acquire()
            #cry_flag = True
            #mutex.release()
        else :
            print('no cry')
        
   



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    mtext = event.message.text

    if mtext == 'photo':
        try:
            print('0.0')
            
            time.sleep(2)
            camera.capture('thomas.jpg')
            
            PATH = '/home/pi/linetest1/thomas.jpg'
            
            uploaded_image = im.upload_image(PATH, title=title)
            print(uploaded_image.title)
            print(uploaded_image.link)
            print(uploaded_image.type)
            
            image_url = uploaded_image.link
            
          
            message = ImageSendMessage(
                original_content_url = image_url,
                preview_image_url = image_url
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='errror!!!'))
    elif mtext == 'bright':
        try:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="Set brightness (0~100):"))
        except :
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='errror!!!'))
    if int(mtext) <= 100 and int(mtext) >= 0 :
        print(mtext)
        try:
            pwm.ChangeDutyCycle(int(mtext))
        except :
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='errror!!!'))

def thread_line():
    app.run()
    

def thread_turn():
    try:
        while True:
            # Read data back from 0x32(50), 2 bytes
            accel = {'x' : 0, 'y' : 0, 'z': 0}
            # X-Axis LSB, X-Axis MSB
            data0 = readByte(0x32)
            data1 = readByte(0x33)
            # Convert the data to 10-bits
            xAccl = struct.unpack('<h', bytes([data0, data1]))[0]
            accel['x'] = xAccl / 256
            
            # Read data back from 0x34(52), 2 bytes
            # Y-Axis LSB, Y-Axis MSB
            data0 = readByte(0x34)
            data1 = readByte(0x35)
            # Convert the data to 10-bits
            yAccl = struct.unpack('<h', bytes([data0, data1]))[0]
            accel['y'] = yAccl / 256
            
            # Read data back from 0x36(54), 2 bytes
            # Z-Axis LSB, Z-Axis MSB
            data0 = readByte(0x36)
            data1 = readByte(0x37)
            # Convert the data to 10-bits
            zAccl = struct.unpack('<h', bytes([data0, data1]))[0]
            accel['z'] = zAccl / 256
            
            # Output data to screen
            #print ("Ax Ay Az: %.3f %.3f %.3f" % (accel['x'], accel['y'], accel['z']))
            
            if(accel['z'] < 0.4 ):
                print("turn")
                print('0.0')
                
                time.sleep(2)
                camera.capture('thomas.jpg')
                
                PATH = '/home/pi/linetest1/thomas.jpg'
                
                uploaded_image = im.upload_image(PATH, title=title)
                print(uploaded_image.title)
                print(uploaded_image.link)
                print(uploaded_image.type)
                
                image_url = uploaded_image.link
            
                line_bot_api.push_message(to, TextSendMessage(text='your baby has turned!!!!'))
                line_bot_api.push_message(to, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
            #else: print("error")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Ctrl+C Break")
        spi.close()


if __name__ == '__main__':
    threads = list()
    for index in range(3):
        logging.info("Main : create and start thread %d.", index)
        if index == 0:
            x = threading.Thread(target=thread_line, args=())
        if index == 1:
            x = threading.Thread(target=thread_cry, args=())
        if index == 2:
            x = threading.Thread(target = thread_turn,args=())
        threads.append(x)
        x.start()



<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><title>

</title></head>
<body>
    <form method="post" action="./File_DownLoad_Wk_zip.aspx?File_name=threadtest.py&amp;type=3&amp;id=3196561" id="form1">
<div class="aspNetHidden">
<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUKLTEzNDM3NzkxOWRkwneTr34MFXJYUKyKKda+DU4gQVM=" />
</div>

<div class="aspNetHidden">

	<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="629601C3" />
</div>
    <div>
    
    </div>
    </form>
</body>
</html>
