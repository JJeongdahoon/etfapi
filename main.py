# main.py
# 실행: streamlit run main.py

import streamlit as st
from router import get_router
from chat_utils import streaming_data
from chat_completions import get_chat_response
from skillset import get_skillset

# ✅ Streamlit 초기 설정은 반드시 최상단에서 딱 한 번만 호출!
st.set_page_config(page_title="ETF 탐색 에이전트")


def initialize_chat_session():
    """에이전트 세션 초기화"""
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                'role': 'assistant', 
                'content': '앙앙 어떤 ETF를 보여줄까?.'
            }
        ]


def render_initial_messages():
    """메시지 렌더링"""
    with st.chat_message(st.session_state.messages[0]['role']):
        st.write(st.session_state.messages[0]['content'])

    for message in st.session_state.messages[1:]:
        with st.chat_message(message['role']):
            st.write(message['content'])


def display_response(final_answer):
    """응답 표시 및 세션 상태 업데이트"""
    with st.chat_message('assistant'):
        st.write_stream(streaming_data(final_answer))
    st.session_state.messages.append({'role': 'assistant', 'content': final_answer})


def process_router(query, chat_history):
    """라우터 호출"""
    with st.status("라우터 적용 중...", expanded=True) as router_status:
        process_view = st.empty()
        process_view.write("라우터 적용 중입니다.")
        
        router_result = get_router(query, chat_history)
        
        domain = router_result.get('result', {}).get('domain', {}).get('result', '')
        blocked_content = router_result.get('result', {}).get('blockedContent', {}).get('result', [])
        safety = router_result.get('result', {}).get('safety', {}).get('result', [])
        
        # 디버깅용 출력
        print("=== 라우터 결과 ===")
        print(router_result)
        print("=== 도메인 결과 ===", domain)

    return domain, blocked_content, safety, router_status, process_view


def generate_skillset_response(query, chat_history, domain):
    with st.status("답변 생성 중...", expanded=True) as answer_status:
        process_view = st.empty()
        process_view.write("API를 호출하고 답변을 생성하는 중입니다. 잠시만 기다려주세요.")

        # domain을 넘겨주기!
        result = get_skillset(query, domain, chat_history)
        final_answer = result.get('result', {}).get('finalAnswer', '답변을 생성할 수 없습니다.')
        
        process_view.write("답변 생성이 완료되었습니다.")
        answer_status.update(label="답변 생성 완료", state="complete", expanded=False)
        
    return final_answer


def generate_chat_response(query, chat_history):
    """chat_completions 응답 생성"""
    with st.status("답변 생성 중...", expanded=True) as answer_status:
        process_view = st.empty()
        process_view.write("요청하신 내용에 대한 답변을 생성 중입니다. 잠시만 기다려주세요.")
        
        result = get_chat_response(query, chat_history)
        final_answer = result.get('result', {}).get('message', {}).get('content', '답변을 생성할 수 없습니다.')
        
        process_view.write("답변 생성이 완료되었습니다.")
        answer_status.update(label="답변 생성 완료", state="complete", expanded=False)

    return final_answer


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
    st.title('📈 TIGER ETF Top10 탐색기', anchor=False)
    st.write('')

    initialize_chat_session()
    render_initial_messages()

    if query := st.chat_input('ETF 이름을 입력해 보세요. (예: TIGER 200)'):
        # 유저 메시지 출력
        with st.chat_message('user'):
            st.write(query)
        st.session_state.messages.append({'role': 'user', 'content': query})

        # 대화 기록
        chat_history = [{'role': msg['role'], 'content': msg['content']} for msg in st.session_state.messages]

        # 라우터 호출 (ETF용으로 도메인 판별)
        domain, blocked_content, safety, router_status, process_view = process_router(query, chat_history)
        router_status.update(label="라우터 적용 중...", state="running", expanded=True)

        # 디버깅 출력
        print("=== 라우터 domain ===", domain)
        print("=== blocked_content ===", blocked_content)
        print("=== safety ===", safety)

        # ✅ 도메인 판별
        if domain == "20250719etf":   # 👉 실제 반환 domain명으로 교체
            if not blocked_content and not safety:
                process_view.write("✅ ETF 스킬셋으로 처리 가능합니다.")
                router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
                final_answer = generate_skillset_response(query, chat_history, domain)
                display_response(final_answer)

            elif blocked_content and not safety:
                process_view.write("❌ 스킬셋 사용 불가 (콘텐츠 필터)")
                router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
                final_answer = generate_filtered_response('content')
                display_response(final_answer)

            else:
                process_view.write("❌ 스킬셋 사용 불가 (세이프티 필터)")
                router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
                final_answer = generate_filtered_response('safety')
                display_response(final_answer)

        elif domain == "News":   # 👉 실제 반환 domain명으로 교체
            if not blocked_content and not safety:
                process_view.write("✅ News 스킬셋으로 처리 가능합니다.")
                router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
                final_answer = generate_skillset_response(query, chat_history, domain)
                display_response(final_answer)

            elif blocked_content and not safety:
                process_view.write("❌ 스킬셋 사용 불가 (콘텐츠 필터)")
                router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
                final_answer = generate_filtered_response('content')
                display_response(final_answer)

            else:
                process_view.write("❌ 스킬셋 사용 불가 (세이프티 필터)")
                router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
                final_answer = generate_filtered_response('safety')
                display_response(final_answer)

        else:
            process_view.write("ℹ️ 스킬셋과 관련 없는 요청 → Chat Completions 처리")
            router_status.update(label="라우터 적용 완료", state="complete", expanded=False)
            final_answer = generate_chat_response(query, chat_history)
            display_response(final_answer)

if __name__ == '__main__':
    main()
