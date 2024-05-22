import pathlib
import site
import click
import sys

CURRENT_DIR = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_DIR)

from src.hvt import main as mainhvt
from src.syncRtc import main as mainRtc
from src.rtcCalibration import main as mainCalRtc
from src.calibrate_v2 import main as mainGainCal
from src.eraseFlash import main as mainEraseFlash

@click.command()
@click.option('--meterid', prompt='Enter meter id')
@click.option('--meterport', prompt='Enter meter port')
def main(meterid, meterport):
    while True:
        print(f'\nHW5.0 Calibration Tool. METER ID: "{meterid}" at {meterport}')
        print('MENU:')
        print('1. HVT')
        print('2. RTC calibration')
        print('3. Gain Calibration')
        print('4. Sync Clock')
        print('5. EraseFlash')

        try:
            sys.stdin.flush()
            choice = input('Choice (e for exit): ')
            if choice == 'e':
                print('Exit')
                break
            choice = int(choice)
        except:
            print('Invalid input\n\n')
        if choice == 1:
            mainhvt(meterid, meterport)
        elif choice == 2:
            mainCalRtc(meterid)
        elif choice == 3:
            tbport = input('Testbench port: ')
            mainGainCal(meterid, meterport, tbport)
        elif choice == 4:
            timediv = input("Enter timediv: ")
            timediv = int(timediv)
            mainRtc(meterid=meterid, comport=meterport, timediv=timediv)
        elif choice == 5:
            mainEraseFlash(meterid, meterport)
        else:
            print('IVALID INPUT')
            
if __name__ == '__main__':
    main()