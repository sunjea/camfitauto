import logging
import config
import sys 
import json

from PyQt5.QtWidgets import * 
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from api.api_camfit import requestGetData, requestPostData
from util import getTimeStamp
from database.db_helper import createTable, insertCampingInfo, getSelectCampId, insertZoneInfo, getSelectZoneId, insertSiteInfo, getSelectSiteId
from enums import SEND_MSG_STS, THREAD_MODE

#UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다. 
form_class = uic.loadUiType("ui/resrvUi.ui")[0] 
_thr_mode = None

# 캠핑 기간
_params_time = dict()

_camp_id = None
_zone_id = None

# 계산 정보
_calculateInfo = dict()
_bookInfo = dict()

class WindowClass(QMainWindow, form_class) : 
    def __init__(self) : 
        super().__init__() 
        self.setupUi(self) 
        self.setFixedSize(579,426)
        createTable()

        #각 버튼에 대한 함수 연결 
        self.pushButton.clicked.connect(self.campingListSearch)
        self.lineEdit.returnPressed.connect(self.campingListSearch)
        self.pushButton_2.clicked.connect(self.campingReservation)
        self.listWidget.itemClicked.connect(self.campingListClicked)
        self.listWidget_2.itemClicked.connect(self.zoneListClicked)
        self.listWidget_3.itemClicked.connect(self.siteListClicked)
        self.dateEdit.dateChanged.connect(self.onDateEditChange)

        self.pushButton_2.setDisabled(True)
        self.searchThr = SearchThread(parent=self)
        self.statusBar.showMessage('준비')

        self.dateEdit.setDateTime(QDateTime.currentDateTime())
        self.dateEdit_2.setDateTime(QDateTime.currentDateTime().addDays(1))
            
    def onDateEditChange(self, qDate):
        self.dateEdit_2.setMinimumDate(QDate(qDate.year(), qDate.month(), qDate.day()))

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
        site_id = getSelectSiteId(self.listWidget_3.currentRow(), _camp_id, _zone_id)

        checkInDate = self.dateEdit.date()
        checkoutDate = self.dateEdit_2.date()

        global _calculateInfo
        _calculateInfo['siteId'] = site_id
        _calculateInfo['checkInDate'] = {
            "year" : checkInDate.year(),
            "month" : checkInDate.month(),
            "day" : checkInDate.day()
        }
        _calculateInfo['checkoutDate'] = {
            "year" : checkoutDate.year(),
            "month" : checkoutDate.month(),
            "day" : checkoutDate.day()
        }
        _calculateInfo['numOfAdults'] = int(self.lineEdit_2.text())
        _calculateInfo['numOfTeens'] = 0
        _calculateInfo['numOfChildren'] = int(self.lineEdit_3.text())
        _calculateInfo['numOfCars'] = 1
        getServiceIdInfo()
        _calculateInfo['hasTrailer'] = False
        _calculateInfo['hasCampingCar'] = False
 
    def campingReservation(self):

        apiUri = '/v1/booking/calculate'
        response = requestPostData(apiUri, _calculateInfo)
        status: int = response.status
        data: dict = response.data
        if 200 == status : 
            global _bookInfo
            _bookInfo = _calculateInfo
            _bookInfo['name'] = self.lineEdit_4.text()
            _bookInfo['contact'] = self.lineEdit_5.text()
            _bookInfo['paymentMethod'] = 'bank'
            _bookInfo['coupon'] = None
            _bookInfo['campingPass'] = None
            _bookInfo['carNumbers'] = []
            _bookInfo['accommodationPrice'] = data['totalCharge']
            _bookInfo['parkingPrice'] = 0
            _bookInfo['servicePrice'] = 0
            _bookInfo['couponDiscount'] = 0
            
            apiUri = '/v1/book'
            response = requestPostData(apiUri, _calculateInfo)
            status: int = response.status
            data: dict = response.data
            if 200 == status :
                logger.info(f' == get campingReservation == \n {data} ')
                win = CustomDialog("확인","예약이 완료되었습니다. \n 자세한 내용은 문자나 알림톡 확인")
                r = win.showModal()

