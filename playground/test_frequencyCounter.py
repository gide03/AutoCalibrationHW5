import pyvisa as visa
import click
from datetime import datetime, timedelta

INSTRUMENT_PATH = 'USB0::0x14EB::0x0090::389645::INSTR'
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
 
class UnknownVendor(Exception):
    def __init__(self, message):
        super.__init__(message)

@click.command()
@click.option('--vendor', prompt='Instrument vendor')
def main(vendor):
    instrument = rm.open_resource(INSTRUMENT_PATH)
    if vendor == 'PENDULUM':
        instrument.write("CONF:FREQ 4, (@1)")
        # instrument.write("INP:IMP 1000000")
        # instrument.write("INP:RANG 5")
        instrument.write("INP:COUP DC")
        instrument.write("INP:LEV 0.1")
        # instrument.write("INP:NREJ ON")
    elif vendor == 'KEYSIGHT':
        instrument.write("CONF:FREQ 4, (@1)")
        instrument.write("INP:IMP 1000000")
        instrument.write("INP:RANG 5")
        instrument.write("INP:COUP DC")
        instrument.write("INP:LEV 0.1")
        instrument.write("INP:NREJ ON")
    else:
        raise UnknownVendor(f'Vendor available: PENDULUM, KEYSIGHT')
        
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
        except KeyboardInterrupt:
            print('Keyboard interrupt')
            break
        except:
            pass
    instrument.close()

if __name__ == "__main__":
    main()