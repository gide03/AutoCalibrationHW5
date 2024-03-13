from lib.DLMS_Client.dlms_service.dlms_service import mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient

import logging
logger = logging.getLogger(__name__)

def login(dlmsClient:DlmsCosemClient, authKey:str='', mechanism:int=mechanism.LOWEST_LEVEL):
    try:
        logger.debug('Login to meter')
        loginResult = dlmsClient.client_login(authKey, mechanism)
        logger.debug(f'Login result - {loginResult}')
        return loginResult
    except Exception as e:
        logger.debug(str(e))
        return False

def logout(dlmsClient:DlmsCosemClient):
    try:
        logger.debug('Logout from meter')
        dlmsClient.client_logout()    
        return True
    except Exception as e:
        logger.debug(str(e))
        return False