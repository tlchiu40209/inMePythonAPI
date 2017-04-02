import bluetooth
import time

class InMEReader:
    START_BYTE = 0x51
    START_SECOND_BYTE = 0x70
    PACKET_ASSURANCE_BYTE = 0xA1

    def setInMEAddress(self, address):
        self.InMEAddress = address

    def connectToInME(self):
        if (not self.InMEAddress):
            print "No address is given!"
            return

        try:
            self.InMESocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.InMESocket.connect((self.InMEAddress, 1))
            return
        except bluetooth.btcommon.BluetoothError as error:
            print "Could not connect: ", error, "Retry in 5s"
            time.sleep(5)

    def _getBytesIntoBuffer(self):
        self.InMEBuffer = []
        print "Grabbing Data"
        self.InMEBuffer = self.InMESocket.recv(114)
        print "Grab the following Data into buffer:\n"
        print ":".join("{:02x}".format(ord(c)) for c in self.InMEBuffer)

    def nextRecord(self):
        self._getBytesIntoBuffer()
        self._findHeader()
        

    def _findHeader(self):
        headerFound = False
        print len(self.InMEBuffer)
        print "START_BYTE ", chr(self.START_BYTE)
        print "SECOND BYTE ", chr(self.START_SECOND_BYTE)
        print "ASSU BYTE ", chr(self.PACKET_ASSURANCE_BYTE)

        while(not headerFound):
            for i in range(0, len(self.InMEBuffer)):
                if (i > 57):
                    print "Bad Buffer(Payload Data) Discarding.."
                    self._getBytesIntoBuffer()
                    i = 0
                if (((self.InMEBuffer[i] == chr(self.START_BYTE)) and (self.InMEBuffer[i+1] == chr(self.START_SECOND_BYTE))) and (self.InMEBuffer[i + 37] == chr(self.PACKET_ASSURANCE_BYTE))):
                    print "Header Found", i, self.InMEBuffer[i]
                    self.packetFirstByteLocation = i
                    headerFound = True                    
                    break
                else:
                    print "Not Header", i, self.InMEBuffer[i]

    def disconnectFromInME(self):
        self.InMESocket.close()

    def getADS1229Descriptive(self):
        shift = self.packetFirstByteLocation
        ads1229Descriptive = ADS1229_Descriptive_DataStruct(self.InMEBuffer[shift + 2 : shift + 10])
        return ads1229Descriptive

    def getADS1229Channel(self):
        shift = self.packetFirstByteLocation
        ads1229Channel = ADS1229_Channel_DataStruct(self.InMEBuffer[shift + 13 : shift + 37])
        return ads1229Channel

    def getADS1229LeadOff(self):
        shift = self.packetFirstByteLocation
        ads1229LeadOff = ADS1229_LeadOff_DataStruct(self.InMEBuffer[shift + 10 : shift + 13])
        return ads1229LeadOff

    def getAFE4490Descriptive(self):
        shift = self.packetFirstByteLocation
        afe4490Descriptive = AFE4490_Descriptive_DataStruct(self.InMEBuffer[shift + 41 : shift + 49])
        return afe4490Descriptive

    def getAFE4490Channel(self):
        shift = self.packetFirstByteLocation
        afe4490Channel = AFE4490_Channel_DataStruct(self.InMEBuffer[shift + 49 : shift + 55])
        return afe4490Channel
                                                  

class ADS1229_Descriptive_DataStruct:
    def __init__(self, eightBytes):
        self._payload = eightBytes
        self._parsePayload()

    def _parsePayload(self):
        self.FrameID = self._convertToInteger(self._payload[0:4])
        self.TimeTick = self._convertToInteger(self._payload[4:8])

    def _convertToInteger(self, fourBytes):
        firstByte = fourBytes[0]
        secondByte = fourBytes[1]
        thirdByte = fourBytes[2]
        fourthByte = fourBytes[3]

        value = ord(firstByte) * 16777216 + ord(secondByte) * 65536 + ord(thirdByte) * 256 + ord(fourthByte)
        return value

    def __str__(self):
        print ":".join("{:02x}".format(ord(c)) for c in self._payload)
        return """ADS1229 Descriptive Data:
                FrameID: {self.FrameID}
                TimeTick: {self.TimeTick}
                """.format(self = self)        

