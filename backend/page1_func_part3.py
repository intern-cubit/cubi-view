import cv2
import pyaudio
import wave
import threading
import time
import os
from datetime import datetime
import getpass
from credentials import REPORT_DIR
from write_report import write_report

# Configuration
CAPTURE_DURATION = 5  # Duration in seconds
FRAME_RATE = 20  # Frames per second for video
AUDIO_RATE = 44100  # Audio sample rate
AUDIO_CHANNELS = 2  # Stereo
AUDIO_FORMAT = pyaudio.paInt16  # 16-bit audio

user = getpass.getuser()
date_folder = datetime.now().strftime("%d-%m-%Y")
OUTPUT_FOLDER = os.path.join(REPORT_DIR, date_folder, user + "\\captured_clips")
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global variables for threading and scheduling
audio_thread = None
video_thread = None
audio_stop_event = threading.Event()
video_stop_event = threading.Event()

def capture_audio():
    """Capture audio for a specified duration and save to a WAV file."""
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=AUDIO_FORMAT, channels=AUDIO_CHANNELS, rate=AUDIO_RATE, input=True, frames_per_buffer=1024)
        frames = []
        
        write_report(REPORT_DIR, "capture_report", "Recording audio...")
        print("Recording audio...")
        for _ in range(0, int(AUDIO_RATE / 1024 * CAPTURE_DURATION)):
            if audio_stop_event.is_set():
                break
            data = stream.read(1024)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        if frames:  # Save only if there is data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = os.path.join(OUTPUT_FOLDER, f"audio_{timestamp}.wav")
            wf = wave.open(audio_file, 'wb')
            wf.setnchannels(AUDIO_CHANNELS)
            wf.setsampwidth(p.get_sample_size(AUDIO_FORMAT))
            wf.setframerate(AUDIO_RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            write_report(REPORT_DIR, "capture_report", f"Audio saved: {audio_file}")
            print(f"Audio saved: {audio_file}")
    except Exception as e:
        write_report(REPORT_DIR, "capture_report", f"Error capturing audio: {e}")
        print(f"Error capturing audio: {e}")

def capture_video():
    """Capture video for a specified duration and save to an MP4 file."""
    try:
        cap = cv2.VideoCapture(0)  # 0 is the default webcam
        if not cap.isOpened():
            raise Exception("Could not open webcam.")
        
        # Define video writer
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_file = os.path.join(OUTPUT_FOLDER, f"video_{timestamp}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_file, fourcc, FRAME_RATE, (640, 480))
        
        write_report(REPORT_DIR, "capture_report", "Recording video...")
        print("Recording video...")
        start_time = time.time()
        while (time.time() - start_time) < CAPTURE_DURATION:
            if video_stop_event.is_set():
                break
            ret, frame = cap.read()
            if not ret:
                raise Exception("Failed to capture video frame.")
            out.write(frame)
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        if (time.time() - start_time) > 0:  # Save only if some video was captured
            write_report(REPORT_DIR, "capture_report", f"Video saved: {video_file}")
            print(f"Video saved: {video_file}")
    except Exception as e:
        write_report(REPORT_DIR, "capture_report", f"Error capturing video: {e}")
        print(f"Error capturing video: {e}")

def audio_scheduler():
    """Run audio capture every hour until stopped."""
    while not audio_stop_event.is_set():
        capture_audio()
        # Sleep for 1 hour (3600 seconds), checking for stop event every second
        for _ in range(3600):
            if audio_stop_event.is_set():
                break
            time.sleep(1)

def video_scheduler():
    """Run video capture every hour until stopped."""
    while not video_stop_event.is_set():
        capture_video()
        # Sleep for 1 hour (3600 seconds), checking for stop event every second
        for _ in range(3600):
            if video_stop_event.is_set():
                break
            time.sleep(1)

def enable_audio_capture():
    """Start capturing audio on a scheduler in a separate thread."""
    global audio_thread, audio_stop_event
    if audio_thread and audio_thread.is_alive():
        write_report(REPORT_DIR, "capture_report", "Audio capture is already running.")
        print("Audio capture is already running.")
        return
    
    audio_stop_event.clear()  # Reset the stop event
    audio_thread = threading.Thread(target=audio_scheduler)
    audio_thread.start()
    write_report(REPORT_DIR, "capture_report", "Audio capture scheduler enabled and running in a thread.")
    print("Audio capture scheduler enabled and running in a thread.")

def disable_audio_capture():
    """Stop the audio capture scheduler thread."""
    global audio_thread, audio_stop_event
    if not audio_thread or not audio_thread.is_alive():
        write_report(REPORT_DIR, "capture_report", "Audio capture is not running.")
        print("Audio capture is not running.")
        return
    
    audio_stop_event.set()  # Signal the thread to stop
    audio_thread.join()  # Wait for the thread to finish
    write_report(REPORT_DIR, "capture_report", "Audio capture scheduler disabled.")
    print("Audio capture scheduler disabled.")

def enable_video_capture():
    """Start capturing video on a scheduler in a separate thread."""
    global video_thread, video_stop_event
    if video_thread and video_thread.is_alive():
        write_report(REPORT_DIR, "capture_report", "Video capture is already running.")
        print("Video capture is already running.")
        return
    
    video_stop_event.clear()  # Reset the stop event
    video_thread = threading.Thread(target=video_scheduler)
    video_thread.start()
    write_report(REPORT_DIR, "capture_report", "Video capture scheduler enabled and running in a thread.")
    print("Video capture scheduler enabled and running in a thread.")

def disable_video_capture():
    """Stop the video capture scheduler thread."""
    global video_thread, video_stop_event
    if not video_thread or not video_thread.is_alive():
        write_report(REPORT_DIR, "capture_report", "Video capture is not running.")
        print("Video capture is not running.")
        return
    
    video_stop_event.set()  # Signal the thread to stop
    video_thread.join()  # Wait for the thread to finish
    write_report(REPORT_DIR, "capture_report", "Video capture scheduler disabled.")
    print("Video capture scheduler disabled.")

# Example usage with your schedule function (for reference)
#if __name__ == "__main__":
#    # Simulate your schedule function calling enable/disable
#    print("Simulating schedule function...")
#    enable_audio_capture()
#    enable_video_capture()
#    time.sleep(20)  # Wait for the first capture to complete and observe
#    disable_audio_capture()
#    disable_video_capture()
