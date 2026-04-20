# Pi_CAN_Comm.py
# This code runs on the Raspberry Pi to communicate with the Arduino (ECU) via CAN bus.
# It receives sensor data from the ECU and can send commands back.

import can          # Python-CAN library for CAN bus communication
import time         # For time-related functions like sleep
import struct       # For packing and unpacking binary data
import os           # For interacting with the operating system (e.g., checking CAN interface status, environment variables)

# --- CAN Message Identifiers (IDs) ---
# These define unique IDs for different types of data or commands on the CAN bus.
# IMPORTANT: These IDs MUST match the ones defined in the Arduino (ECU) code.
CAN_ID_THROTTLE = 0x100 # CAN ID for Throttle Position Sensor data
CAN_ID_LAMBDA   = 0x101 # CAN ID for Lambda Sensor data
CAN_ID_RPM      = 0x102 # CAN ID for Crankshaft Position Sensor (RPM) data
CAN_ID_GEAR     = 0x103 # CAN ID for Gear Positioning Sensor data
CAN_ID_COOLANT  = 0x104 # CAN ID for Coolant Sensor data
CAN_ID_COMMAND  = 0x200 # CAN ID for commands sent from Pi to ECU

# Sensor data storage on Pi (to hold the latest received values)
sensor_data = {
    "throttle": 0,   # 0-100%
    "lambda": 0.0,   # 0.80-1.20 AFR
    "rpm": 0,        # 0-8000 RPM
    "gear": 0,       # 0 (Neutral) to 5
    "coolant": 0     # 0-120 Celsius
}

# --- Function to Process and Store Received Sensor Data ---
def process_received_sensor_data(msg):
    """
    Processes a received CAN message, updates the global sensor_data dictionary,
    and returns True if the message was successfully processed, False otherwise.
    """
    try:
        if msg.arbitration_id == CAN_ID_THROTTLE and len(msg.data) == 2:
            sensor_data["throttle"] = struct.unpack('>H', msg.data)[0]
        elif msg.arbitration_id == CAN_ID_LAMBDA and len(msg.data) == 2:
            lambda_int = struct.unpack('>H', msg.data)[0]
            sensor_data["lambda"] = lambda_int / 100.0 # Convert back to float
        elif msg.arbitration_id == CAN_ID_RPM and len(msg.data) == 2:
            sensor_data["rpm"] = struct.unpack('>H', msg.data)[0]
        elif msg.arbitration_id == CAN_ID_GEAR and len(msg.data) == 1:
            sensor_data["gear"] = msg.data[0]
        elif msg.arbitration_id == CAN_ID_COOLANT and len(msg.data) == 2:
            sensor_data["coolant"] = struct.unpack('>H', msg.data)[0]
        elif msg.arbitration_id == CAN_ID_COMMAND:
            if len(msg.data) >= 1:
                command_code = msg.data[0]
                print(f"Received Command from ECU: 0x{command_code:02x}")
            else:
                print(f"ERROR: Received command message with insufficient data length ({len(msg.data)} bytes).")
            return True # Command messages are also processed
        else:
            print(f"WARNING: Received unknown or malformed CAN message: ID=0x{msg.arbitration_id:03x}, DLC={msg.dlc}, Data={msg.data.hex()}")
            return False
        return True # Message successfully processed
    except struct.error as e:
        print(f"ERROR: Struct unpacking error for ID 0x{msg.arbitration_id:03x}: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error processing CAN message: {e}")
        return False

