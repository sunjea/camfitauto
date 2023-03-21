
import requests
import json
import logging
import sys

from .api_result import ApiResult

logger = logging.getLogger(__name__)

'''
    apiUrl : https://api.camfit.co.kr  - 캠핏 API URL(공통)
    
    apiUri : 
        GET :
            /v2/search/count            - 캠핑장 검색 카운트
            /v2/search                  - 캠핑장 리스트
            /v1/camps/zones/count/{_id} - 캠핑장 Zone 카운트
            /v1/camps/zones/{_id}       - 캠핑장 Zone 정보
            /v1/sites/{_id}             - 캠핑장 Site 정보
            /v1/zones/services          - 캠핑장 Zone 에서 제공하는 서비스들 (calculate, book에 사용)

        POST :
            /v1/booking/calculate       - 캠핑장 총 비용 계산 요청
            /v1/book                    - 캠핑장 예약 요청

'''

apiUrl = 'https://api.camfit.co.kr'

'''
    API 를 요청할때는 보안상의 이유로 아래 헤더들을 챙겨서 요청을 해야하는듯...
'''
headers={
    'Origin': 'https://camfit.co.kr',
    'Referer': 'https://camfit.co.kr',
    'sec-ch-ua': '"Chromium";v="106", "Not A;Brand";v="99", "Google Chrome";v="106"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform' : '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
   
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42'
}


def requestGetData(apiUri, _id=None, getParams=None):

    result: ApiResult = None
    if _id != None :
        queryUrl = f'{apiUrl}{apiUri}/{_id}'
    else :
        queryUrl = f'{apiUrl}{apiUri}'
    
    try :
        response = requests.get(url=queryUrl, params=getParams,
                                    headers=headers
                                )                        
        rsp_data = None
        if response.text and response.text != "":
            rsp_data = json.loads(response.text)
        result = ApiResult(response.status_code, rsp_data)   
    except Exception as err:
        logger.error(f' == requestGetData Error : {err} ')
        raise err
    
    return result
        
def requestPostData(apiUri, postObj):
    
    datas = json.dumps(postObj)
    datas = datas.replace(" ", "")

    '''
        POST 전송시 Headers 에는 Content-Length/Content-Type 이 필수.
        Body 는 공백 없이 전송
    '''
    global headers
    headers['Content-Length'] = str(len(datas))
    headers['Content-Type'] = 'application/json'
    
    result: ApiResult = None
    queryUrl = f'{apiUrl}{apiUri}'
    try :
        response = requests.post(url=queryUrl,
                                    headers=headers,
                                    data=datas
                                )
        rsp_data = None
        if response.text and response.text != "":
            rsp_data = json.loads(response.text)
        result = ApiResult(response.status_code, rsp_data)   
    except Exception as err:
        logger.error(f' == requestPostData Error : {err} ')
        raise err
    
    return result
