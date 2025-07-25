import requests
from config import Config

def get_skillset(query, domain, chat_history=None):
    if domain == "20250719etf":  # ETF 도메인
        url = Config.SKILLSET_API_ETF
        request_id = Config.REQUEST_ID_ETF_SKILLSET
        client_id = Config.NAVER_LOCAL_CLIENT_ID
        client_secret = Config.NAVER_LOCAL_CLIENT_SECRET
    elif domain == "News":  # NEWS 도메인
        url = Config.SKILLSET_API_NEWS
        request_id = Config.REQUEST_ID_NEWS_SKILLSET
        client_id = Config.NAVER_NEWS_CLIENT_ID
        client_secret = Config.NAVER_NEWS_CLIENT_SECRET
    else:
        # 기본값
        url = Config.SKILLSET_API_ETF
        request_id = Config.REQUEST_ID_ETF_SKILLSET
        client_id = Config.NAVER_LOCAL_CLIENT_ID
        client_secret = Config.NAVER_LOCAL_CLIENT_SECRET

    headers = {
        'Authorization': f'Bearer {Config.API_KEY}',
        'X-NCP-CLOVASTUDIO-REQUEST-ID': request_id,
        'Content-Type': 'application/json',
    }

    data = {
        'query': query,
        'requestOverride': {
            'baseOperation': {
                'header': {
                    'X-Naver-Client-Id': client_id,
                    'X-Naver-Client-Secret': client_secret
                }
            }
        }
    }

    if chat_history:
        data['chatHistory'] = chat_history[-3:-1]

    response = requests.post(url, headers=headers, json=data)

    try:
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ 스킬셋 API 호출 실패: {e}")
        print(f"응답 내용: {response.text}")
        return {"result": {"finalAnswer": "스킬셋 호출 중 오류가 발생했습니다."}}
