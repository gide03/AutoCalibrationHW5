import pathlib
import site
import click
import sys
import json

CURRENT_DIR = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_DIR)

from lib.TestBench.GenyUtil import ElementSelector, PowerSelector, VoltageRange

from src.hvt import main as mainhvt
from src.syncRtc import main as mainRtc
from src.rtcCalibration import main as mainCalRtc
from src.calibrate_v3 import main as mainGainCal, initGenyClient
from src.eraseFlash import main as mainEraseFlash

def miscellaneous(meterid, meterport):
    testBench = None
    while True:
        print(f'\nHW5.0 Calibration Tool. METER ID: "{meterid}" at {meterport}')
        print('--- MISCELLANEOUS ---')
        print('1. Turn On Testbech (via serial)')
        print('2. Turn Off Testbench (via serial)')
        print('3. Readback Sampling (via serial)')
        try:
            choice = input('Choice (b for back): ')
            if choice == 'b':
                if testBench != None:
                    testBench.serialMonitor.stopMonitor()
                    del testBench
                break
            
            choice = int(choice)
        except:
            print('ERR: INVALID INPUT')
            continue
        
        if choice in (1,2, 3):
            if testBench == None:
                tbport = input('Testbench port: ')
                testBench = initGenyClient(tbport)
        
        if choice == 1:
            print('TURN ON TESTBENCH')
            testBench.setMode(1)
            testBench.setPowerSelector(PowerSelector._3P4W_ACTIVE)
            testBench.setElementSelector(ElementSelector.EnergyErrorCalibration._COMBINE_ALL)
            testBench.setVoltageRange(VoltageRange.YC99T_3C._380V)
            testBench.setPowerFactor(60, inDegree=True)
            testBench.setVoltage(230)
            testBench.setCurrent(40)
            testBench.setFrequency(50)
            testBench.apply()
        elif choice == 2:
            testBench.close()
        elif choice == 3:
            try:
                readBackSampling = testBench.readBackSamplingData()
                for samplingName in readBackSampling:
                    sampling = readBackSampling[samplingName]
                    readBackSampling[samplingName] = sampling.value
                print(json.dumps(readBackSampling, indent=2))
            except:
                pass
            


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
        print('100. Miscellaneous')

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
            try:
                mainhvt(meterid, meterport)
            except Exception as e:
                print(f'HTV Error, message: {str(e)}')
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
        elif choice == 100:
            miscellaneous(meterid, meterport)
        else:
            print('IVALID INPUT')
            
if __name__ == '__main__':
    main()