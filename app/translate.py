import json
import requests
from flask_babel import _
#from app import app
from flask import current_app

def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in current_app.config or \
            not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    auth = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'eastus2'}
    r = requests.post(
        'https://api.cognitive.microsofttranslator.com'
        f'/translate?api-version=3.0&from={source_language}&to={dest_language}',
        headers=auth, json=[{'Text': text}])
    # request 패키지의 post()메서드는 첫 번째 인수로 제공된 URL에 POST 메서드가 있는 HTTP 요청을 보냄.
    # 번역기 리소스의 "Keys and Endpoint" 페이지에 나타나는 기본 URL인 
    #  https://api.cognitive.microsofttranslator.com/ 을 사용하고 있다.
    # 번역 끝점의 경로는 /translate 
    # 출발어 및 도착어는 URL에서 각각 from 및 to 라는 이름의 쿼리 문자열 인수로 제공되어야 함.
    # API는 또한 쿼리 문자열에 api-version = 3.0 인수를 지정해야함. 
    # 번역할 테스트는 요청 본문에 "{"Text":"the text to translate here"} 형식으로 JSON형식으로 제공 되어야한다.
   
   # 서비스를 인증하려면 구성에 추가한 키를 전달해야한다.
   # 이 키는 이름이 Ocp-Apim-Subscription-Key 인 사용자 지정 HTTP 헤더에 제공되어야함.
   # Ocp-Apim-Subscription-Region 에 번역자 리소스가 베포 된 지역도 헤더에 제공되어야함.
   # 지역에 대해 제공해야하는 이름은 "Keys and Endpoint" 페이지에 표시됨. 헤더로 인증 딕셔너리를 만든 다음 headers 인수의 요청에 전달했다.
   
    if r.status_code != 200: # 상태 코드가 성공적인 요청을 위한 코드인 200인지 확인하기 
        return _('Error: the translation service failed.')
    return r.json()[0]['translations'][0]['text'] 
        # 응답 본문에 번역이 포함된 JSON 인코딩 문자열이 있으므로 
        # json() 응답 객체의 메서드를 사용하여 JSON을 사용할 수 있는 Python 문자열로 디코딩하기 
        # -> JSON 응답은 번역 먹록이지만 단일 텍스트를 번역하고 있으므로 
        #    첫 번째 요소를 가져와 번역 구조내에서 실제 번역된 텍스트를 찾을 수 있다.