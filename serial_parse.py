import os, datetime, serial, csv, time, random, signal, math
import io
import serial.tools.list_ports
from serial import Serial
import matplotlib.pyplot as plt

# This string is only for testing purposes (fake data)
from document.CommandOutput import fakeData


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

    def port_setup(self):  # Return ports list
        # open the port and list of all available ports
        self.all_ports = []
        try:
            ports = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(ports):
                # print("{}: {}".format(port, desc))    # Uncomment to see all ports found
                self.all_ports.append("{}: {}".format(port, desc))
            return self.all_ports
        except:
            print("something was wrong when setting up port")
            return False

    def connectPort(self, port):  # Return ports list
        # TODO: MAKE THIS BACK TO FALSE: TRUE IS ONLY FOR TESTING PURPOSE
        return True
        try:
            p = port.lower()
            serial_port = p.split(':')[0]
            message = f"Found {serial_port}"
            self.isConnected = True
            print(message)

            # Setup Serial Connection
            self.ser = Serial(serial_port, self.BAUD_RATE, stopbits=1, parity=serial.PARITY_NONE,
                              bytesize=serial.EIGHTBITS,
                              timeout=0)

            self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))

            return True
        except:
            print("Something was wrong when connecting port")
            return False

    def disconnectPort(self):
        if self.ser.isOpen():
            self.ser.close()
            self.isConnected = False

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

    # Get battInfo and parse important information
    def getConnectionStatus(self):
        return self.isConnected

    def get_battInfo(self):
        # # sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        # self.ser.write("battInfo\n".encode())
        # # sio.flush()
        # time.sleep(0.2)  # Wait for response
        # raw_data = self.ser.read(self.ser.inWaiting())
        # data = raw_data.decode()

        # TODO: Uncomment above and remove these two lines
        # ///////////////////////////////////////////////////////////////
        data = fakeData
        print("fake Data: " + fakeData)
        # ///////////////////////////////////////////////////////////////


        if not data:
            print("ERROR: NO DATA RECEIVED FROM BATTINFO CMD")
            return "error"

        else:
            ###     PARSE DATA FROM BATTINFO    ###
            '''
                split_data[0] is the summary
                split_data[1] is the individual cell data
            '''
            split_data = data.split("Index	Cell Voltage(V)	Temp Channel(degC)")
            battSummary = self.parseCellSummary(split_data[0])
            cell_data = split_data[1].split("bmu >")[0]
            return [cell_data, battSummary]

    def parseCellSummary(self, data):
        mainInfo = data.split("*Note Temp is not related to a specific cell number")[0]
        mainInfo_list = mainInfo.split('\n\n')

        IVBUS = mainInfo_list[0].strip()

        if "PEC Rate" in IVBUS:
            IVBUS = IVBUS[IVBUS.find('IBUS'):]

        IVBUS_Num = IVBUS.split('\n')[1].split('\t')

        #TODO: Splitting tab not working here dude
        IBUS = IVBUS_Num[0].strip()
        VBUS = IVBUS_Num[1].strip()
        VBATT = IVBUS_Num[2].strip()

        volANDTEMP = mainInfo_list[1].strip()
        volANDTEMP_Num = volANDTEMP.split('\n')[1].split('\t')
        MinVoltage = volANDTEMP_Num[0].strip()
        MaxVoltage = volANDTEMP_Num[1].strip()
        MinTemp = volANDTEMP_Num[2].strip()
        MaxTemp = volANDTEMP_Num[3].strip()
        PackVoltage = volANDTEMP_Num[4].strip()

        return {"IBUS": IBUS,
                "VBUS": VBUS,
                "VBATT": VBATT,
                "MinVoltage": MinVoltage,
                "MaxVoltage": MaxVoltage,
                "MinTemp": MinTemp,
                "MaxTemp": MaxTemp,
                "PackVoltage": PackVoltage}

    def getSoC(self):
        data = self.sendRequest("soc")
        soc = round(float(data[data.find("Charge") + 7: data.find("%") - 1]), 2)
        return soc

    def balancePack(self, cell, switch):
        # TODO: Do we need to stop, there is like on and off? and I think the first cell is 0?
        # Top/Bottom balance? all do we just top balance all?
        """ balanceCell <cell number> <on|off>:\r\n set the state of the balance resistor for a specific cell\r\n"""
        if cell > 70 or cell < 0:
            return "invalid input"
        return self.sendRequest("balanceCell " + cell + " " + switch)

    def sendRequest(self, command):
        command = command + "\n"
        self.ser.write(command.encode())
        # ser.flush()
        time.sleep(0.2)  # Wait for response
        raw_data = self.ser.read(self.ser.inWaiting())
        return raw_data.decode()

    def setForceChargeMode(self):
        return self.sendRequest("forceChargeMode 1")

    def canStartCharger(self):
        return self.sendRequest("canStartCharger")

    def hvToggle(self):
        return self.sendRequest("hvToggle")

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
