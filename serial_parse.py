import os, datetime, serial, csv, time, random, signal, math
import io
import serial.tools.list_ports
from serial import Serial

import matplotlib.pyplot as plt



class SerialConnect(object):

    BAUD_RATE = 230400
    STLINK_NAME = "STMicroelectronics STLink Virtual COM Port"
    NUM_CELLS = 70


    def __init__(self):
        self.ser = None
        self.cell_data = {}
        self.all_ports = []
        self.sio = None

    # Cell Data Dictionary:
    """
    cell_data = {
        "cell_0": {
            "voltage": 3.6,
            "temp": 25,
        }
    }
    """

    def port_setup(self):
        # Populate Cell Data dictionary:
        for cell_num in range(self.NUM_CELLS):
            self.cell_data.update({f"cell_{cell_num}": {"voltage": 0, "temp": 0}})

        # print(cell_data["cell_0"]["voltage"])

        # open the port
        ports = serial.tools.list_ports.comports()
        # list of all available ports

        message = ""

        for port, desc, hwid in sorted(ports):
            # print("{}: {}".format(port, desc))    # Uncomment to see all ports found
            self.all_ports.append("{}: {}".format(port, desc))

        ### connect to the port
        serial_port = ""
        port_found = False

        for p in self.all_ports:
            curr = p.lower()
            if self.STLINK_NAME.lower() in curr:
                serial_port = p.split(':')[0]
                port_found = True
                message  = f"Found STLink on {serial_port}"
                print(message)

                # Setup Serial Connection
                self.ser = Serial(serial_port, self.BAUD_RATE, stopbits=1, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS,
                             timeout=0)
                # Not so sure what this does
                self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))

        if not port_found:
            print("STLink not found! Ensure it is plugged in")
            # insert a message to the log box: not connected

            # not too sure what exit does here
            # exit()
            return port_found

        return port_found


    ####


    def execute(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for i in range(10):
            # get battInfo commend
            # input("Press Enter to get battInfo")
            self.get_battInfo(self.ser)
            print("Got battInfo", i+1)
            for cell_name in self.cell_data.keys():
                plt.scatter(i, self.cell_data[cell_name]["voltage"])
            plt.pause(0.05)

            print(self.cell_data)
            time.sleep(2)


    """
    -----       Serial Parsing Code     -----
    
    
    """


    # Get battInfo and parse important information
    def get_battInfo(self):
        # sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        self.ser.write("battInfo\n".encode())
        # sio.flush()
        time.sleep(0.2)  # Wait for response
        raw_data = self.ser.read(self.ser.inWaiting())
        data = raw_data.decode()

        if not data:
            print("ERROR: NO DATA RECEIVED FROM BATTINFO CMD")
            return "error"
        

        else:

            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(data)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

            ###     PARSE DATA FROM BATTINFO    ###
            data = data.split("Index	Cell Voltage(V)	Temp Channel(degC)")[1].split("bmu >")[0]
            # print(cell_data)
            for line in data.split("\n"):
                parsed = line.strip().split("\t")
                if len(parsed) > 1:
                    try:
                        # data Cell     Voltage     Temp
                        cell_num = int(parsed[0])
                        cell_voltage = parsed[1]
                        cell_temp = parsed[2]


                        # 70x3 array
                        '''
                        [[cell_num,cell_voltage, cell_temp], 
                         [cell_num,cell_voltage, cell_temp],
                         [cell_num,cell_voltage, cell_temp]]
                        '''


                        cell_key = f"cell_{cell_num}"

                        # Populate dictionary entry
                        if cell_key in self.cell_data.keys():
                            self.cell_data[cell_key]["voltage"] = cell_voltage
                            self.cell_data[cell_key]["temp"] = cell_temp

                    except Exception as e:      # TODO: Remove this once all parsing bugs are fixed
                        print("Got Exception", e)
                        print(parsed)
                        print(self.cell_data)

                    # print(f"{cell_num} {cell_voltage} {cell_temp}")
            
            return data

    def getSoC(self):
        soc = self.sendRequest("balanceCell")
        return float(soc)

    def balancePack(self):
        self.sendRequest("balanceCell")

    # sending Max current request
    def setCurrent(self):
        self.sendRequest("maxChargeCurrent")

    # Is this the right command?
    def getCurrent(self):
        data = self.sendRequest("printHVMeasurements")
        return data

    def getVoltage(self):
        data = self.sendRequest("printHVMeasurements")
        return data



    def startCharging(self, current):
        self.sendRequest(current)


    def StopCharging(self):
        message = self.sendRequest("stopCharge")
        return message


    def sendRequest(self, command):
        command = command + "\n"
        self.sio.write(command.encode())
        # sio.flush()
        time.sleep(0.2)  # Wait for response
        raw_data = self.sio.read(self.sio.inWaiting())
        return raw_data.decode()


    def get_cell_data(self):
        return self.cell_data

    def get_port_name(self):
        return self.all_ports

    def get_cellNum(self):
        return self.NUM_CELLS



#
# if __name__ == "__main__":
#     main()
