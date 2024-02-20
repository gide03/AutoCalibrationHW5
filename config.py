METER_USB_PORT  = 'COM4'
GENY_USB_PORT   = 'COM2'    # only used when calibrating error energy

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

class CalibrationParameter:    
    GENY_SLOT_INDEX = 3         # NOTE: Posisi meter pada slot geny test bench, ditihitung dari palig kiri 1, 2, 3
    ERROR_ACCEPTANCE = 0.4      # NOTE: Kriteria meter sukses dikalibrasi dalam persen
    
    # Test bench nominal configuration
    PHASE_ANGLE_CONFIG = 60     # in Degree
    VOLTAGE_NOMINAL = 230       # in Volt
    CURRENT_NOMINAL = 30        # in Ampere
    BOOTING_TIME = 10           # in Second. waiting time for boot start from geny is turned on
    REBOOT_WAIT = 10             # in Second. Waiting time for reboot
    
    # Error tolrance relate to meter Vrms and Irms measurement
    VOLTAGE_ERROR_ACCEPTANCE = 30/100   # in Percent
    CURRENT_ERROR_ACCEPTANCE = 30/100   # in Percent
    POWER_ERROR_ACCEPTANCE   = 30/100   # in Percent
    

#
# COSEM LIST
#
class CosemObject:
    def __init__(self, objectName, obis, classId) -> None:
        self.objectName = objectName
        self.obis = obis
        self.classId = classId

class CosemList(CosemObject):
    CalibarationData = CosemObject('CalibrationData', '0;128;96;14;80;255', 1)
    MeterSetup = CosemObject('MeterSetup', '0;128;96;14;81;255', 1)
    FlashErase = CosemObject('FlashErase', '1;1;128;130;3;255', 1)
    
    InstantVoltagePhase1 = CosemObject('InstantVoltagePhase1', "1;0;32;7;0;255", 3)
    InstantVoltagePhase2 = CosemObject('InstantVoltagePhase2', "1;0;52;7;0;255", 3)
    InstantVoltagePhase3 = CosemObject('InstantVoltagePhase3', "1;0;72;7;0;255", 3)
    InstantCurrentPhase1 = CosemObject('InstantCurrentPhase1', "1;0;31;7;0;255", 3)
    InstantCurrentPhase2 = CosemObject('InstantCurrentPhase2', "1;0;51;7;0;255", 3)
    InstantCurrentPhase3 = CosemObject('InstantCurrentPhase3', "1;0;71;7;0;255", 3)
    InstantActivePowerPhase1 = CosemObject('InstantActivePowerPhase1', "1;0;35;7;0;255", 3)
    InstantActivePowerPhase2 = CosemObject('InstantActivePowerPhase2', "1;0;55;7;0;255", 3)
    InstantActivePowerPhase3 = CosemObject('InstantActivePowerPhase3', "1;0;75;7;0;255", 3)
    PhaseAnglePhase1 = CosemObject('PhaseAnglePhase1', "1;0;81;7;40;255", 3)
    PhaseAnglePhase2 = CosemObject('PhaseAnglePhase2', "1;0;81;7;51;255", 3)
    PhaseAnglePhase3 = CosemObject('PhaseAnglePhase3', "1;0;81;7;62;255", 3)
    
    