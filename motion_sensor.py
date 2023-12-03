from picamera2 import Picamera2, Preview
from gpiozero import MotionSensor
from picamera2.encoders import H264Encoder
from signal import pause
from time import sleep
import time
import libcamera
from datetime import datetime
import threading

# Global variables
recording = False
video_directory = '/home/pi/'
motion_detected = False

# Start video recording
def start_recording():
    global recording, motion_detected
    if not recording:
        print('recording')
        current_datetime = datetime.now()
        formated_date = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')
        video_filename = f'{video_directory}video_{formated_date}.h264'
        camera.start_recording(encoder, video_filename) 
        recording = True
        motion_detected = True

# stop video recording  
def stop_recording():
    global recording, motion_detected
    if recording and not motion_detected:
        print('No motion detected - Stopping recording in 5 seconds...')
        #stop recording after 5 seconds if no motion is detected
        threading.Timer(5, delayed_stop_recording).start()
        
        
# Function to stop recording after delay if no motion is detected
def delayed_stop_recording():
    global recording
    if recording and not motion_detected:
        print('Stopping recording...')
        camera.stop_recording()
        recording = False
        
def reset_motion_status():
    global motion_detected
    motion_detected = False
       
camera = Picamera2()

preview_config = camera.create_preview_configuration(main={"size": (1920, 1080)})

vid_config = camera.create_video_configuration()
camera.configure(vid_config)
encoder = H264Encoder(10000000)

pir = MotionSensor(14)

pir.when_motion = start_recording
pir.when_no_motion = stop_recording

#thread to reset motion status after a delay
def delayed_reset():
    while True:
        time.sleep(5) 
        reset_motion_status()

reset_thread = threading.Thread(target=delayed_reset)
reset_thread.daemon = True
reset_thread.start()

pause()
