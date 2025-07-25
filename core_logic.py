# core_logic.py
from router import get_router
from chat_utils import streaming_data
from chat_completions import get_chat_response
from skillset import get_skillset

# --------------------- 개별 로직 ---------------------

def process_router(query, chat_history):
    router_result = get_router(query, chat_history)
    domain = router_result.get('result', {}).get('domain', {}).get('result', '')
    blocked_content = router_result.get('result', {}).get('blockedContent', {}).get('result', [])
    safety = router_result.get('result', {}).get('safety', {}).get('result', [])
    return domain, blocked_content, safety

def generate_skillset_response(query, chat_history, domain):
    result = get_skillset(query, domain, chat_history)
    return result.get('result', {}).get('finalAnswer', '답변을 생성할 수 없습니다.')

def generate_chat_response(query, chat_history):
    result = get_chat_response(query, chat_history)
    return result.get('result', {}).get('message', {}).get('content', '답변을 생성할 수 없습니다.')

def generate_filtered_response(filter_type):
    if filter_type == 'content':
        return (
            "**해당 ETF의 구성 종목 정보가 제공되지 않았어요.** 😢\n\n"
            "다른 ETF를 검색해보는 건 어떠신가요?\n"
            "- TIGER 미국S&P500 ETF의 종목 비율 알려줘\n"
            "- KODEX 2차전지산업 ETF의 상위 종목 구성 보여줘"
        )
    else:
        return (
            "**해당 ETF의 종목 비율 데이터를 찾을 수 없어요.** 🙏\n\n"
            "다른 ETF로 시도해보시겠어요?\n"
            "- ARIRANG 고배당주 ETF 구성 비율 알려줘\n"
            "- KOSEF 코스닥150 ETF 상위 종목 비중 알려줘\n\n"
            "언제든 궁금한 ETF 이름을 알려주면 최대한 도와드리겠습니다! 📈"
        )

# --------------------- 메인 로직 ---------------------

def handle_query(query: str, messages: list):
    # 세션 메시지 업데이트
    messages.append({'role': 'user', 'content': query})
    chat_history = [{'role': m['role'], 'content': m['content']} for m in messages]

    domain, blocked_content, safety = process_router(query, chat_history)

    if domain == "20250719etf":  # 실제 domain 이름 맞춰서 수정
        if not blocked_content and not safety:
            final_answer = generate_skillset_response(query, chat_history, domain)
        elif blocked_content and not safety:
            final_answer = generate_filtered_response('content')
        else:
            final_answer = generate_filtered_response('safety')

    elif domain == "News":  # 실제 domain 이름 맞춰서 수정
        if not blocked_content and not safety:
            final_answer = generate_skillset_response(query, chat_history, domain)
        elif blocked_content and not safety:
            final_answer = generate_filtered_response('content')
        else:
            final_answer = generate_filtered_response('safety')

    else:
        final_answer = generate_chat_response(query, chat_history)

    # streaming_data가 generator라면 join
    answer_str = "".join([chunk for chunk in streaming_data(final_answer)])
    messages.append({'role': 'assistant', 'content': answer_str})
    return answer_str
