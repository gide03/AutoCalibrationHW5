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
    CalMode = CosemObject('CalMode', '0;128;96;14;82;255', 1)
    FlashErase = CosemObject('FlashErase', '1;1;128;130;3;255', 1)
    BatteryVoltage = CosemObject('BatteryVoltage', '0;0;128;130;4;255', 3)
    Clock = CosemObject('Clock', '0;0;1;0;0;255', 8)
    PowerFactorL1 = CosemObject('PowerFactorL1', '1;0;33;7;0;255', 3)
    PowerFactorL2 = CosemObject('PowerFactorL2', '1;0;53;7;0;255', 3)
    PowerFactorL3 = CosemObject('PowerFactorL3', '1;0;73;7;0;255', 3)
    InstantFrequency = CosemObject('InstantFrequency', '1;0;14;7;0;255', 3)
    Temperature = CosemObject('Temperature', '1;0;96;9;0;255', 3)
    InstantFrequency = CosemObject('InstantFrequency', '1;0;14;7;0;255', 3)
    
    # refer C:\Repo\HW_5.0\FW\common\CommonMetrologyDef.h
    KYZ1Configuration = CosemObject('KYZ1Configuration', '0;128;96;6;21;255', 1)
    KYZ2Configuration = CosemObject('KYZ2Configuration', '0;128;96;6;22;255', 1)
    KYZ3Configuration = CosemObject('KYZ3Configuration', '0;128;96;6;23;255', 1)
    KYZ4Configuration = CosemObject('KYZ4Configuration', '0;128;96;6;24;255', 1)
    KYZ5Configuration = CosemObject('KYZ5Configuration', '0;128;96;6;25;255', 1)
    
    LED1Configuration = CosemObject('LED1Configuration', '0;128;96;6;8;255', 1)
    LED2Configuration = CosemObject('LED2Configuration', '0;128;96;6;20;255', 1)
    
    # TODO: Confirm to pak Aji about load control
    # TODO: Confirm to pak Yonas the list of configuration
    
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
    
    
