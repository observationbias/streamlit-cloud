from dotenv import load_dotenv
import os
from openai import OpenAI
import streamlit as st
import time
# streamlit 설정에 API 키를 숨겨놓고 이를 호출합니다. MBTI API key입니다.
API_KEY = st.secrets["general"]["OPENAPI_KEY"]
client = OpenAI(api_key=API_KEY)

# 테스트 대화를 나눌 어시스턴트 아이디를 입력합니다. (현재 모델은 오류해결용 버전으로 등록해 두었습니다.)
assistant_id = "asst_xkBSWJrxZ99CyjnaiA965Vfo"

# 처음 대화할 때 세션을 초기화합니다.
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

# 어시스턴트 이름 가져오기 (ID에서 정보 얻어옴)
assistant_info = client.beta.assistants.retrieve(assistant_id=assistant_id)
assistant_name = assistant_info.name

# 페이지 제목 설정
st.header(f"{assistant_name}")

# 충분한 높이의 빈 공간 생성
placeholder = st.empty()

# 메시지 표시 섹션 코드
if 'thread_id' in st.session_state and st.session_state['thread_id'] is not None:
    with placeholder.container():
        thread_messages = client.beta.threads.messages.list(st.session_state['thread_id'])
        for msg in reversed(thread_messages.data):
            with st.chat_message(msg.role):
                st.write(f"<div style='border:1px solid #ccc; padding:10px; border-radius:10px; margin:10px 0;'>{msg.content[0].text.value}</div>", unsafe_allow_html=True)

# 사용자 입력 섹션 코드
prompt = st.text_input("질문 입력", key="user_input")
submit_button = st.button("Send")

if submit_button and prompt:
    if st.session_state.thread_id is None:
        # 새 스레드 생성
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # 메시지 생성 및 저장
    message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    # Assistant 실행 및 결과 처리
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id,
    )

    # RUN 완료까지 대기
    while run.status not in ["completed", "failed", "require_action"]:
        print(f"Current run status: {run.status}")  # 큐 상태를 터미널에 출력
        time.sleep(1)  # 1초 대기
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
    
    # 완료된 상태를 터미널에 출력
    if run.status == "completed":
        print("Run completed successfully.")
    elif run.status == "failed":
        print("Run failed. Please check the details.")
    elif run.status == "require_action":
        print("Additional action required. Please check the details and take necessary steps.")
    
    # 완료된 대화 불러오기
    if run.status == "completed":
        with placeholder.container():
            messages = client.beta.threads.messages.list(st.session_state.thread_id)
            for msg in reversed(messages.data):
                with st.chat_message(msg.role):
                    st.write(f"<div style='border:1px solid #ccc; padding:10px; border-radius:10px; margin:10px 0;'>{msg.content[0].text.value}</div>", unsafe_allow_html=True)