# --- Function to Display Current Sensor Data ---
def display_sensor_data():
    """
    Displays the current sensor data stored in the global sensor_data dictionary.
    """
    gear_str = "Unknown"
    if sensor_data["gear"] == 0: gear_str = "Neutral"
    elif sensor_data["gear"] == 1: gear_str = "1st"
    elif sensor_data["gear"] == 2: gear_str = "2nd"
    elif sensor_data["gear"] == 3: gear_str = "3rd"
    elif sensor_data["gear"] == 4: gear_str = "4th"
    elif sensor_data["gear"] == 5: gear_str = "5th"

    print("\n--- Current Sensor Readings ---")
    print(f"Throttle Position: {sensor_data['throttle']:.1f} %")
    print(f"Lambda Value: {sensor_data['lambda']:.2f} AFR")
    print(f"Engine RPM: {sensor_data['rpm']} RPM")
    print(f"Gear Position: {gear_str}")
    print(f"Coolant Temperature: {sensor_data['coolant']:.1f} °C")
    print("-----------------------------")

# --- Function to Send Data (Commands from Pi to ECU) ---
def send_command_to_ecu(bus, command_code):
    """
    Constructs and sends a CAN frame with a specified command code to the ECU.
    """
    msg = can.Message(
        arbitration_id=CAN_ID_COMMAND, # Set the CAN ID for commands
        data=[command_code],           # Place the command code in the data payload
        is_extended_id=False,          # Use standard 11-bit CAN ID
        dlc=1                          # Data Length Code: 1 byte for the command code
    )

    try:
        bus.send(msg) # Send the CAN message
        print(f"INFO: Sent command 0x{command_code:02x} to ECU.")
    except can.CanError as e:
        print(f"ERROR: CAN Send error: {e}") # Print error if sending fails

# --- Function to Adjust Data for Environmental Factors ---
def adjust_data_for_environment():
    """
    THIS SECTION REPRESENTS REAL-TIME ADJUSTMENTS TO ACQUIRED SENSOR DATA
    BASED ON ENVIRONMENTAL FACTORS OR CALIBRATION. THESE ADJUSTMENTS ARE
    TYPICALLY APPLIED AFTER RECEIVING THE RAW DATA FROM THE ECU TO REFINE
    ITS ACCURACY BASED ON EXTERNAL CONDITIONS.

    FOR ILLUSTRATIVE PURPOSES, THIS FUNCTION SHOWS HOW YOU MIGHT ACCESS
    ENVIRONMENT VARIABLES (E.G., SET IN YOUR SHELL OR SYSTEMD SERVICE)
    TO APPLY CORRECTIONS. IN A REAL SYSTEM, THESE FACTORS MIGHT COME FROM
    ADDITIONAL SENSORS ON THE PI OR A MORE SOPHISTICATED CALIBRATION MODEL.
    """
    # EXAMPLE: APPLYING A TEMPERATURE CORRECTION TO COOLANT SENSOR READING.
    # ASSUME 'AMBIENT_TEMP_C' IS AN ENVIRONMENT VARIABLE SET ON THE PI.
    # e.g., export AMBIENT_TEMP_C="25.5"
    try:
        ambient_temp_str = os.getenv('AMBIENT_TEMP_C', '20.0')
        ambient_temp_pi = float(ambient_temp_str)
        if ambient_temp_pi < 5.0:
            sensor_data['coolant'] += 2 # Adjust for very cold conditions
            print(f"ENVIRONMENTAL ADJUSTMENT: Coolant +2°C due to low ambient temp ({ambient_temp_pi}°C)")
        elif ambient_temp_pi > 40.0:
            sensor_data['coolant'] -= 1 # Adjust for very hot conditions
            print(f"ENVIRONMENTAL ADJUSTMENT: Coolant -1°C due to high ambient temp ({ambient_temp_pi}°C)")
    except ValueError:
        print("WARNING: AMBIENT_TEMP_C environment variable is not a valid number.")

    # EXAMPLE: ADJUSTING RPM BASED ON BAROMETRIC PRESSURE.
    # ASSUME 'BAROMETRIC_PRESSURE_PA' IS AN ENVIRONMENT VARIABLE.
    # e.g., export BAROMETRIC_PRESSURE_PA="98000.0"
    try:
        barometric_pressure_str = os.getenv('BAROMETRIC_PRESSURE_PA', '101325.0')
        barometric_pressure_pa = float(barometric_pressure_str)
        if barometric_pressure_pa < 95000: # Below 950 hPa (approx. 950 mbar)
            sensor_data['rpm'] = int(sensor_data['rpm'] * 0.98) # Reduce RPM for lower pressure/higher altitude
            print(f"ENVIRONMENTAL ADJUSTMENT: RPM adjusted by -2% due to low barometric pressure ({barometric_pressure_pa} Pa)")
        elif barometric_pressure_pa > 105000: # Above 1050 hPa
            sensor_data['rpm'] = int(sensor_data['rpm'] * 1.01) # Increase RPM for higher pressure
            print(f"ENVIRONMENTAL ADJUSTMENT: RPM adjusted by +1% due to high barometric pressure ({barometric_pressure_pa} Pa)")
    except ValueError:
        print("WARNING: BAROMETRIC_PRESSURE_PA environment variable is not a valid number.")

    # NOTE: THESE ADJUSTMENTS ARE SIMPLISTIC AND FOR ILLUSTRATIVE PURPOSES.
    # REAL-WORLD APPLICATIONS WOULD USE MORE SOPHISTICATED MODELS,
    # POTENTIALLY INVOLVING MACHINE LEARNING, DETAILED PHYSICAL MODELS,
    # OR LOOKUP TABLES TO ENSURE ACCURATE REAL-TIME DATA CORRECTION.
    # THE KEY IS TO HAVE A MECHANISM TO DYNAMICALLY MODIFY SENSOR OUTPUT
    # BASED ON EXTERNAL CONDITIONS TO REFLECT TRUE OPERATIONAL STATE.

