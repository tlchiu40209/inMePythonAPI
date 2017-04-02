from inME_API import InMEReader, ADS1229_Descriptive_DataStruct, ADS1229_LeadOff_DataStruct\
     , ADS1229_Channel_DataStruct, AFE4490_Descriptive_DataStruct, AFE4490_Channel_DataStruct

inME = InMEReader()
inME.setInMEAddress("00:1A:FF:09:0A:0A")
inME.connectToInME()
 
inME.nextRecord()
ads1229Descriptive = inME.getADS1229Descriptive()
ads1229LeadOff = inME.getADS1229LeadOff()
ads1229Channel = inME.getADS1229Channel()
afe4490Descriptive = inME.getAFE4490Descriptive()
afe4490Channel = inME.getAFE4490Channel()
print ads1229Descriptive
print ads1229LeadOff
print ads1229Channel
print afe4490Descriptive
print afe4490Channel
inME.disconnectFromInME()
