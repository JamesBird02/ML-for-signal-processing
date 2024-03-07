from picamera2 import Picamera2, Preview
from gpiozero import MotionSensor
from picamera2.encoders import H264Encoder
from signal import pause
import threading
from datetime import datetime, timedelta

# Global variables
recording = False
motion_detected = False
stop_recording_timer = None
video_directory = '/home/james/'
start_time = None  # Track the start time of the recording
text_filename = None  # Filename for logging motion timestamps

camera = Picamera2()
camera.global_camera_info()

vid_config = camera.create_video_configuration(main={"size": (1920, 1080)})
camera.configure(vid_config)
encoder = H264Encoder(10000000)

pir = MotionSensor(14)

def start_recording():
    global recording, motion_detected, stop_recording_timer, start_time, text_filename
    if not recording:
        print('Recording started.')
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')
        video_filename = f'{video_directory}video_{formatted_date}.h264'
        text_filename = f'{video_directory}motion_times_{formatted_date}.txt'
        camera.start_recording(encoder, video_filename)
        recording = True
        start_time = datetime.now()  # Set the start time of the recording
    else:
        # Calculate the timestamp relative to the start of the video
        elapsed_time = datetime.now() - start_time
        # Format the elapsed time into a HH:MM:SS string
        elapsed_time_str = str(timedelta(seconds=elapsed_time.seconds))
        # Write the formatted elapsed time to the text file
        with open(text_filename, 'a') as file:
            file.write(f'Motion detected at {elapsed_time_str}\n')

    motion_detected = True
    # Cancel any pending stop recording action if motion is detected again
    if stop_recording_timer is not None:
        stop_recording_timer.cancel()
        stop_recording_timer = None
        print('Motion detected - Continuing recording.')

def stop_recording():
    global recording, motion_detected, stop_recording_timer
    if recording:
        motion_detected = False
        if stop_recording_timer is None:
            print('No motion detected - Stopping recording in 5 seconds...')
            stop_recording_timer = threading.Timer(5, delayed_stop_recording)
            stop_recording_timer.start()

def delayed_stop_recording():
    global recording, motion_detected, stop_recording_timer
    if not motion_detected:
        print('Stopping recording...')
        camera.stop_recording()
        recording = False
    stop_recording_timer = None

pir.when_motion = start_recording
pir.when_no_motion = stop_recording

pause()
