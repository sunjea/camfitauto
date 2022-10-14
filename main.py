import logging
import config
import sys 

from PyQt5.QtWidgets import * 
from PyQt5 import uic 
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from api.api_camfit import requestGetData
from util import getTimeStamp
from database.db_helper import createTable, insertCampingInfo, getSelectCampId, insertZoneInfo, getSelectZoneId, insertSiteInfo
from enums import SEND_MSG_STS, THREAD_MODE

#UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다. 
form_class = uic.loadUiType("ui/resrvUi.ui")[0] 
_thr_mode = None

class WindowClass(QMainWindow, form_class) : 
    def __init__(self) : 
        super().__init__() 
        self.setupUi(self) 

        createTable()

        #각 버튼에 대한 함수 연결 
        self.pushButton.clicked.connect(self.campingListSearch)
        self.pushButton_2.clicked.connect(self.campingReservation)
        self.listWidget.itemClicked.connect(self.campingListClicked)
        self.listWidget_2.itemClicked.connect(self.zoneListClicked)
        self.listWidget_3.itemClicked.connect(self.siteListClicked)

        self.pushButton_2.setDisabled(True)
        self.searchThr = SearchThread(parent=self)
        self.statusBar.showMessage('준비')

    def campingListSearch(self) :
        global _thr_mode
        _thr_mode = THREAD_MODE.CAMP_LIST
        
        self.pushButton_2.setDisabled(True)
        self.pushButton.setDisabled(True)
        self.searchThr.start()

    def campingListClicked(self) :
        global _thr_mode
        _thr_mode = THREAD_MODE.ZONE_LIST
        self.pushButton_2.setDisabled(True)
        self.pushButton.setDisabled(True)
        self.searchThr.start()

    def zoneListClicked(self) :
        global _thr_mode
        _thr_mode = THREAD_MODE.SITE_LIST
        self.pushButton_2.setDisabled(True)
        self.pushButton.setDisabled(True)
        self.searchThr.start()

    def siteListClicked(self) :
        self.pushButton_2.setEnabled(True)

    def campingReservation(self):

        pass
        
class SearchThread(QThread): 
    def __init__(self, parent): 
        super().__init__(parent) 
        self.parent = parent 
    
    def run(self): 
        if _thr_mode == THREAD_MODE.CAMP_LIST :
            text = self.parent.lineEdit.text()
            
            '''
            1. 캠핑장 검색 후 캠핑장 리스트를 DB 저장
            '''
            apiUri = '/v2/search/count'
            getParams = {
                'search': text,
            }
            logger.info(f" == Search Text : {text} ")
            response = requestGetData(apiUri, None, getParams)
            status: int = response.status
            data: dict = response.data
            if 200 == status and int(data) > 0 :
                logger.info(f" == CampList Count : {data} ")
                apiUri = '/v2/search'
                getParams = {
                    'search': text,
                    'skip' : 0,
                    'limit' : data
                }
                response = requestGetData(apiUri, None, getParams)
                status: int = response.status
                data: dict = response.data
                if 200 == status :
                    self.parent.listWidget.clear()
                    for idx, rs in enumerate(data) :
                        logger.info(f"== CampList idx, name, Camp ID : {idx}, {rs['name']}, {rs['_id']}")                    
                        self.parent.listWidget.addItem(rs['name'])
                        insertCampingInfo(idx, rs['name'], rs['_id'])

        elif _thr_mode == THREAD_MODE.ZONE_LIST :

            '''
            2. 선택한 캠핑장 정보를 DB 검색 후 _id 값으로 Zone 정보 조회
               Zone 리스트 DB 저장
            '''
            camp_id = getSelectCampId(self.parent.listWidget.currentRow(), self.parent.listWidget.currentItem().text())
            
            apiUri = '/v1/camps/zones/count'
            response = requestGetData(apiUri, camp_id)
            status: int = response.status
            data: dict = response.data
            if 200 == status and int(data) > 0 :
                logger.info(f" == ZoneList Count : {data} ")
                
                params_time = dict()
                # 사이트 정보를가져오기 위한 임의 날짜 값
                params_time['stime'] = '2022-1-1'
                params_time['etime'] = '2022-1-2'

                if -1 != getTimeStamp(params_time) :           
                    apiUri = '/v1/camps/zones'
                    '''
                        3가지 값은 caculate 전에는 고정
                        'adult': 2,
                        'teen': 0,
                        'child': 0,
                    '''
                    getParams = {
                        'id': camp_id,
                        'limit' : data,
                        'adult': 2,
                        'teen': 0,
                        'child': 0,
                        'startTimestamp': params_time['stime'],
                        'endTimestamp' : params_time['etime'],
                        'skip' : 0,
                    }
                    response = requestGetData(apiUri, camp_id, getParams)
                    status: int = response.status
                    data: dict = response.data
                    if 200 == status :
                        self.parent.listWidget_2.clear()
                        for idx, rs in enumerate(data) :
                            logger.info(f" == ZoneList Response idx, name, Zone ID , isUnavailable : {idx}, {rs['name']}, {rs['id']}, {rs['isUnavailable']} ")
                            self.parent.listWidget_2.addItem(rs['name'])
                            insertZoneInfo(idx, rs['name'], rs['id'])

        elif _thr_mode == THREAD_MODE.SITE_LIST :
            
            '''
            3. 선택한 Zone 정보를 DB 검색 후 _id 값으로 Site 정보 조회
               Site 리스트 DB 저장 
            '''
            zone_id = getSelectZoneId(self.parent.listWidget_2.currentRow(), self.parent.listWidget_2.currentItem().text())
                  
            apiUri = '/v1/sites'
            params_time = dict()
            # 사이트 정보를가져오기 위한 임의 날짜 값
            params_time['stime'] = '2022-1-1'
            params_time['etime'] = '2022-1-2'

            if -1 != getTimeStamp(params_time) :  
                getParams = {
                    'startTimestamp': params_time['stime'],
                    'endTimestamp' : params_time['etime']
                }
                    
                response = requestGetData(apiUri, zone_id, getParams)
                status: int = response.status
                data: dict = response.data
                if 200 == status :
                    self.parent.listWidget_3.clear()
                    for idx, rs in enumerate(data) :
                        logger.info(f" == Site Response idx, id, name, isAvailable : {idx}, {rs['id']}, {rs['name']}, {rs['isAvailable']} ")
                        self.parent.listWidget_3.addItem(rs['name'])
                        insertSiteInfo(idx, rs['name'], rs['id'])

            #     '''
            #     4. 선택한 Site 예약전 서비스 확인 및 계산
            #     '''
            #     apiUri = '/v1/zones/services'
            #     getParams = {
            #         'id': site_id,
            #         'limit' : 100,
            #         'skip' : 0
            #     }
            #     response = requestGetData(apiUri, site_id, getParams)
            #     if -1 != response :
            #         response = response.json()
            #         service_obj = dict()
            #         for idx, data in enumerate(response) :
            #             logger.info(" == Service Response idx, id : {}, {}, {} ".format(idx, data['id'], data['name']))
                    

            #     '''
            #     5. 선택한 Site 예약
            #     '''

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
