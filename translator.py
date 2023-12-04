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
    "Phase Direction[PhaseA]"                           : ["byte_signed", 0],
    "Phase Direction[PhaseB]"                           : ["byte_signed", 0],
    "Phase Direction[PhaseC]"                           : ["byte_signed", 0],
    "Phase Direction[PhaseN]"                           : ["byte_signed", 0],
    "Phase Delay[PhaseA]"                               : ["short_unsigned", 0],
    "Phase Delay[PhaseB]"                               : ["short_unsigned", 0],
    "Phase Delay[PhaseC]"                               : ["short_unsigned", 0],
    "Phase Delay[PhaseN]"                               : ["short_unsigned", 0],
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
        for enum in data:
            if CalibrationParameter[enum][0] == "short_unsigned":
                mTempList.extend(serializeU16(data[enum]))        
            elif CalibrationParameter[enum][0] == "short_signed":
                mTempList.extend(serializeS16(data[enum]))        
            elif CalibrationParameter[enum][0] == "byte_signed":
                mTempList.extend(serializeS08(data[enum]))        
            else:
                mTempList.append(data[enum])

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

# data = [0, 129, 0, 128, 0, 128, 0, 128, 0, 128, 0, 128, 136, 120, 136, 120, 136, 120, 136, 120, 170, 116, 170, 116, 170, 116, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 36, 19, 32, 3, 1, 1, 1, 255, 250, 0, 250, 0, 250, 0, 250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# register = translate(data)
# for reg in register:
#     print(f'{reg}: {register[reg]}')