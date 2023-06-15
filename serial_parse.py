import os, datetime, serial, csv, time, random, signal, math
import io
import serial.tools.list_ports
from serial import Serial
import matplotlib.pyplot as plt
from document.CommandOutput import BatteryInfoString


class SerialConnect(object):
    BAUD_RATE = 230400
    STLINK_NAME = "STMicroelectronics STLink Virtual COM Port"
    NUM_CELLS = 70

    def __init__(self):
        self.ser = None
        self.cell_data = {}
        self.all_ports = []
        self.sio = None
        self.isTesting = True
        self.isConnected = False

    def port_setup(self):
        # Return bool True/False
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
            # Always pass for now, add dropdown in GUI for selecting COM port later
            if True:  # or self.STLINK_NAME.lower() in curr:
                serial_port = p.split(':')[0]
                port_found = True
                message = f"Found STLink on {serial_port}"
                self.isConnected=True
                print(message)

                # Setup Serial Connection
                self.ser = Serial(serial_port, self.BAUD_RATE, stopbits=1, parity=serial.PARITY_NONE,
                                  bytesize=serial.EIGHTBITS,
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

    def execute(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for i in range(10):
            # get battInfo commend
            # input("Press Enter to get battInfo")
            self.get_battInfo(self.ser)[0]
            print("Got battInfo", i + 1)
            for cell_name in self.cell_data.keys():
                plt.scatter(i, self.cell_data[cell_name]["voltage"])
            plt.pause(0.05)

            print(self.cell_data)
            time.sleep(2)

    """
    -----       Serial Parsing Code     -----
    
    
    """

    # Get battInfo and parse important information
    def getConnectionStatus(self):
        return self.isConnected

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
            ###     PARSE DATA FROM BATTINFO    ###
            split_data = data.split("Index	Cell Voltage(V)	Temp Channel(degC)")

            battSummary = self.parseCellSummary(split_data[0])

            cell_data = split_data[1].split("bmu >")[0]

            return [cell_data, battSummary]

    def parseCellSummary(self, data):
        mainInfo = data.split("*Note Temp is not related to a specific cell number")[0]
        IVBUS = mainInfo.strip().split('\n\n')[0]
        IVBUS_Num = IVBUS.split('\n')[1].split('     ')
        IBUS = IVBUS_Num[0].strip()
        VBUS = IVBUS_Num[1].strip()
        VBATT = IVBUS_Num[2].strip()

        volANDTEMP = mainInfo.strip().split('\n\n')[1]
        volANDTEMP_Num = volANDTEMP.split('\n')[1].split('     ')
        MinVoltage = volANDTEMP_Num[0].strip()
        MaxVoltage = volANDTEMP_Num[1].strip()
        MinTemp = volANDTEMP_Num[2].strip()
        MaxTemp = volANDTEMP_Num[3].strip()
        PackVoltage = volANDTEMP_Num[4].strip()


        return {"IBUS": IBUS,
                "VBUS": VBUS,
                "VBATT": VBATT,
                "MinVoltage":MinVoltage,
                "MaxVoltage": MaxVoltage,
                "MinTemp": MinTemp,
                "MaxTemp": MaxTemp,
                "PackVoltage": PackVoltage}

    def getSoC(self):
        soc = self.sendRequest("soc")
        return float(soc)

    def balancePack(self):
        self.sendRequest("balanceCell")

    def sendRequest(self, command):
        command = command + "\n"
        self.sio.write(command.encode())
        # sio.flush()
        time.sleep(0.2)  # Wait for response
        raw_data = self.sio.read(self.sio.inWaiting())
        return raw_data.decode()

    def setForceChargeMode(self):
        return self.sendRequest("forceChargeMode 1")

    def canStartCharger(self):
        return self.sendRequest("canStartCharger")

    def hvToggle(self):
        return self.sendRequest("hvToggle")

    # sending Max current request
    def setMaxCurrent(self):
        return self.sendRequest("maxChargeCurrent")

    def startCharging(self):
        return self.sendRequest("startCharge")

    def StopCharging(self):
        return self.sendRequest("stopCharge")



    def get_port_name(self):
        return self.all_ports

#
# if __name__ == "__main__":
#     main()
