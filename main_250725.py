# main_no_streamlit.py
from router import get_router
from chat_utils import streaming_data
from chat_completions import get_chat_response
from skillset import get_skillset


# 세션 메시지 저장
messages = [
    {
        'role': 'assistant',
        'content': '앙앙 어떤 ETF를 보여줄까?.'
    }
]


def display_response(final_answer):
    """응답 출력 및 세션 상태 업데이트"""
    print("\n🤖 [Assistant]:")
    # streaming_data가 제너레이터일 경우 처리
    for chunk in streaming_data(final_answer):
        print(chunk, end='', flush=True)
    print()
    messages.append({'role': 'assistant', 'content': final_answer})


def process_router(query, chat_history):
    """라우터 호출"""
    print("\n[라우터 적용 중...]")
    router_result = get_router(query, chat_history)

    domain = router_result.get('result', {}).get('domain', {}).get('result', '')
    blocked_content = router_result.get('result', {}).get('blockedContent', {}).get('result', [])
    safety = router_result.get('result', {}).get('safety', {}).get('result', [])

    # 디버깅 출력
    print("=== 라우터 결과 ===", router_result)
    print("=== 도메인 결과 ===", domain)

    return domain, blocked_content, safety


def generate_skillset_response(query, chat_history, domain):
    """스킬셋 응답 생성"""
    print("[스킬셋 호출 중...]")
    result = get_skillset(query, domain, chat_history)
    return result.get('result', {}).get('finalAnswer', '답변을 생성할 수 없습니다.')


def generate_chat_response(query, chat_history):
    """chat_completions 응답 생성"""
    print("[Chat Completions 호출 중...]")
    result = get_chat_response(query, chat_history)
    return result.get('result', {}).get('message', {}).get('content', '답변을 생성할 수 없습니다.')


def generate_filtered_response(filter_type):
    """고정 응답"""
    if filter_type == 'content':
        return (
            "**콘텐츠 필터 규정**에 따라, 해당 질문에는 답변을 제공해 드리기 어려운 점 양해 부탁드려요.\n\n"
            "혹시 이렇게 질문해 보시는 건 어떠실까요? :)\n"
            "- 경기도 가을 단풍 명소 추천해 주세요.\n"
            "- 제주도 애월 맛집과 카페"
        )
    else:  # safety filter
        return (
            '**안전 관련 규정**에 따라, 해당 질문에는 답변을 제공해 드리기 어려운 점 양해 부탁드려요.\n\n'
            '혹시 이렇게 질문해 보시는 건 어떠실까요?\n'
            '- 부산에서 인기 있는 맛집 찾아줄래?\n'
            '- 서울 분위기 좋은 카페 추천\n'
            '- 티엔미미 인기 메뉴 알려주세요\n\n'
            '언제나 좋은 정보로 도움 드리고자 합니다. 필요하신 내용이 있으시면 편하게 말씀해 주세요! 😊'
        )


def main():
    print("📈 TIGER ETF Top10 탐색기 (콘솔 버전)")
    print(messages[0]['content'])

    while True:
        query = input("\n🧑 [User]: ")
        if query.lower() in ['quit', 'exit']:
            print("종료합니다. 👋")
            break

        messages.append({'role': 'user', 'content': query})
        chat_history = [{'role': m['role'], 'content': m['content']} for m in messages]

        domain, blocked_content, safety = process_router(query, chat_history)

        if domain == "20250719etf":  # 👉 실제 domain명으로 교체
            if not blocked_content and not safety:
                print("✅ ETF 스킬셋으로 처리 가능합니다.")
                final_answer = generate_skillset_response(query, chat_history, domain)
                display_response(final_answer)
            elif blocked_content and not safety:
                print("❌ 스킬셋 사용 불가 (콘텐츠 필터)")
                display_response(generate_filtered_response('content'))
            else:
                print("❌ 스킬셋 사용 불가 (세이프티 필터)")
                display_response(generate_filtered_response('safety'))

        elif domain == "News":  # 👉 실제 domain명으로 교체
            if not blocked_content and not safety:
                print("✅ News 스킬셋으로 처리 가능합니다.")
                final_answer = generate_skillset_response(query, chat_history, domain)
                display_response(final_answer)
            elif blocked_content and not safety:
                print("❌ 스킬셋 사용 불가 (콘텐츠 필터)")
                display_response(generate_filtered_response('content'))
            else:
                print("❌ 스킬셋 사용 불가 (세이프티 필터)")
                display_response(generate_filtered_response('safety'))

        else:
            print("ℹ️ 스킬셋과 관련 없는 요청 → Chat Completions 처리")
            final_answer = generate_chat_response(query, chat_history)
            display_response(final_answer)


if __name__ == '__main__':
    main()
