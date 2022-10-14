import logging
import config
import sys 

from PyQt5.QtWidgets import * 
from PyQt5 import uic 
from PyQt5.QtCore import *

from api.api_camfit import requestGetData
from util import getTimeStamp

#UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다. 
form_class = uic.loadUiType("ui/resrvUi.ui")[0] 

class WindowClass(QMainWindow, form_class) : 
    def __init__(self) : 
        super().__init__() 
        self.setupUi(self) 

        #각 버튼에 대한 함수 연결 
        self.pushButton.clicked.connect(self.func_start)
        self.searchThr = SearchThread(parent=self)
        self.statusBar.showMessage('준비')

    def func_start(self) :
        self.pushButton.setDisabled(True)
        self.searchThr.start()

class SearchThread(QThread): 
    def __init__(self, parent): 
        super().__init__(parent) 
        self.parent = parent 
    
    def run(self): 
        text = self.parent.lineEdit.text()
        
        '''
        1. 캠핑장 검색
        '''
        apiUri = '/v2/search/count'
        getParams = {
            'search': text,
        }
        logger.info(" == Search Text : {} ".format(text))
        response = requestGetData(apiUri, None, getParams)
        
        if -1 != response :
            logger.info(" == Search Response Count : {} ".format(response.text))
            if int(response.text) > 0 :
                apiUri = '/v2/search'
                getParams = {
                    'search': text,
                    'skip' : 0,
                    'limit' : response.text
                }
                response = requestGetData(apiUri, None, getParams)
                if -1 != response :
                    response = response.json()
                    for idx, data in enumerate(response) :
                        logger.info(" == Response idx, name, Camp ID : {}, {}, {} ".format(idx, data['name'], data['_id']))
                        # 임시 설정 값
                        zone_id = data['_id']
        
                '''
                2. 선택한 캠핑장 Zone 정보를 검색 
                '''
                apiUri = '/v1/camps/zones/count'
                response = requestGetData(apiUri, zone_id)
                if -1 != response :
                    logger.info(" == Camp Response Count : {} ".format(response.text))
                    
                    params_time = dict()
                    # 임시설정 값
                    params_time['stime'] = '2022-10-20'
                    params_time['etime'] = '2022-10-21'

                    if -1 != getTimeStamp(params_time) :           
                        apiUri = '/v1/camps/zones'
                        '''
                            3가지 값은 caculate 전에는 고정
                            'adult': 2,
                            'teen': 0,
                            'child': 0,
                        '''
                        getParams = {
                            'id': zone_id,
                            'limit' : response.text,
                            'adult': 2,
                            'teen': 0,
                            'child': 0,
                            'startTimestamp': params_time['stime'],
                            'endTimestamp' : params_time['etime'],
                            'skip' : 0,
                        }
                        response = requestGetData(apiUri, zone_id, getParams)
                        if -1 != response :
                            response = response.json()
                            for idx, data in enumerate(response) :
                                logger.info(" == Camp Response idx, name, Zone ID , isUnavailable : {}, {}, {}, {} ".format(idx, data['name'], data['id'], data['isUnavailable']))
                                # 임시 설정 값
                                if data['isUnavailable'] == False :
                                    site_id = data['id']
                
                '''
                3. 선택한 Zone의 Site 정보를 검색 
                '''
                if site_id != None :
                    apiUri = '/v1/sites/count'
                    response = requestGetData(apiUri, site_id)
                    if -1 != response :
                        logger.info(" == Site Response Count : {} ".format(response.text))
                        
                        apiUri = '/v1/sites'
                        getParams = {
                            'startTimestamp': params_time['stime'],
                            'endTimestamp' : params_time['etime']
                        }
                        
                        response = requestGetData(apiUri, site_id, getParams)
                        if -1 != response :
                            response = response.json()
                            for idx, data in enumerate(response) :
                                logger.info(" == Site Response idx, id, name, isAvailable : {}, {}, {}, {} ".format(idx, data['id'], data['name'], data['isAvailable']))
                                # 임시 설정 값
                                if data['isAvailable'] :
                                    reserv_id = data['id']
                    '''
                    4. 선택한 Site 예약전 서비스 확인 및 계산
                    '''
                    apiUri = '/v1/zones/services'
                    getParams = {
                        'id': site_id,
                        'limit' : 100,
                        'skip' : 0
                    }
                    response = requestGetData(apiUri, site_id, getParams)
                    if -1 != response :
                        response = response.json()
                        service_obj = dict()
                        for idx, data in enumerate(response) :
                            logger.info(" == Service Response idx, id : {}, {}, {} ".format(idx, data['id'], data['name']))
                       

                    '''
                    5. 선택한 Site 예약
                    '''

        self.parent.statusBar.showMessage('처리완료')
        self.parent.pushButton.setEnabled(True)
     
if __name__ == '__main__' :
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(config.LOG_PATH)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(" === START Camping-Reservation Program === ")

    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show() 
    app.exec_()
    
    logger.info(" === END Camping-Reservation Program === ")
    
    
    # apiUri = '/v2/search/count'
    # getParams = {
    #     'search': '트멍',
    # }
        
    # apiUri = '/v2/search'
    # getParams = {
    #     'search': '트멍',
    #     'skip' : 0,
    #     'limit' : 20
    # }
    
    # requestGetData(apiUri, getParams)
