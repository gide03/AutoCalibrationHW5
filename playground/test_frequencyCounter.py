import pyvisa as visa
from datetime import datetime, timedelta

INSTRUMENT_PATH = 'USB0::0x0957::0x1707::MY63150298::INSTR'
HOW_LONG = 30 * 60 # in seconds

rm = visa.ResourceManager()
 
init = (
    "*RST\n"
    "*CLS\n"
    ":INP:IMP 1E6\n",
    ":INP2:IMP 1E6\n",
    ":INP:LEV:AUTO ON\n",
    ":INP2:LEV:AUTO ON\n",
    ":INP:COUP AC\n",
    ":INP2:COUP AC\n",
)
 
 
instrument = rm.open_resource(INSTRUMENT_PATH)
instrument.write("CONF:FREQ 4, (@1)")
instrument.write("INP:IMP 1000000")
instrument.write("INP:RANG 5")
instrument.write("INP:COUP AC")
instrument.write("INP:LEV -0.028")
instrument.write("INP:NREJ ON")

t = datetime.now()

import time
while datetime.now() - t < timedelta(minutes=HOW_LONG):
    try:
        with open('Frequency Read Log.txt', 'a') as f:
            instrument.write("*CLS")
            instrument.write("READ?")
        
            response = instrument.read()
            print(float(response[:-1]))
            print(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}, float(response[:-1])', file=f)
            time.sleep(1)
    except:
        pass
instrument.close()