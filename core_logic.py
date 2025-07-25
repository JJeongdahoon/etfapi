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
            "**콘텐츠 필터 규정**에 따라, 해당 질문에는 답변을 제공해 드리기 어려운 점 양해 부탁드려요.\n\n"
            "혹시 이렇게 질문해 보시는 건 어떠실까요? :)\n"
            "- 경기도 가을 단풍 명소 추천해 주세요.\n"
            "- 제주도 애월 맛집과 카페"
        )
    else:
        return (
            '**안전 관련 규정**에 따라, 해당 질문에는 답변을 제공해 드리기 어려운 점 양해 부탁드려요.\n\n'
            '혹시 이렇게 질문해 보시는 건 어떠실까요?\n'
            '- 부산에서 인기 있는 맛집 찾아줄래?\n'
            '- 서울 분위기 좋은 카페 추천\n'
            '- 티엔미미 인기 메뉴 알려주세요\n\n'
            '언제나 좋은 정보로 도움 드리고자 합니다. 필요하신 내용이 있으시면 편하게 말씀해 주세요! 😊'
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
