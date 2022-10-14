
import requests
import json
import logging

from .api_result import ApiResult

logger = logging.getLogger(__name__)

'''
    apiUrl : https://api.camfit.co.kr  - 캠핏 API URL(공통)
    
    apiUri :
        /v2/search/count  - 캠핑장 검색 카운트 URI
        /v2/search        - 캠핑장 검색
        /v1/camps/zones/count/{_id} - 캠핑장 사이트 카운트
    
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

def requestGetData(apiUri, _id=None, getParams=None) -> ApiResult:

    if _id != None :
        queryUrl = "{}{}/{}".format(apiUrl, apiUri, _id)    
    else :
        queryUrl = "{}{}".format(apiUrl, apiUri)
    response = requests.get(url=queryUrl, params=getParams,
                                headers=headers
                            )
                            
    logger.info(' == Request GetData URL : {} '.format(response.url))        
    if response.status_code == 200 :
        return response
    else :
        logger.error(' == Response : {} '.format(response.status_code))
        return -1
        
def requestPostData(apiUri, postObj) -> ApiResult:

    queryUrl = "{}{}".format(apiUrl, apiUri)
    logger.info(' == Request PostData URL : {} '.format(queryUrl))
    response = requests.post(url=queryUrl,
                                headers=headers,
                                data=json.dumps(postObj)
                            )
    
    if response.status_code == 200 :
        return response
    else :
        logger.error(' == Response : {} '.format(response.status_code))
        return -1
