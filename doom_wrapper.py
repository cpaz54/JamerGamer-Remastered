import pygame
import sys
import os
import subprocess
import time
import threading

def run_doom_game(screen):
    """Wrapper function to run the doom game and return completion status"""
    try:
        # Get the current directory and doom game path
        current_dir = os.getcwd()
        doom_dir = os.path.join(current_dir, "DOOM-style-Game-main")
        
        # Check if doom game directory exists
        if not os.path.exists(doom_dir):
            print("Doom game directory not found")
            return False
        
        # Create a communication file to signal skip
        skip_file = os.path.join(current_dir, "doom_skip_signal.txt")
        if os.path.exists(skip_file):
            os.remove(skip_file)
        
        # Run the doom game as a subprocess
        print("Starting doom game...")
        process = subprocess.Popen([sys.executable, "main.py"], 
                                 cwd=doom_dir,
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Start a thread to monitor for skip signal
        skip_detected = threading.Event()
        
        def monitor_skip():
            while process.poll() is None:  # While process is running
                if os.path.exists(skip_file):
                    print("Skip signal detected, terminating doom game...")
                    process.terminate()
                    skip_detected.set()
                    break
                time.sleep(0.1)  # Check every 100ms
        
        skip_thread = threading.Thread(target=monitor_skip)
        skip_thread.daemon = True
        skip_thread.start()
        
        # Wait for the process to complete or skip signal
        while process.poll() is None:  # While process is running
            if skip_detected.is_set():
                print("Doom game was skipped")
                return "skipped"
            time.sleep(0.1)  # Check every 100ms
        
        # Process has finished, get the output
        stdout, stderr = process.communicate()
        
        # Clean up skip file if it exists
        if os.path.exists(skip_file):
            os.remove(skip_file)
        
        # Check if skip was detected
        if skip_detected.is_set():
            print("Doom game was skipped")
            return "skipped"
        
        # Check the return code
        if process.returncode == 0:
            print("Doom game completed successfully")
            return True
        else:
            print(f"Doom game ended with error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"Error running doom game: {e}")
        return False
