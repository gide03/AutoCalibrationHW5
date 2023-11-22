COSEM_LIST = {
    "0;128;96;14;80;255" : ["CalibrationData", 1, ],
    "0;128;96;14;82;255" : ["CalibrationMode", 1, ],
    "0;128;96;14;81;255" : ["MeterSetup", 1, ],
    "1;1;128;129;0;255" : ["SLBEnableDisable", 1, ],
    "1;1;128;130;0;255" : ["SLBObject", 1, ],
    "1;0;96;9;0;255" : ["temperature", 3, ],
    "1;0;35;7;0;255" : ["PowerActivePhase1", 3, ],
    "1;0;55;7;0;255" : ["PowerActivePhase2", 3, ],
    "1;0;75;7;0;255" : ["PowerActivePhase3", 3, ],
    "1;0;29;7;0;255" : ["PowerApparentImportPhase1", 3, ],
    "1;0;49;7;0;255" : ["PowerApparentImportPhase2", 3, ],
    "1;0;69;7;0;255" : ["PowerApparentImportPhase3", 3, ],
    "1;0;23;7;0;255" : ["PowerReactiveImportPhase1", 3, ],
    "1;0;43;7;0;255" : ["PowerReactiveImportPhase2", 3, ],
    "1;0;63;7;0;255" : ["PowerReactiveImportPhase3", 3, ],
    "1;0;33;7;0;255" : ["PowerFactorImportPhase1", 3, ],
    "1;0;53;7;0;255" : ["PowerFactorImportPhase2", 3, ],
    "1;0;73;7;0;255" : ["PowerFactorImportPhase3", 3, ],
    "1;0;31;7;0;255" : ["InstantCurrentPhase1", 3, ],
    "1;0;51;7;0;255" : ["InstantCurrentPhase2", 3, ],
    "1;0;71;7;0;255" : ["InstantCurrentPhase3", 3, ],
    "1;0;32;7;0;255" : ["InstantVoltagePhase1", 3, ],
    "1;0;52;7;0;255" : ["InstantVoltagePhase2", 3, ],
    "1;0;72;7;0;255" : ["InstantVoltagePhase3", 3, ],
}

METER_SERIAL_PORT = '/dev/ttyUSB4'

GENY_SERVER_IP = '10.23.40.185'

# Setting Geny, 230 Volt, 20 A, 60 degree, 3 Phase. 
GENY_PARAMETERS = {
    "V_R" : 230,
    "V_S" : 230,
    "V_T" : 230,
    "I_R" : 230,
    "I_S" : 230,
    "I_T" : 230,
    "Phase_R" : 20,
    "Phase_S" : 20,
    "Phase_T" : 20,
}