class SearchThread(QThread): 
    def __init__(self, parent): 
        super().__init__(parent) 
        self.parent = parent 
    
    def run(self): 
        if _thr_mode == THREAD_MODE.CAMP_LIST :

            text = self.parent.lineEdit.text()
            self.parent.listWidget_3.clear()
            self.parent.listWidget_2.clear()
            self.parent.listWidget.clear()
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
                    for idx, rs in enumerate(data) :
                        self.parent.listWidget.addItem(rs['name'])
                        insertCampingInfo(idx, rs['name'], rs['_id'])
          
        elif _thr_mode == THREAD_MODE.ZONE_LIST :

            '''
            2. 선택한 캠핑장 정보를 DB 검색 후 _id 값으로 Zone 정보 조회
               Zone 리스트 DB 저장
            '''
            self.parent.listWidget_2.clear()
            self.parent.listWidget_3.clear()
            global _camp_id
            _camp_id = getSelectCampId(self.parent.listWidget.currentRow(), self.parent.listWidget.currentItem().text())
            
            apiUri = '/v1/camps/zones/count'
            response = requestGetData(apiUri, _camp_id)
            status: int = response.status
            data: dict = response.data
            if 200 == status and int(data) > 0 :
                logger.info(f" == ZoneList Count : {data} ")

                global _params_time
                _params_time['stime'] = self.parent.dateEdit.date().toString("yyyy-MM-dd")
                _params_time['etime'] = self.parent.dateEdit_2.date().toString("yyyy-MM-dd")

                if -1 != getTimeStamp(_params_time) :           
                    apiUri = '/v1/camps/zones'
                    '''
                        3가지 값은 caculate 전에는 고정
                        'adult': 2,
                        'teen': 0,
                        'child': 0,
                    '''
                    getParams = {
                        'id': _camp_id,
                        'limit' : data,
                        'adult': 2,
                        'teen': 0,
                        'child': 0,
                        'startTimestamp': _params_time['stime'],
                        'endTimestamp' : _params_time['etime'],
                        'skip' : 0,
                    }
                    response = requestGetData(apiUri, _camp_id, getParams)
                    status: int = response.status
                    data: dict = response.data
                    if 200 == status :
                        for idx, rs in enumerate(data) :
                            '''
                                # 예약가능 조건
                                    rs['isUnavailable'] == False and rs['unavailableReason'] == None
                            ''' 
                            if rs['isUnavailable'] != False :
                                self.parent.listWidget_2.addItem(f"{rs['name']} - {rs['unavailableReason']} X ")
                            else :
                                self.parent.listWidget_2.addItem(f"{rs['name']}")
                            insertZoneInfo(idx, rs['name'], rs['id'], _camp_id)

        elif _thr_mode == THREAD_MODE.SITE_LIST :
            self.parent.listWidget_3.clear()
            '''
            3. 선택한 Zone 정보를 DB 검색 후 _id 값으로 Site 정보 조회
               Site 리스트 DB 저장 
            '''
            global _zone_id
            _zone_id = getSelectZoneId(self.parent.listWidget_2.currentRow(), _camp_id)
                  
            apiUri = '/v1/sites'
            getParams = {
                'startTimestamp': _params_time['stime'],
                'endTimestamp' : _params_time['etime']
            }
                
            response = requestGetData(apiUri, _zone_id, getParams)
            status: int = response.status
            data: dict = response.data
            if 200 == status :
                for idx, rs in enumerate(data) :
                    '''
                        # 예약가능 조건
                            rs['isAvailable'] == true and rs['unavailableReason'] == None

                        # 사이트 크기
                            rs['siteWidth'] x rs['siteLength'] 
                    ''' 
                    try :
                        if rs['isAvailable'] != True :
                            self.parent.listWidget_3.addItem(f"{rs['name']} - {rs['unavailableReason']} ")
                        else :
                            if rs['siteWidth'] != None and rs['siteLength'] != None :
                                self.parent.listWidget_3.addItem(f"{rs['name']} : {rs['siteWidth']} X {rs['siteLength']}")
                            else :
                                self.parent.listWidget_3.addItem(f"{rs['name']}")
                    except Exception as err:
                        self.parent.listWidget_3.addItem(f"{rs['name']}")
                        pass
                    insertSiteInfo(idx, rs['name'], rs['id'], _camp_id, _zone_id)
            
        self.parent.statusBar.showMessage('처리완료')
        self.parent.pushButton.setEnabled(True)

def getServiceIdInfo():
    '''
    4. 선택한 Site 예약전 서비스 확인 및 계산
    '''
    apiUri = '/v1/zones/services'
    getParams = {
        'id': _zone_id,
        'limit' : 100,
        'skip' : 0
    }
    response = requestGetData(apiUri, _zone_id, getParams)
    status: int = response.status
    data: dict = response.data

    if 200 == status :
        global _calculateInfo
        _calculateInfo['services'] = []
        for idx, rs in enumerate(data) :
            service = dict()
            logger.info(f" == Service Response idx, id : {idx}, {rs['id']}, {rs['name']} ")
            service['id'] = rs['id']
            service['quantity'] = 0 # 옵션에 대한 기능은 미제공..
            _calculateInfo['services'].append(service)


class CustomDialog(QDialog):
    def __init__(self, title, message):
        super().__init__()

        self.setWindowTitle(title)

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        
        message = QLabel(message)

        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
    
    def showModal(self):
        return super().exec_()

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
