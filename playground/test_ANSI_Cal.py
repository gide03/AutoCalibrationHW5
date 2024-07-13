import serial
import pathlib
import time
import site
import click
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()

site.addsitedir(CURRENT_PATH.parent)

from datetime import datetime, timedelta
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

from lib.Utils.MeterSetup import MeterSetup
from lib.Utils.CalibrationData import CalibrationRegister
from lib.Utils.CalMode import CalMode
from src.config import CosemList

class commSetting:
    METER_ADDR = 100
    CLIENT_NUMBER = 0x73
    AUTH_KEY = "wwwwwwwwwwwwwwww"
    GUEK = "30303030303030303030303030303030"
    GAK = "30303030303030303030303030303030"
    SYS_TITLE = "4954453030303030"
    # For HW 5
    USE_RLRQ = True
    IS_RLRQ_PROTECTED = True
    
def calRunningCRC16(dataFrame) -> int:
    lCrc = 0xffff
    
    for dataIdx in range(0, len(dataFrame)):
        data = dataFrame[dataIdx]
        lCrc = lCrc ^ (data << 8)
        for i in range(0,8):
            if (lCrc & 0x8000):
                lCrc = (lCrc << 1) ^ 0x1021
            else:
                lCrc <<= 1
        lCrc &= 0xffff
    # return [lCrc&0xff, lCrc>>8]
    return lCrc

@click.command()
@click.option('--port', prompt="Enter serial port")
def main(port):
    calibrationData = CalibrationRegister()
    meterSetup = MeterSetup()
    ser_client = DlmsCosemClient(
        port=port,
        baudrate=19200,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.05,
        inactivity_timeout=10,
        login_retry=1,
        meter_addr=commSetting.METER_ADDR,
        client_nb=commSetting.CLIENT_NUMBER,
        address_size = AddrSize.ONE_BYTE
    )
    CYCLE_CAL = 90
    PF = 0.5

    ser_client.client_logout()
    login_result = ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
    print('login result: ',login_result)

    # START FROM HERE1-23:1.8.0.255

    cosem = CosemList.CalibarationData
    calib = CalibrationRegister()
    read_calib = ser_client.get_cosem_data(cosem.classId, cosem.obis, 2)
    calib.extract(read_calib)
    
    # calib.tf_control.set(1)
    # ser_client.set_cosem_data(cosem.classId, cosem.obis, 2, 9, calib.dataFrame())
    # print(f'RMS Gain:')
    # objectList = vars(calib)
    # for regName in objectList:
    #     if "Irms" in regName or "Vrms" in regName :
    #         print(f'{regName}: {objectList[regName].value}')

    cosem = CosemList.CalMode
    calmode = CalMode()

    print(f'Write CalMode:')
    calmode.Quantity.value = 1 #calib wH
    calmode.Cycles.value = CYCLE_CAL # 90 cycle
    calmode.CalStatus.value = 1 #start calibration
    read_result = ser_client.set_cosem_data(cosem.classId, cosem.obis, 2, CosemDataType.e_OCTET_STRING, calmode.dataFrame())
    print(f'WRITE RESULT: {read_result}')
    time.sleep(3)

    read_calmode = ser_client.get_cosem_data(cosem.classId, cosem.obis, 2)
    calmode.extract(read_calmode)
    print(f'Read CalMode:')
    # objectList = vars(calmode)
    # for regName in objectList:
    #     print(f'{regName}: {objectList[regName].value}')

    # PF_A_cosem = CosemList.PowerFactorL1
    # PF_A = ser_client.get_cosem_data(PF_A_cosem.classId, PF_A_cosem.obis, 2)
    # PF_B_cosem = CosemList.PowerFactorL2
    # PF_B = ser_client.get_cosem_data(PF_B_cosem.classId, PF_B_cosem.obis, 2)
    # PF_C_cosem = CosemList.PowerFactorL3
    # PF_C = ser_client.get_cosem_data(PF_C_cosem.classId, PF_C_cosem.obis, 2)
    # PF = [PF_A/1000,PF_B/1000,PF_C/1000]

    InstFreq = CosemList.InstantFrequency
    Fin = round(ser_client.get_cosem_data(InstFreq.classId, InstFreq.obis, 2)/1000)

    
    # print(calmode.VrmsA.value,calib.GainVrms_A.value)
    cycle = CYCLE_CAL
    Calimp = [calmode.CalimpA.value,calmode.CalimpB.value,calmode.CalimpC.value]
    Calrem = [calmode.CalremA.value,calmode.CalremB.value,calmode.CalremC.value]
    ThreshPulses = calmode.Threshpulses.value
    basegain = 32768
    gainvrms = [calib.VrmsGainPhA.value,calib.VrmsGainPhB.value,calib.VrmsGainPhC.value]
    gainirms = [calib.IrmsGainPhA.value,calib.IrmsGainPhB.value,calib.IrmsGainPhC.value]
    insVrms =[calmode.VrmsA.value/1000,calmode.VrmsB.value/1000,calmode.VrmsC.value/1000]
    insIrms =[calmode.IrmsA.value/1000,calmode.IrmsB.value/1000,calmode.IrmsC.value/1000]
    
    phaseDelayOld = [calib.PhaseDelayA.value,calib.PhaseDelayB.value,calib.PhaseDelayC.value]
    phaseDelayNew = [0,0,0]
    
    calmode.info(verbose=True)
    print(f'Calimp: {Calimp}')
    print(f'Calrem: {Calrem}')
    print(f'TrheshPulses: {ThreshPulses}')
    print(f'Phase delay old: {phaseDelayOld}')


    
    FLV = [1,1,1] #always 1
    PFV = [0,0,0]

    # PhaseDelayOld
    # (FLV[i] - PFV[i])/0.03 + phaseDelayOld

    print("PF :",PF)
    print("Fin :",Fin)
    print("Calimp:",Calimp)
    print("Calrem:",Calrem)
    print("gainvrms:",gainvrms)
    print("gainrms:",gainirms)
    Wh_m = [0,0,0]
    New_Vrms_Gain = [0,0,0]
    New_Irms_Gain = [0,0,0]
    Wh_std = [0,0,0]
    for i in range(3):
        Wh_m[i] = (Calimp[i] + (Calrem[i]/ThreshPulses))/10
        New_Vrms_Gain[i] = gainvrms[i]/basegain
        New_Irms_Gain[i] = gainirms[i]/basegain
        Wh_std[i] = insVrms[i] * insIrms[i] / 3600 * cycle/Fin * PF
        if Wh_std[i] != 0 :
            PFV[i] = Wh_m[i] / Wh_std[i]
        phaseDelayNew[i] = ((FLV[i]*100 - PFV[i]*100) / 0.03 ) + phaseDelayOld[i]
        #check rollover
        if phaseDelayNew[i] > 256 :
            phaseDelayNew[i] -= 256
        if phaseDelayNew[i] < 0 :
            phaseDelayNew[i] = 256 + phaseDelayNew[i]
        
    
    print("Vrms",insVrms)
    print("Irms",insIrms)
    print("Wh_m",Wh_m)
    print("New_Vrms_Gain",New_Vrms_Gain)
    print("New_Irms_Gain",New_Irms_Gain)
    print("Wh_std",Wh_std)
    print("PFV",PFV)
    print("phaseDelayOld",phaseDelayOld)
    print("phaseDelayNew",phaseDelayNew)

    # END HERE

    ser_client.client_logout()

if __name__ == '__main__':
    main()