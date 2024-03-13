from typing import Union
from ..GenyUtil import Util, CommmandDataFrame, VoltageRange, CurrentRange, PowerSelector, ElementSelector
from ..GenyUtil import VoltageRangeError, CurrentRangeError

class GenySys:
    class Command:
        ONLINE = 0x80
        DISCONNECT_ONLINE = 0x81
        ADJUST_SPEED = 0x82
        CLOSE_OPEN_LOOP = 0x83
        SOURCE_FEEDBACK = 0x8f

    def __init__(self):
        self.commandDataFrame = CommmandDataFrame()

    # ONLINE
    def connect(self) -> list:
        '''
            Return data frame to login to test bench
        '''
        dataFrame = self.commandDataFrame.genDataFrame(GenySys.Command.ONLINE, [])
        return dataFrame

    # DISCONNECT ONLINE
    def disconnect(self) -> list:
        '''
            Return data frame to logout from test bench
        '''
        dataframe = self.commandDataFrame.genDataFrame(GenySys.Command.DISCONNECT_ONLINE, [])
        return dataframe