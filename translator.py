import struct

CalibrationParameter = {
    "g_MQAcquisition.gainActiveE[phaseA]"               : ["short_unsigned", 0],
    "g_MQAcquisition.gainActiveE[phaseB]"               : ["short_unsigned", 0],
    "g_MQAcquisition.gainActiveE[phaseC]"               : ["short_unsigned", 0],
    "g_MQAcquisition.gainReactiveE[phaseA]"             : ["short_unsigned", 0],
    "g_MQAcquisition.gainReactiveE[phaseB]"             : ["short_unsigned", 0],
    "g_MQAcquisition.gainReactiveE[phaseC]"             : ["short_unsigned", 0],
    "g_MQAcquisition.gainIrms[phaseA]"                  : ["short_unsigned", 0],
    "g_MQAcquisition.gainIrms[phaseB]"                  : ["short_unsigned", 0],
    "g_MQAcquisition.gainIrms[phaseC]"                  : ["short_unsigned", 0],
    "g_MQAcquisition.gainIrms[neutral]"                 : ["short_unsigned", 0],
    "g_MQAcquisition.gainVrms[phaseA]"                  : ["short_unsigned", 0],
    "g_MQAcquisition.gainVrms[phaseB]"                  : ["short_unsigned", 0],
    "g_MQAcquisition.gainVrms[phaseC]"                  : ["short_unsigned", 0],
    "g_MQPhaseFilter.k1[phaseA]"                        : ["short_signed", 0],
    "g_MQPhaseFilter.k2[phaseA]"                        : ["short_signed", 0],
    "g_MQPhaseFilter.k3[phaseA]"                        : ["short_signed", 0],
    "g_MQPhaseFilter.k1[phaseB]"                        : ["short_signed", 0],
    "g_MQPhaseFilter.k2[phaseB]"                        : ["short_signed", 0],
    "g_MQPhaseFilter.k3[phaseB]"                        : ["short_signed", 0],
    "g_MQPhaseFilter.k1[phaseC]"                        : ["short_signed", 0],
    "g_MQPhaseFilter.k2[phaseC]"                        : ["short_signed", 0],
    "g_MQPhaseFilter.k3[phaseC]"                        : ["short_signed", 0],
    "g_MQPhaseFilter.gainSlope"                         : ["short_signed", 0],
    "Temperature.k1_V"                                  : ["short_signed", 0],
    "Temperature.k2_V"                                  : ["short_signed", 0],
    "Temperature.k3_V"                                  : ["short_signed", 0],
    "Temperature.k1_I"                                  : ["short_signed", 0],
    "Temperature.k2_I"                                  : ["short_signed", 0],
    "Temperature.k3_I"                                  : ["short_signed", 0],
    "Temperature.k1Shift_V"                             : ["byte_unsigned", 0],
    "Temperature.k2Shift_V"                             : ["byte_unsigned", 0],
    "Temperature.k3Shift_V"                             : ["byte_unsigned", 0],
    "Temperature.k1Shift_I"                             : ["byte_unsigned", 0],
    "Temperature.k2Shift_I"                             : ["byte_unsigned", 0],
    "Temperature.k3Shift_I"                             : ["byte_unsigned", 0],
    "g_NonLinear.k1"                                    : ["short_signed", 0],
    "g_NonLinear.k2"                                    : ["short_signed", 0],
    "g_NonLinear.k3"                                    : ["short_signed", 0],
    "g_NonLinear.k4"                                    : ["short_signed", 0],
    "g_NonLinear.k5"                                    : ["short_signed", 0],
    "g_NonLinear.k6"                                    : ["short_signed", 0],
    "g_NonLinear.k7"                                    : ["short_unsigned", 0],
    "g_NonLinear.Break_Current[0]"                      : ["short_unsigned", 0],
    "g_NonLinear.Break_Current[1]"                      : ["short_unsigned", 0],
    "g_NonLinear.k1Shift"                               : ["byte_unsigned", 0], 
    "g_NonLinear.k2Shift"                               : ["byte_unsigned", 0],
    "g_NonLinear.k3Shift"                               : ["byte_unsigned", 0],
    "g_NonLinear.k4Shift"                               : ["byte_unsigned", 0],
    "g_NonLinear.k5Shift"                               : ["byte_unsigned", 0],
    "g_NonLinear.k6Shift"                               : ["byte_unsigned", 0],
    "Vrms.Slope"                                        : ["short_signed", 0],
    "Vrms.Offset"                                       : ["short_unsigned", 0],
    "Temperature.Calibration Temperature"               : ["short_signed", 0],
    "Temperature.Actual_Temp_At_Cal"                    : ["short_signed", 0],
    "Phase Direction[PhaseA]"                         : ["byte_signed", 0],
    "Phase Direction[PhaseB]"                         : ["byte_signed", 0],
    "Phase Direction[PhaseC]"                         : ["byte_signed", 0],
    "Phase Direction[PhaseN]"                         : ["byte_signed", 0],
    "Phase Delay[PhaseA]"                             : ["short_unsigned", 0],
    "Phase Delay[PhaseB]"                             : ["short_unsigned", 0],
    "Phase Delay[PhaseC]"                             : ["short_unsigned", 0],
    "Phase Delay[PhaseN]"                             : ["short_unsigned", 0],
    "g_MQFrequency.window"                              : ["byte_unsigned", 0],
    "g_MQMetrology.activeqties.energy.offset[phaseA]"   : ["short_signed", 0],
    "g_MQMetrology.activeqties.energy.offset[phaseB]"   : ["short_signed", 0],
    "g_MQMetrology.activeqties.energy.offset[phaseC]"   : ["short_signed", 0],
    "g_MQMetrology.reactiveqties.energy.offset[phaseA]" : ["short_signed", 0],
    "g_MQMetrology.reactiveqties.energy.offset[phaseB]" : ["short_signed", 0],
    "g_MQMetrology.reactiveqties.energy.offset[phaseC]" : ["short_signed", 0],
}