# --- Main Loop for Continuous Communication ---
if __name__ == "__main__":
    print("Starting Raspberry Pi CAN communication loop. Press Ctrl+C to exit.")

    # Check if the CAN interface 'can0' is up.
    print("Checking CAN interface status...")
    if not os.path.exists('/sys/class/net/can0'):
        print("Error: CAN interface 'can0' not found.")
        print("Please ensure it's configured and up (e.g., sudo ip link set can0 up type can bitrate 500000)")
        exit(1)

    # Initialize the CAN bus
    bus = None
    try:
        bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=500000)
        print("CAN bus communication initialized on can0. Waiting for data from ECU...")
    except can.CanError as e:
        print(f"Error initializing CAN bus: {e}")
        print("Please ensure the CAN interface 'can0' is configured and up (e.g., sudo ip link set can0 up type can bitrate 500000)")
        exit(1)

    last_command_send_time = time.time() # To control command sending frequency
    command_send_interval = 5            # Send a command every 5 seconds
    last_display_time = time.time()      # To control display frequency
    display_interval = 1                 # Display data every 1 second

    try:
        while True:
            # Receive data from ECU (non-blocking)
            msg = bus.recv(timeout=0.01) # Small timeout to allow other tasks in the loop
            if msg:
                if process_received_sensor_data(msg):
                    # Apply environment variable adjustments after successfully receiving a sensor message
                    # Note: Adjustments are applied to the 'sensor_data' dictionary directly.
                    adjust_data_for_environment()

            # Display sensor data periodically
            current_time = time.time()
            if current_time - last_display_time >= display_interval:
                display_sensor_data()
                last_display_time = current_time

            # Example of sending a command back to ECU (e.g., every 5 seconds)
            if current_time - last_command_send_time >= command_send_interval:
                send_command_to_ecu(bus, 0x01) # Example command: Request ECU to toggle a diagnostic LED
                last_command_send_time = current_time

            time.sleep(0.001) # Very small delay to prevent high CPU usage
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Stopping CAN communication.")
    except Exception as e:
        print(f"An unexpected error occurred in the main loop: {e}")
    finally:
        # Ensure the CAN bus is properly shut down on exit
        if bus:
            bus.shutdown()
            print("CAN Bus shut down.")