class ADS1229_LeadOff_DataStruct:
    def __init__(self, threeBytes):
        self._payload = threeBytes
        self._parsePayload()

    def _parsePayload(self):

        secondByte = self._payload[1]
        bitArray = bin(ord(secondByte))[2:].zfill(8)

        self.CH1 = False
        self.CH2 = False
        self.CH3 = False
        self.CH4 = False
        self.CH5 = False
        self.CH6 = False
        self.CH7 = False
        self.CH8 = False

        if (bitArray[4] == '1'):
            self.CH1 = True
        if (bitArray[5] == '1'):
            self.CH2 = True
        if (bitArray[6] == '1'):
            self.CH3 = True
        if (bitArray[7] == '1'):
            self.CH4 = True
        if (bitArray[0] == '1'):
            self.CH5 = True
        if (bitArray[1] == '1'):
            self.CH6 = True
        if (bitArray[2] == '1'):
            self.CH7 = True
        if (bitArray[3] == '1'):
            self.CH8 = True

    def __str__(self):
        print ":".join("{:02x}".format(ord(c)) for c in self._payload)
        if (self._payload[1] == chr(0)):
            return "No lead off Devices"
        else:
            return_string = "The following Channel is leading Off!"
            if (self.CH1):
                return_string += "\n Channel 1"
            if (self.CH2):
                return_string += "\n Channel 2"
            if (self.CH3):
                return_string += "\n Channel 3"
            if (self.CH4):
                return_string += "\n Channel 4"
            if (self.CH5):
                return_string += "\n Channel 5"
            if (self.CH6):
                return_string += "\n Channel 6"
            if (self.CH7):
                return_string += "\n Channel 7"
            if (self.CH8):
                return_string += "\n Channel 8"
            return return_string


class ADS1229_Channel_DataStruct:
    def __init__(self, twentyFourBytes):
        self._payload = twentyFourBytes
        self._parsePayload()

    def _parsePayload(self):
        self.CH1 = self._convertToInteger(self._payload[0:3])
        self.CH2 = self._convertToInteger(self._payload[3:6])
        self.CH3 = self._convertToInteger(self._payload[6:9])
        self.CH4 = self._convertToInteger(self._payload[9:12])
        self.CH5 = self._convertToInteger(self._payload[12:15])
        self.CH6 = self._convertToInteger(self._payload[15:18])
        self.CH7 = self._convertToInteger(self._payload[18:21])
        self.CH8 = self._convertToInteger(self._payload[21:24])

    def _convertToInteger(self, threeBytes):
        firstByte = threeBytes[0]
        secondByte = threeBytes[1]
        thirdByte = threeBytes[2]

        value = ord(firstByte) *65536 + ord(secondByte) *256 + ord(thirdByte)
        if (value > 8338607):
            value -= 16777216
        return value

    def __str__(self):
        print ":".join("{:02x}".format(ord(c)) for c in self._payload)
        return """ADS1229 Channel Data:
                CH1: {self.CH1}
                CH2: {self.CH2}
                CH3: {self.CH3}
                CH4: {self.CH4}
                CH5: {self.CH5}
                CH6: {self.CH6}
                CH7: {self.CH7}
                CH8: {self.CH8}
                """.format(self = self)

class AFE4490_Descriptive_DataStruct:
    def __init__(self, eightBytes):
        self._payload = eightBytes
        self._parsePayload()

    def _parsePayload(self):
        self.FrameID = self._convertToInteger(self._payload[0:4])
        self.TimeTick = self._convertToInteger(self._payload[4:8])

    def _convertToInteger(self, fourBytes):
        firstByte = fourBytes[0]
        secondByte = fourBytes[1]
        thirdByte = fourBytes[2]
        fourthByte = fourBytes[3]

        value = ord(firstByte) * 16777216 + ord(secondByte) * 65536 + ord(thirdByte) * 256 + ord(fourthByte)
        return value

    def __str__(self):
        print ":".join("{:02x}".format(ord(c)) for c in self._payload)
        return """AFE4490 Descriptive Data:
                FrameID: {self.FrameID}
                TimeTick: {self.TimeTick}
                """.format(self = self)
        

class AFE4490_Channel_DataStruct:
    def __init__(self, sixBytes):
        self._payload = sixBytes
        self._parsePayload()

    def _parsePayload(self):
        self.RData = self._convertToInteger(self._payload[0:3])
        self.IRData = self._convertToInteger(self._payload[3:6])

    def _convertToInteger(self, threeBytes):
        firstByte = threeBytes[0]
        secondByte = threeBytes[1]
        thirdByte = threeBytes[2]

        value = ord(firstByte) + ord(secondByte) * 256 + ord(thirdByte) * 65536
        return value

    def __str__(self):
        print ":".join("{:02x}".format(ord(c)) for c in self._payload)
        return """AFE4490 Channel Data:
                RData: {self.RData}
                IRData: {self.IRData}
                """.format(self = self) 
