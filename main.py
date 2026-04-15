import json
import os
import subprocess
import serial
import time


ARDUINO = True
DEBUG = True

STORAGE_FILE = "data.json"

STATE = "r"

def read_NFC():
    if ARDUINO:
        # 1. Open the port with a timeout to prevent infinite hanging
        try:
            ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
            
            # 2. CRITICAL: Wait for Arduino to reboot after serial connection
            time.sleep(2) 
            
            # 3. Clear the buffer of any "junk" data from bootup
            ser.reset_input_buffer()

            print("Place the miniature on the stand...")

            while True:
                if ser.in_waiting > 0:
                    # 4. Read an entire line until \n
                    line = ser.readline() 
                    
                    # Convert bytes to string and strip whitespace/newlines
                    uid = line.decode('utf-8').strip()
                    
                    if uid:
                        if DEBUG:
                            print(f"UID read from arduino: {uid}")
                        return uid
                
                # Small sleep to prevent 100% CPU usage in the loop
                time.sleep(0.1)

        except Exception as e:
            print(f"Serial Error: {e}")
            return None
    else:
        uid = input("TEST uid = :")
        return uid




def find_filepath(uid):
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            data = json.load(f)
    else:
        return None

    # Iterate through every path and its list of UIDs
    for filepath, uid_list in data.items():
        if uid in uid_list:
            return filepath  # Return the first path that matches
            
    return None # Return None if the UID isn't found anywhere



def display(uid, current_display):
    if current_display is not None:
        try:
            current_display.terminate()
        except Exception as e:
            print(f"Error found when loading new PDF: {e}")
        

    file_path = find_filepath(uid)

    if DEBUG:
        print(f"File Located: '{file_path}' \nTrying to display file...")
    display = subprocess.Popen(["evince", "-s", file_path])
    return display




def request_character():
    """Function to find the character that the person is trying to map the UID to"""

    return input("GIVE ME PATH ID :")




def alias(uid, character_id):
    # Map the UID to the character file path
    """Use JSON to associate the UID to the ID/filepath of the character"""
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            data = json.load(f)
    else:
        if DEBUG:
            print(f"File {STORAGE_FILE} not found")
        data = {}
    
    if character_id not in data:
        data[character_id] = []

    if uid not in data[character_id]:
        data[character_id].append(uid)
    
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return




def main():    
    current_display = None
    while True:
        if STATE == "r":
            uid = read_NFC()
            current_display = display(uid, current_display)
        elif STATE == "w":

            uid = read_NFC()
            character_id = request_character()
            alias(uid, character_id) #This function assumes that the character ID is the character file path


if __name__ == "__main__":
    main()

