class hdlcParam:
    configSizeWindowRx = 0
    configSizeWindowTx = 0
    configSizeInfoFieldRx = 0
    configSizeInfoFieldTx = 0
    negotSizeWindowRx = 1
    negotSizeWindowTx = 1
    negotSizeInfoFieldRx = 128
    negotSizeInfoFieldTx = 128
    maxApduSize = 0

    def __init__(self, sizeWindowRx, sizeWindowTx, maxInfoField, max_apdu_size):
        self.configSizeWindowRx = sizeWindowRx
        self.configSizeWindowTx = sizeWindowTx
        self.configSizeInfoFieldRx = maxInfoField
        self.configSizeInfoFieldTx = maxInfoField
        self.maxApduSize = max_apdu_size
    
    def constructNegotResponse(self):
        tempBuff = []
        tempBuff.append(0x81)
        tempBuff.append(0x80)
        tempBuff.append(0x14)
        tempBuff.append(0x05)
        tempBuff.append(0x02)
        tempBuff.append(self.negotSizeInfoFieldTx >> 8)
        tempBuff.append(self.negotSizeInfoFieldTx & 0xFF)
        tempBuff.append(0x06)
        tempBuff.append(0x02)
        tempBuff.append(self.negotSizeInfoFieldRx >> 8)
        tempBuff.append(self.negotSizeInfoFieldRx & 0xFF)
        tempBuff.append(0x07)
        tempBuff.append(0x04)
        tempBuff.append(self.negotSizeWindowTx >> 24)
        tempBuff.append((self.negotSizeWindowTx >> 16) & 0xFF)
        tempBuff.append((self.negotSizeWindowTx >> 8) & 0xFF)
        tempBuff.append(self.negotSizeWindowTx & 0xFF)
        tempBuff.append(0x08)
        tempBuff.append(0x04)
        tempBuff.append(self.negotSizeWindowRx >> 24)
        tempBuff.append((self.negotSizeWindowRx >> 16) & 0xFF)
        tempBuff.append((self.negotSizeWindowRx >> 8) & 0xFF)
        tempBuff.append(self.negotSizeWindowRx & 0xFF)
        return tempBuff        

    def checkNegotParam(self, buffer):
        responseBuffer = []
        negotBuff = []
        negotLength = 0
        negotWindowRx = 0
        negotWindowTx = 0
        negotSizeInfoRx = 0
        negotSizeInfoTx = 0
        is_ok = False
        if len(buffer) > 0:
            if buffer[0] == 0x81:
                if buffer[1] == 0x80:
                    negotLength = buffer[2]
                    negotBuff = buffer[3:]
                    if len(negotBuff) == negotLength:
                        index_check = 0
                        is_ok = True
                        while index_check < negotLength and is_ok:
                            if negotBuff[index_check] == 0x05:
                                index_check += 1
                                if negotBuff[index_check] > 1:
                                    index_check += 1
                                    negotSizeInfoTx = negotBuff[index_check] << 8
                                    index_check += 1
                                    negotSizeInfoTx = negotSizeInfoTx + negotBuff[index_check]
                                    index_check += 1
                                else:
                                    index_check += 1
                                    negotSizeInfoTx = negotBuff[index_check]
                                    index_check += 1
                            elif negotBuff[index_check] == 0x06:
                                index_check += 1
                                if negotBuff[index_check] > 1:
                                    index_check += 1
                                    negotSizeInfoRx = negotBuff[index_check] << 8
                                    index_check += 1
                                    negotSizeInfoRx = negotSizeInfoRx + negotBuff[index_check]
                                    index_check += 1
                                else:
                                    index_check += 1
                                    negotSizeInfoRx = negotBuff[index_check]
                                    index_check += 1
                            elif negotBuff[index_check] == 0x07:
                                index_check += 2
                                negotWindowTx = negotBuff[index_check] << 24
                                index_check += 1
                                negotWindowTx = negotWindowTx + negotBuff[index_check] << 16
                                index_check += 1
                                negotWindowTx = negotWindowTx + negotBuff[index_check] << 8
                                index_check += 1
                                negotWindowTx = negotWindowTx + negotBuff[index_check]
                                index_check += 1
                            elif negotBuff[index_check] == 0x08:
                                index_check += 2
                                negotWindowRx = negotBuff[index_check] << 24
                                index_check += 1
                                negotWindowRx = negotWindowRx + negotBuff[index_check] << 16
                                index_check += 1
                                negotWindowRx = negotWindowRx + negotBuff[index_check] << 8
                                index_check += 1
                                negotWindowRx = negotWindowRx + negotBuff[index_check]
                                index_check += 1
                            else:
                                is_ok = False
            if is_ok:
                if negotSizeInfoTx == 0: negotSizeInfoTx = self.configSizeInfoFieldTx
                if negotSizeInfoRx == 0: negotSizeInfoRx = self.configSizeInfoFieldRx
                if negotWindowTx == 0: negotWindowTx = self.configSizeWindowTx
                if negotWindowRx == 0: negotWindowRx = self.configSizeWindowRx

                self.setNegotParam(negotWindowRx, negotWindowTx, negotSizeInfoRx, negotSizeInfoTx)
                responseBuffer = self.constructNegotResponse()
        else:
            if negotSizeInfoTx == 0: negotSizeInfoTx = self.configSizeInfoFieldTx
            if negotSizeInfoRx == 0: negotSizeInfoRx = self.configSizeInfoFieldRx
            if negotWindowTx == 0: negotWindowTx = self.configSizeWindowTx
            if negotWindowRx == 0: negotWindowRx = self.configSizeWindowRx

            self.setNegotParam(negotWindowRx, negotWindowTx, negotSizeInfoRx, negotSizeInfoTx)
            responseBuffer = self.constructNegotResponse()

        return responseBuffer
        

    def setNegotParam(self, inSizeWindowRx, inSizeWindowTx, inMaxInfoRx, inMaxInfoTx):
        if inSizeWindowRx > self.configSizeWindowRx:
            self.negotSizeWindowRx = self.configSizeWindowRx
        else:
            self.negotSizeWindowRx = inSizeWindowRx
        if inSizeWindowTx > self.configSizeWindowTx:
            self.negotSizeWindowTx = self.configSizeWindowTx
        else:
            self.negotSizeWindowTx = inSizeWindowTx
        if inMaxInfoRx > self.configSizeInfoFieldRx:
            self.negotSizeInfoFieldRx = self.configSizeInfoFieldRx
        else:
            self.negotSizeInfoFieldRx = inMaxInfoRx
        if inMaxInfoTx > self.configSizeInfoFieldTx:
            self.negotSizeInfoFieldTx = self.configSizeInfoFieldTx
        else:
            self.negotSizeInfoFieldTx = inMaxInfoTx