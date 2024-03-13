from .hdlc_util import hdlcConstant, checkSequence, controlType, controlMask, pollFinalBit, llcInfo, frameError, segmentBit, rejectReason
from threading import Thread, Timer
from time import sleep
import json

class AddrSize:
	ONE_BYTE  = 1
	TWO_BYTE  = 2
	FOUR_BYTE = 4

class HdlcClass:
    rx_srcAddressLength = 0
    rx_destAddress = None
    rx_srcAddress = None
    rx_frameControl = None
    rx_frameInfo = []
    rx_seg_bit = None
    rx_pf_bit = None
    is_rx_segmented = False
    rx_segmented_info = []
    tx_segmented_info = []
    frame_counter_R = 0
    frame_counter_S = 0

    def __init__(self, hdlc_param, addr_size=AddrSize.FOUR_BYTE):
        self.cs_helper = checkSequence()
        self.hdlc_param = hdlc_param
        self.count_inactivity = 0
        self.stop_timer = False
        self.addr_size = addr_size

    def checkFrameFlag(self, buffer):
        checkType = frameError.FLAG_ERROR
        if len(buffer) < 2 * hdlcConstant.LengthFlag:
            checkType = frameError.FLAG_FIELD_ERROR
        
        startFlag = buffer[0]
        endFlag = buffer[len(buffer)-1]
        if(startFlag != hdlcConstant.Flag or endFlag != hdlcConstant.Flag):
            checkType = frameError.FLAG_ERROR
        else:
            checkType = frameError.NO_ERROR
        return checkType
    
    def checkFrameFCS(self, buffer):
        checkType = frameError.FCS_ERROR
        fcsIdx = len(buffer) - (hdlcConstant.LengthFcsField + hdlcConstant.LengthFlag)
        rx_frameCS = (buffer[fcsIdx + 1] << 8) | buffer[fcsIdx]

        calcBuffer = buffer[1:fcsIdx]
        if(self.cs_helper.checkCS(calcBuffer) == rx_frameCS):
            checkType = frameError.NO_ERROR
        else:
            checkType = frameError.FCS_ERROR
        return checkType
    
    def checkFrameFormatType(self, buffer, length):
        checkType = frameError.FORMAT_TYPE_ERROR
        if len(buffer) < (2 * hdlcConstant.LengthFlag + hdlcConstant.LengthFrameFormatField):
            checkType = frameError.FRAME_FORMAT_FIELD_ERROR
        frameFormat = (buffer[1] << 8) | buffer[2]
        if((frameFormat & hdlcConstant.FormatType) == hdlcConstant.FormatType):
            if(frameFormat & (hdlcConstant.FormatType >> 1) == 0):
                checkType = frameError.NO_ERROR
        frameLength = frameFormat & hdlcConstant.MaskFrameLength
        if(length - (2 * hdlcConstant.LengthFlag) != frameLength):
            checkType = frameError.FRAME_LENGTH_ERROR
        else:
            checkType = frameError.NO_ERROR
        if checkType == frameError.NO_ERROR:
            if (frameFormat & hdlcConstant.PositionSegmentBit) == hdlcConstant.PositionSegmentBit:
                self.rx_seg_bit = segmentBit.SB_ON
            else:
                self.rx_seg_bit = segmentBit.SB_OFF
        return checkType

    def getSrcAddressLength(self, buffer):
        self.rx_srcAddressLength = 1
        for i in range(hdlcConstant.LengthServerAddressField):
            if buffer[hdlcConstant.OffsetSrcAddress + i] & hdlcConstant.MaskExtendedAddress != hdlcConstant.MaskExtendedAddress:
                self.rx_srcAddressLength = self.rx_srcAddressLength + 1
            else:
                break
        if self.rx_srcAddressLength == 3:
            return frameError.SOURCE_ADDR_FIELD_ERROR
        elif self.rx_srcAddressLength > 4:
            return frameError.SOURCE_ADDR_FIELD_ERROR
        else:
            return frameError.NO_ERROR

    def getSrcAddress(self, buffer):
        if self.rx_srcAddressLength == 1:
            self.rx_srcAddress = (buffer[hdlcConstant.OffsetSrcAddress] >> 1) << 16
        elif self.rx_srcAddressLength == 2:
            srcAddressTemp = buffer[hdlcConstant.OffsetSrcAddress] << 8
            srcAddressTemp = buffer[hdlcConstant.OffsetSrcAddress + 1] + srcAddressTemp
            upperHdlcAddress = (srcAddressTemp & 0x0000FF00) >> 9
            lowerHdlcAddress = (srcAddressTemp & 0x000000FF) >> 1
            if lowerHdlcAddress == 0x7F:
                lowerHdlcAddress = srcAddressTemp
            self.rx_srcAddress = (upperHdlcAddress << 16) | lowerHdlcAddress
        elif self.rx_srcAddressLength == 4:
            srcAddressTemp = buffer[hdlcConstant.OffsetSrcAddress] << 24
            srcAddressTemp = (buffer[hdlcConstant.OffsetSrcAddress + 1] << 16) + srcAddressTemp
            srcAddressTemp = (buffer[hdlcConstant.OffsetSrcAddress + 2] << 8) + srcAddressTemp
            srcAddressTemp = buffer[hdlcConstant.OffsetSrcAddress + 3] + srcAddressTemp
            upperHdlcAddress = (srcAddressTemp & 0xFF000000) >> 25
            upperHdlcAddress = ((srcAddressTemp & 0x00FF0000) >> 17) + upperHdlcAddress
            lowerHdlcAddress = ((srcAddressTemp & 0x0000FF00) >> 9) << 7
            lowerHdlcAddress = ((srcAddressTemp & 0x000000FF) >> 1) + lowerHdlcAddress
            # if lowerHdlcAddress == hdlcConstant.ValueAddressServerBroadcastTwoBytes:
            #     lowerHdlcAddress = srcAddressTemp
            self.rx_srcAddress = (upperHdlcAddress << 16) | lowerHdlcAddress

    def checkSourceAddress(self, buffer, i_deviceAddress):
        checkType = frameError.SOURCE_ADDR_ERROR
        if len(buffer) < (2 * hdlcConstant.LengthFlag + hdlcConstant.LengthFrameFormatField + 1):
            checkType = frameError.SOURCE_ADDR_FIELD_ERROR
        
        if checkType != frameError.SOURCE_ADDR_FIELD_ERROR:
            checkType = self.getSrcAddressLength(buffer)
            if(checkType == frameError.NO_ERROR):
                self.getSrcAddress(buffer)
                if (self.rx_srcAddress & hdlcConstant.MaskPhysicalDeviceAddress) == hdlcConstant.ValueAddressServerBroadcastTwoBytes:
                    checkType = frameError.NO_ERROR
                else:
                    if ((self.rx_srcAddress & hdlcConstant.MaskLogicalDeviceAddress) >> 16) == 1: # should not only 1 later
                        if self.rx_srcAddressLength > 1:
                            if (self.rx_srcAddress & hdlcConstant.MaskPhysicalDeviceAddress) == i_deviceAddress:
                                checkType = frameError.NO_ERROR
                            else:
                                checkType = frameError.PHYSICAL_DEVICE_ADDRESS_ERROR
                        elif self.rx_srcAddressLength == 1:
                            checkType = frameError.NO_ERROR
                    else:
                        checkType = frameError.DEST_ADDR_ERROR
        return checkType

    def checkDestAddress(self, buffer):
        checkType = frameError.DEST_ADDR_FIELD_ERROR
        if len(buffer) >= (2 * hdlcConstant.LengthFlag + hdlcConstant.LengthFrameFormatField + self.rx_srcAddressLength + 1):
            destAddress = buffer[hdlcConstant.OffsetDestAddress]
            if (destAddress & hdlcConstant.MaskExtendedAddress) == hdlcConstant.MaskExtendedAddress:
                self.rx_destAddress = destAddress >> 1
                checkType = frameError.NO_ERROR
            else:
                checkType = frameError.DEST_ADDR_ERROR

        if checkType == frameError.NO_ERROR:
            if self.rx_destAddress == hdlcConstant.ValueAddressNoClient:
                checkType = frameError.DEST_ADDR_ERROR
            else:
                checkType = frameError.NO_ERROR	
        return checkType

    def getControlType(self):
        if (self.rx_frameControl & hdlcConstant.MaskControlTypeI) == controlMask.INFO:
            return controlType.INFO
        elif (self.rx_frameControl & hdlcConstant.MaskControlTypeSup) == controlMask.RR:
            return controlType.RR
        elif (self.rx_frameControl & hdlcConstant.MaskControlTypeSup) == controlMask.RNR:
            return controlType.RNR
        elif (self.rx_frameControl & hdlcConstant.MaskControlTypeOther) == controlMask.SNRM:
            return controlType.SNRM
        elif (self.rx_frameControl & hdlcConstant.MaskControlTypeOther) == controlMask.DISC:
            return controlType.DISC
        elif (self.rx_frameControl & hdlcConstant.MaskControlTypeOther) == controlMask.UA:
            return controlType.UA
        elif (self.rx_frameControl & hdlcConstant.MaskControlTypeOther) == controlMask.DM:
            return controlType.DM
        elif (self.rx_frameControl & hdlcConstant.MaskControlTypeOther) == controlMask.FRMR:
            return controlType.FRMR
        elif (self.rx_frameControl & hdlcConstant.MaskControlTypeOther) == controlMask.UI:
            return controlType.UI
        else:
            return controlType.UNKNOWN

    def checkControlType(self, buffer):
        checkType = frameError.CONTROL_FIELD_ERROR
        if len(buffer) >= (2 * hdlcConstant.LengthFlag + hdlcConstant.LengthFrameFormatField + self.rx_srcAddressLength + hdlcConstant.LengthClientAddressField + 1):
            self.rx_frameControl = buffer[hdlcConstant.OffsetDestAddress + self.rx_srcAddressLength + hdlcConstant.LengthClientAddressField]
            checkType = frameError.NO_ERROR
            # if checkType == frameError.NO_ERROR:
            #     checkControl = self.getControlType()
                # if checkControl != controlType.UI and checkControl != controlType.DISC:
                #     if (self.rx_destAddress & (hdlcConstant.MaskPhysicalDeviceAddress << 16)) == (hdlcConstant.ValueAddressServerBroadcastTwoBytes << 16):
                #         checkType = frameError.DEST_ADDR_ERROR
                #     if (self.rx_destAddress & hdlcConstant.MaskPhysicalDeviceAddress) == hdlcConstant.ValueAddressServerBroadcastTwoBytes:
                #         checkType = frameError.DEST_ADDR_ERROR
        return checkType

    def getRx_nR(self, checkControl):
        nR = 0xFF
        if checkControl == controlType.INFO or checkControl == controlType.RR or checkControl == controlType.RNR:
            nR = (self.rx_frameControl & hdlcConstant.MaskNr) >> 5
        return nR
    
    def getRx_nS(self, checkControl):
        nS = 0xFF
        if checkControl == controlType.INFO:
            nS = (self.rx_frameControl & hdlcConstant.MaskNs) >> 1
        return nS

    def checkSequenceRx(self, checkControl):
        result = False
        if checkControl == controlType.INFO:
            if self.getRx_nS(checkControl) == self.frame_counter_R:
                result = True
        if checkControl == controlType.RR or checkControl == controlType.RNR:
            if self.getRx_nR(checkControl) == self.frame_counter_S:
                result = True
        return result

    def checkFrameHCS(self, buffer):
        checkType = frameError.HCS_ERROR
        hcsIdx = (2 * hdlcConstant.LengthFlag + hdlcConstant.LengthFrameFormatField + self.rx_srcAddressLength + hdlcConstant.LengthClientAddressField + hdlcConstant.LengthControlField)-1
        rx_headerCS = (buffer[hcsIdx + 1] << 8) | buffer[hcsIdx]
        calcBuffer = buffer[1:hcsIdx]
        
        if(self.cs_helper.checkCS(calcBuffer) == rx_headerCS):
            checkType = frameError.NO_ERROR
        return checkType
    
    def checkInformationFrame(self, buffer):
        checkType = frameError.NO_ERROR
        frameHasInformation = False
        length = len(buffer) - (2 * hdlcConstant.LengthFlag + hdlcConstant.LengthFrameFormatField + self.rx_srcAddressLength + hdlcConstant.LengthClientAddressField + hdlcConstant.LengthControlField)
        if length == hdlcConstant.LengthFcsField:
            frameHasInformation = False
        elif length > (hdlcConstant.LengthHcsField + hdlcConstant.LengthFcsField):
            startInfoIdx = hdlcConstant.LengthFlag + hdlcConstant.LengthFrameFormatField + self.rx_srcAddressLength + hdlcConstant.LengthClientAddressField + hdlcConstant.LengthControlField + hdlcConstant.LengthHcsField
            endInfoIdx = len(buffer) - (hdlcConstant.LengthFcsField + hdlcConstant.LengthFlag)
            self.rx_frameInfo = buffer[startInfoIdx:endInfoIdx]
            frameHasInformation = True
        else:
            checkType = frameError.INFORMATION_ERROR

        if frameHasInformation:
            checkType = self.checkFrameHCS(buffer)
        return checkType

    def getPollFinalBit(self):
        if (self.rx_frameControl & hdlcConstant.PositionPfBit) == hdlcConstant.PositionPfBit:
            self.rx_pf_bit = pollFinalBit.PF_ON
        else:
            self.rx_pf_bit = pollFinalBit.PF_OFF
    
    def checkRxHdlcFrame(self, buffer, meterAddress):
        error = self.checkFrameFlag(buffer)

        if error == frameError.NO_ERROR:
            error = self.checkFrameFCS(buffer)
        if error == frameError.NO_ERROR:
            error = self.checkFrameFormatType(buffer, len(buffer))
        if error == frameError.NO_ERROR:
            error = self.checkDestAddress(buffer)
        if error == frameError.NO_ERROR:
            error  = self.checkSourceAddress(buffer, meterAddress)
        if error == frameError.NO_ERROR:
            error = self.checkControlType(buffer)
        if error == frameError.NO_ERROR:
            error = self.checkInformationFrame(buffer)
        if error == frameError.NO_ERROR:
            self.getPollFinalBit()
        return error

    def resetFrameCounter(self):
        self.frame_counter_R = 0
        self.frame_counter_S = 0

    def getTxFrameFormat(self, segBit, frameLength):
        frameFormat = 0
        frameFormat = frameFormat & hdlcConstant.MaskFrameLength
        frameFormat = frameFormat | hdlcConstant.FormatType

        if segBit == segmentBit.SB_ON:
            frameFormat = frameFormat | hdlcConstant.PositionSegmentBit
        else:
            frameFormat = frameFormat & (~hdlcConstant.PositionSegmentBit)
        
        frameLength = frameLength & hdlcConstant.MaskFrameLength
        frameFormat = frameFormat & (~hdlcConstant.MaskFrameLength)
        frameFormat = frameFormat | frameLength
        return frameFormat

    def getTxSourceAddress(self, sourceAddr):
        return (sourceAddr << 1) | hdlcConstant.MaskExtendedAddress

    def getTxDestAddress(self, destAddr):
        upperHdlcAddress = destAddr >> 16
        lowerHdlcAddress = destAddr & hdlcConstant.MaskPhysicalDeviceAddress

        destAddress = 0
        if self.addr_size == AddrSize.ONE_BYTE:
            if upperHdlcAddress > 127:
                destAddress = ((upperHdlcAddress & 0x007F) << 1) | hdlcConstant.MaskExtendedAddress
                destAddress = ((upperHdlcAddress >> 7) << 9) + destAddress
            else:
                destAddress = (upperHdlcAddress << 1) | hdlcConstant.MaskExtendedAddress
        else:
            if lowerHdlcAddress > 127:
                destAddress = ((lowerHdlcAddress & 0x007F) << 1) | hdlcConstant.MaskExtendedAddress
                destAddress = ((lowerHdlcAddress >> 7) << 9) + destAddress
            else:
                destAddress = (lowerHdlcAddress << 1) | hdlcConstant.MaskExtendedAddress

            if upperHdlcAddress > 127:
                destAddress = ((upperHdlcAddress & 0x007F) << 17) + destAddress
                destAddress = ((upperHdlcAddress >> 7) << 9) + destAddress
            else:
                if self.addr_size == AddrSize.TWO_BYTE:
                    destAddress = (upperHdlcAddress << 9) + destAddress
                elif self.addr_size == AddrSize.FOUR_BYTE:
                    destAddress = (upperHdlcAddress << 17) + destAddress
        return destAddress
    
    def getTxFrameControl(self, checkControl, setControl, nR, nS, pfBit):
        frameControl = 0
        if checkControl == controlType.INFO or checkControl == controlType.RR or checkControl == controlType.RNR:
            frameControl = frameControl & (~hdlcConstant.MaskNr)
            frameControl = frameControl | (nR << 5)

        if checkControl == controlType.INFO:
            frameControl = frameControl & (~hdlcConstant.MaskNs)
            frameControl = frameControl | ((nS & (hdlcConstant.MaskNs >> 1)) << 1)

        if setControl == controlType.INFO:
            frameControl = frameControl & (hdlcConstant.MaskNr | hdlcConstant.PositionPfBit | hdlcConstant.MaskNs)
        elif setControl == controlType.RR:
            frameControl = frameControl & (hdlcConstant.MaskNr | hdlcConstant.PositionPfBit)
            frameControl = frameControl | controlMask.RR
        elif setControl == controlType.RNR:
            frameControl = frameControl & (hdlcConstant.MaskNr | hdlcConstant.PositionPfBit)
            frameControl = frameControl | controlMask.RNR
        elif setControl == controlType.SNRM:
            frameControl = frameControl & hdlcConstant.PositionPfBit
            frameControl = frameControl | controlMask.SNRM
        elif setControl == controlType.DISC:
            frameControl = frameControl & hdlcConstant.PositionPfBit
            frameControl = frameControl | controlMask.DISC
        elif setControl == controlType.UA:
            frameControl = frameControl & hdlcConstant.PositionPfBit
            frameControl = frameControl | controlMask.UA
        elif setControl == controlType.DM:
            frameControl = frameControl & hdlcConstant.PositionPfBit
            frameControl = frameControl | controlMask.DM
        elif setControl == controlType.FRMR:
            frameControl = frameControl & hdlcConstant.PositionPfBit
            frameControl = frameControl | controlMask.FRMR
        elif setControl == controlType.UI:
            frameControl = frameControl & hdlcConstant.PositionPfBit
            frameControl = frameControl | controlMask.UI
        
        if (pfBit == pollFinalBit.PF_ON):
            frameControl = frameControl | hdlcConstant.PositionPfBit
        else:
            frameControl = frameControl & (~hdlcConstant.PositionPfBit)

        return frameControl

    def getTxInformationField(self, infoBuffer):
        frameInformation = []
        if len(self.tx_segmented_info) == 0:
            frameInformation.append(llcInfo.sapCommand)
            frameInformation.append(llcInfo.sapCommand)
            frameInformation.append(llcInfo.quality)
        
        frameInformation += infoBuffer

        if len(frameInformation) > self.hdlc_param.negotSizeInfoFieldTx:
            self.tx_segmented_info = frameInformation[self.hdlc_param.negotSizeInfoFieldTx:]
            frameInformation = frameInformation[:self.hdlc_param.negotSizeInfoFieldTx]
        else:
            self.tx_segmented_info = []

        return frameInformation
    
    def getTxHdlcFrame(self, infoBuffer, segBit, destAddr, sourceAddr, checkControl, setControl, nR, nS, pfBit):
        tempBuff = []
        tempBuff.append(0x7E)

        tx_frameInfo = infoBuffer
        frameLength = 0
        infoLength = len(tx_frameInfo)
        if infoLength > 0:
            frameLength = hdlcConstant.LengthHdlcHeaderWithoutInfo + self.addr_size + hdlcConstant.LengthHcsField + infoLength + hdlcConstant.LengthFcsField
        else:
            frameLength = hdlcConstant.LengthHdlcHeaderWithoutInfo + self.addr_size + hdlcConstant.LengthHcsField

        tx_frameFormat = self.getTxFrameFormat(segBit, frameLength)
        tempBuff.append(tx_frameFormat >> 8)
        tempBuff.append(tx_frameFormat & 0xFF)

        tx_destAddress = self.getTxDestAddress(destAddr)
        if self.addr_size == AddrSize.FOUR_BYTE:
            tempBuff.append(int((tx_destAddress & 0xFF000000) >> 24))
            tempBuff.append(int((tx_destAddress & 0x00FF0000) >> 16))
            tempBuff.append(int((tx_destAddress & 0x0000FF00) >> 8))
            tempBuff.append(int(tx_destAddress & 0x000000FF))
        elif self.addr_size == AddrSize.TWO_BYTE:
            tempBuff.append(int((tx_destAddress & 0x0000FF00) >> 8))
            tempBuff.append(int(tx_destAddress & 0x000000FF))
        elif self.addr_size == AddrSize.ONE_BYTE:
            tempBuff.append(int(tx_destAddress & 0x000000FF))
        tx_srcAddress = self.getTxSourceAddress(sourceAddr)
        tempBuff.append(tx_srcAddress)

        tx_frameControl = self.getTxFrameControl(checkControl, setControl, nR, nS, pfBit)
        tempBuff.append(tx_frameControl)

        hcsFrame = self.cs_helper.checkCS(tempBuff[1:])
        tempBuff.append(hcsFrame & 0xFF)
        tempBuff.append(hcsFrame >> 8)

        if setControl != controlType.RR and setControl != controlType.RNR and len(tx_frameInfo) != 0:
            tempBuff += tx_frameInfo
            fcsFrame = self.cs_helper.checkCS(tempBuff[1:])
            tempBuff.append(fcsFrame & 0xFF)
            tempBuff.append(fcsFrame >> 8)

        tempBuff.append(0x7E)
        return tempBuff
