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
        print(f"Skip file path: {skip_file}")
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
                    try:
                        process.terminate()
                        # Give it a moment to terminate
                        time.sleep(0.5)
                        if process.poll() is None:
                            process.kill()  # Force kill if terminate didn't work
                    except:
                        pass
                    skip_detected.set()
                    break
                time.sleep(0.05)  # Check every 50ms for faster response
        
        skip_thread = threading.Thread(target=monitor_skip)
        skip_thread.daemon = True
        skip_thread.start()
        
        # Wait for the process to complete or skip signal with timeout
        timeout_counter = 0
        max_timeout = 300  # 15 seconds timeout (300 * 0.05)
        
        while process.poll() is None:  # While process is running
            if skip_detected.is_set():
                print("Doom game was skipped")
                return "skipped"
            
            timeout_counter += 1
            if timeout_counter > max_timeout:
                print("Doom game timeout - force terminating")
                try:
                    process.terminate()
                    time.sleep(0.5)
                    if process.poll() is None:
                        process.kill()
                except:
                    pass
                return False
                
            time.sleep(0.05)  # Check every 50ms for faster response
        
        # Process has finished, get the output
        stdout, stderr = process.communicate()
        
        # Clean up skip file if it exists
        if os.path.exists(skip_file):
            os.remove(skip_file)
        
        # Check if skip was detected
        if skip_detected.is_set():
            print("Doom game was skipped")
            return "skipped"
        
        # Check the return code and output
        print(f"Process return code: {process.returncode}")
        print(f"STDOUT: {stdout.decode() if stdout else 'None'}")
        print(f"STDERR: {stderr.decode() if stderr else 'None'}")
        
        if process.returncode == 0:
            print("Doom game completed successfully")
            # Check if there's any output that indicates victory
            output_text = stdout.decode() if stdout else ""
            if "victory" in output_text.lower() or "win" in output_text.lower():
                return True
            else:
                return True  # Still return True for successful completion
        else:
            print(f"Doom game ended with error code {process.returncode}")
            if stderr:
                print(f"Error details: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"Error running doom game: {e}")
        return False
