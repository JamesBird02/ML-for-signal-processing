from gpiozero import MotionSensor
from picamera import PiCamera
from time import sleep
from signal import pause

#declare components
pir = MotionSensor(4)
camera = PiCamera()


camera.resolution = (1080, 1920)

recording = False

video_directory = '/home/pi/Desktop/'

#start video recording
def start_recording():
    global recording
    if not recording:
        video_filename = f'{video_directory}video.h264'
        camera.start_recording(video_filename)
        recording = True

#stop video recording
def stop_recording():
    global recording
    if recording:
        sleep(5) #wait 5 seconds after no movement to stop recording
        camera.stop_recording()
        recording = False

#motion is detected, run start function
pir.when_motion = start_recording

# no motion is detected, run stop function
pir.when_no_motion = stop_recording

pause()