def serializeU16(iData):
    mArrayReturn = []
    mArrayReturn = list(struct.pack(">H", iData))
    return mArrayReturn

def deserializeU16(iData):
    mReturn = []
    mReturn = struct.unpack(">H", bytearray(iData))
    return mReturn[0]

def serializeS16(iData):
    mArrayReturn = []
    mArrayReturn = list(struct.pack(">h", iData))
    return mArrayReturn

def deserializeS16(iData):
    mReturn = []
    mReturn = struct.unpack(">h", bytearray(iData))
    return mReturn[0]

def serializeS08(iData):
    mArrayReturn = []
    mArrayReturn = list(struct.pack(">b", iData))
    return mArrayReturn

def deserializeS08(iData):
    mReturn = []
    mReturn = struct.unpack(">b", bytearray(iData))
    return mReturn[0]

def translate(data, to_bytes=False):
    if to_bytes:
        #Print Data to Set!
        mTempList = []
        for enum in CalibrationParameter:
            if CalibrationParameter[enum][0] == "short_unsigned":
                mTempList.extend(serializeU16(CalibrationParameter[enum][1]))        
            elif CalibrationParameter[enum][0] == "short_signed":
                mTempList.extend(serializeS16(CalibrationParameter[enum][1]))        
            elif CalibrationParameter[enum][0] == "byte_signed":
                mTempList.extend(serializeS08(CalibrationParameter[enum][1]))        
            else:
                mTempList.append(CalibrationParameter[enum][1])

        # print(len(mTempList))
        # for x in range(len(mTempList)):
        #     mTempList[x] = str(hex(mTempList[x])).replace("0x", "")
        #     if len(mTempList[x]) < 2:
        #         mTempList[x] = "0" + mTempList[x]
        #     print(mTempList[x], end = " ")
        return mTempList
    
    mIndexData = 0 
    mTempList = []
    for enum in CalibrationParameter:
        if CalibrationParameter[enum][0] == "short_unsigned":
            mTempList.append(data[mIndexData])
            mIndexData += 1
            mTempList.append(data[mIndexData])
            mIndexData += 1
            CalibrationParameter[enum][1] = deserializeU16(mTempList)
        elif CalibrationParameter[enum][0] == "short_signed":
            mTempList.append(data[mIndexData])
            mIndexData += 1
            mTempList.append(data[mIndexData])
            mIndexData += 1
            CalibrationParameter[enum][1] = deserializeS16(mTempList)
        elif CalibrationParameter[enum][0] == "byte_signed":
            mTempList.append(data[mIndexData])
            mIndexData += 1
            CalibrationParameter[enum][1] = deserializeS08(mTempList)
        else:
            mTempList = data[mIndexData]
            mIndexData += 1
            CalibrationParameter[enum][1] = mTempList
        mTempList = []

    #Print Data
    output = {}
    for x in CalibrationParameter:
        output[x] = CalibrationParameter[x][1]
    return output


