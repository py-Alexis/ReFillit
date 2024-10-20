import serial
import time
import json
from datetime import datetime

# Set the serial port and baud rate (use the correct port)
SERIAL_PORT = 'COM13'  # Replace with your serial port
BAUD_RATE = 9600  # Must match the ESP32 baud rate
DB_FILE = "database.json"  # JSON file to store RFID tag data

# Initialize serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud rate.")

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

# Function to load the database from the JSON file
def load_database():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Function to save the database to the JSON file
def save_database(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

# Function to update the database with new RFID tag
def update_database(rfid_tag):
    db = load_database()

    if rfid_tag not in db:
        # If the tag is new, add placeholder values for now
        db[rfid_tag] = {
            "name": "Placeholder Name",
            "quantity": 0,  # Placeholder value
            "last_restock": "Placeholder Date"
        }
        print(f"New RFID tag {rfid_tag} added to the database.")
    else:
        # If the tag already exists, print the current data
        print(f"RFID Tag {rfid_tag} found in database: {db[rfid_tag]}")
        send_name(db[rfid_tag]["name"])

    # Save the updated database
    save_database(db)

# Function to read the RFID tag from the serial
def read_rfid():
    i = 0
    try:
        # Send command to ESP32
        print("try sent")
        ser.write("BT-Connection".encode('utf-8'))
        print("sent")
    except Exception as e:
        print(f"Error communicating with ESP32: {e}")

    try:
        while True:
            # Check if there's incoming data from the ESP32
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').rstrip()

                # Check if the response contains an RFID UID
                if response.startswith("RFID UID:"):
                    rfid_tag = response.split("RFID UID: ")[1].strip()
                    print(f"RFID Tag detected: {rfid_tag}")
                    update_database(rfid_tag)
                if response.startswith("Value:"):
                    rfid_tag = response.split("Value: ")[1].strip()
                    print(f"Value sent: {rfid_tag}")
                    send_name("Value received")
                else:
                    print(f"ESP32 Response: {response}")

            i += 1


    except KeyboardInterrupt:
        print("\nProgram terminated.")
    finally:
        ser.close()
        print("Serial connection closed.")

def send_name(command):
    try:
        # Send command to ESP32
        ser.write((command + '\n').encode('utf-8'))
        print(f"Command '{command}' sent.")

    except Exception as e:
        print(f"Error communicating with ESP32: {e}")


# Main loop to read RFID tags
if __name__ == "__main__":
    print("Waiting for RFID tags...")
    read_rfid()
