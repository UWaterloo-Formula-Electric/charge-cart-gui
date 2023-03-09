import os, datetime, serial, csv, time, random, signal, math
import io
import serial.tools.list_ports
from serial import Serial

import matplotlib.pyplot as plt

BAUD_RATE = 230400
STLINK_NAME = "STMicroelectronics STLink Virtual COM Port"
NUM_CELLS = 70

cell_data = {}
# Cell Data Dictionary:
"""
cell_data = {
    "cell_0": {
        "voltage": 3.6,
        "temp": 25,
    }
}
"""

# Populate Cell Data dictionary:
for cell_num in range(NUM_CELLS):
    cell_data.update({f"cell_{cell_num}": {"voltage": 0, "temp": 0}})

# print(cell_data["cell_0"]["voltage"])

# open the port
ports = serial.tools.list_ports.comports()
# list of all available ports
all_ports = []

for port, desc, hwid in sorted(ports):
    # print("{}: {}".format(port, desc))    # Uncomment to see all ports found
    all_ports.append("{}: {}".format(port, desc))

### connect to the port
serial_port = ""
port_found = False
for p in all_ports:
    curr = p.lower()
    if STLINK_NAME.lower() in curr:
        serial_port = p.split(':')[0]
        port_found = True
        print(f"Found STLink on {serial_port}")

        # Setup Serial Connection
        ser = Serial(serial_port, BAUD_RATE, stopbits=1, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, timeout=0)
        # not too sure what this do
        sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

if not port_found:
    print("STLink not found! Ensure it is plugged in")
    exit()


####


def main():
    fig = plt.figure()
    ax = fig.add_subplot(111)

    for i in range(10):
        # input("Press Enter to get battInfo")
        get_battInfo(ser)
        print("Got battInfo", i+1)
        for cell_name in cell_data.keys():
            plt.scatter(i, cell_data[cell_name]["voltage"])
        plt.pause(0.05)

        print(cell_data)
        time.sleep(2)


"""
-----       Serial Parsing Code     -----
"""


# Get battInfo and parse important information
def get_battInfo(sio):
    # sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    sio.write("battInfo\n".encode())
    # sio.flush()
    time.sleep(0.2)  # Wait for response
    raw_data = sio.read(sio.inWaiting())
    data = raw_data.decode()

    if not data:
        print("ERROR: NO DATA RECEIVED FROM BATTINFO CMD")
        return

    else:

        # print(data)

        ###     PARSE DATA FROM BATTINFO    ###
        data = data.split("Index	Cell Voltage(V)	Temp Channel(degC)")[1].split("bmu >")[0]
        # print(cell_data)
        for line in data.split("\n"):
            parsed = line.strip().split("\t")
            if len(parsed) > 1:
                try:
                    cell_num = int(parsed[0])
                    cell_voltage = parsed[1]
                    cell_temp = parsed[2]

                    '''
                    [[cell_num,cell_voltage, cell_temp], 
                     [cell_num,cell_voltage, cell_temp],
                     [cell_num,cell_voltage, cell_temp]]
                    '''

                    cell_key = f"cell_{cell_num}"

                    # Populate dictionary entry
                    if cell_key in cell_data.keys():
                        cell_data[cell_key]["voltage"] = cell_voltage
                        cell_data[cell_key]["temp"] = cell_temp
                except Exception as e:      # TODO: Remove this once all parsing bugs are fixed
                    print("Got Exception", e)
                    print(parsed)
                    print(cell_data)

                # print(f"{cell_num} {cell_voltage} {cell_temp}")



if __name__ == "__main__":
    main()