# #SET CALIBRATION VALUE

# CalibrationSet = {

#     "g_MQAcquisition.gainActiveE[phaseA]"                       : ["short_unsigned",    32734],
#     "g_MQAcquisition.gainActiveE[phaseB]"                       : ["short_unsigned",    32939],
#     "g_MQAcquisition.gainActiveE[phaseC]"                       : ["short_unsigned",    32751],
#     "g_MQAcquisition.gainReactiveE[phaseA]"                     : ["short_unsigned",    32768],
#     "g_MQAcquisition.gainReactiveE[phaseB]"                     : ["short_unsigned",    32768],
#     "g_MQAcquisition.gainReactiveE[phaseC]"                     : ["short_unsigned",    32768],
#     "g_MQAcquisition.gainIrms[phaseA]"                          : ["short_unsigned",    42160],
#     "g_MQAcquisition.gainIrms[phaseB]"                          : ["short_unsigned",    42498],
#     "g_MQAcquisition.gainIrms[phaseC]"                          : ["short_unsigned",    42407],
#     "g_MQAcquisition.gainIrms[neutral]"                         : ["short_unsigned",    34000],
#     "g_MQAcquisition.gainVrms[phaseA]"                          : ["short_unsigned",    29799],
#     "g_MQAcquisition.gainVrms[phaseB]"                          : ["short_unsigned",    30473],
#     "g_MQAcquisition.gainVrms[phaseC]"                          : ["short_unsigned",    30477],

 
#     "g_MQPhaseFilter.k1[phaseA]"                                : ["short_signed",      0],
#     "g_MQPhaseFilter.k2[phaseA]"                                : ["short_signed",      0],
#     "g_MQPhaseFilter.k3[phaseA]"                                : ["short_signed",      0],
#     "g_MQPhaseFilter.k1[phaseB]"                                : ["short_signed",      0],
#     "g_MQPhaseFilter.k2[phaseB]"                                : ["short_signed",      0],
#     "g_MQPhaseFilter.k3[phaseB]"                                : ["short_signed",      0],
#     "g_MQPhaseFilter.k1[phaseC]"                                : ["short_signed",      0],
#     "g_MQPhaseFilter.k2[phaseC]"                                : ["short_signed",      0],
#     "g_MQPhaseFilter.k3[phaseC]"                                : ["short_signed",      0],
#     "g_MQPhaseFilter.gainSlope"                                 : ["short_signed",      0],
#     "Temperature.k1_V"                                          : ["short_signed",      0],
#     "Temperature.k2_V"                                          : ["short_signed",      0],
#     "Temperature.k3_V"                                          : ["short_signed",      0],
#     "Temperature.k1_I"                                          : ["short_signed",      0],
#     "Temperature.k2_I"                                          : ["short_signed",      0],
#     "Temperature.k3_I"                                          : ["short_signed",      0],
#     "Temperature.k1Shift_V"                                     : ["byte_unsigned",     0],
#     "Temperature.k2Shift_V"                                     : ["byte_unsigned",     0],
#     "Temperature.k3Shift_V"                                     : ["byte_unsigned",     0],
#     "Temperature.k1Shift_I"                                     : ["byte_unsigned",     0],
#     "Temperature.k2Shift_I"                                     : ["byte_unsigned",     0],
#     "Temperature.k3Shift_I"                                     : ["byte_unsigned",     0],
#     "g_NonLinear.k1"                                            : ["short_signed",      0],
#     "g_NonLinear.k2"                                            : ["short_signed",      0],
#     "g_NonLinear.k3"                                            : ["short_signed",      0],
#     "g_NonLinear.k4"                                            : ["short_signed",      0],
#     "g_NonLinear.k5"                                            : ["short_signed",      0],
#     "g_NonLinear.k6"                                            : ["short_signed",      0],
#     "g_NonLinear.k7"                                            : ["short_unsigned",    32768],
#     "g_NonLinear.Break_Current[0]"                              : ["short_unsigned",    312],
#     "g_NonLinear.Break_Current[1]"                              : ["short_unsigned",    1875],
#     "g_NonLinear.k1Shift"                                       : ["byte_unsigned",     0], 
#     "g_NonLinear.k2Shift"                                       : ["byte_unsigned",     0],
#     "g_NonLinear.k3Shift"                                       : ["byte_unsigned",     0],
#     "g_NonLinear.k4Shift"                                       : ["byte_unsigned",     0],
#     "g_NonLinear.k5Shift"                                       : ["byte_unsigned",     0],
#     "g_NonLinear.k6Shift"                                       : ["byte_unsigned",     0],
#     "Vrms.Slope"                                                : ["short_signed",      0],
#     "Vrms.Offset"                                               : ["short_unsigned",    32768],
#     "Temperature.Calibration Temperature"                       : ["short_signed",      16121],
#     "Temperature.Actual_Temp_At_Cal"                            : ["short_signed",      800],
#     "Phase Direction[PhaseA]"                                   : ["byte_signed",       1],
#     "Phase Direction[PhaseB]"                                   : ["byte_signed",       1],
#     "Phase Direction[PhaseC]"                                   : ["byte_signed",       1],
#     "Phase Direction[PhaseN]"                                   : ["byte_signed",       1],
#     "Phase Delay[PhaseA]"                                       : ["short_unsigned",    1],
#     "Phase Delay[PhaseB]"                                       : ["short_unsigned",    1],
#     "Phase Delay[PhaseC]"                                       : ["short_unsigned",    1],
#     "Phase Delay[PhaseN]"                                       : ["short_unsigned",    1],
#     "g_MQFrequency.window"                                      : ["byte_unsigned",     5],
#     "g_MQMetrology.activeqties.energy.offset[phaseA]"           : ["short_signed",      0],
#     "g_MQMetrology.activeqties.energy.offset[phaseB]"           : ["short_signed",      0],
#     "g_MQMetrology.activeqties.energy.offset[phaseC]"           : ["short_signed",      0],
#     "g_MQMetrology.reactiveqties.energy.offset[phaseA]"         : ["short_signed",      0],
#     "g_MQMetrology.reactiveqties.energy.offset[phaseB]"         : ["short_signed",      0],
#     "g_MQMetrology.reactiveqties.energy.offset[phaseC]"         : ["short_signed",      0],
# }

# #Print Data to Set!
# mTempList = []
# for enum in CalibrationSet:
#     if CalibrationSet[enum][0] == "short_unsigned":
#         mTempList.extend(serializeU16(CalibrationSet[enum][1]))        
#     elif CalibrationSet[enum][0] == "short_signed":
#         mTempList.extend(serializeS16(CalibrationSet[enum][1]))        
#     elif CalibrationParameter[enum][0] == "byte_signed":
#         mTempList.extend(serializeS08(CalibrationSet[enum][1]))        
#     else:
#         mTempList.append(CalibrationSet[enum][1])

# # print(len(mTempList))
# for x in range(len(mTempList)):
#     mTempList[x] = str(hex(mTempList[x])).replace("0x", "")
#     if len(mTempList[x]) < 2:
#         mTempList[x] = "0" + mTempList[x]
#     print(mTempList[x], end = " ")
