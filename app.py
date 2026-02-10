import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser

# 1. 화면 설정
st.set_page_config(page_title="South American Rock Spirit", page_icon="🤘")
st.title("🎸 스페인어 락 블로그 에이전트")
st.markdown("---")
st.info("💡 팁: 가사는 구글이나 Genius에서 검색해서 붙여넣으면 가장 정확합니다!")

# 2. 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key (sk-...)", type="password")
    model_name = st.selectbox("모델 선택", ["gpt-4o", "gpt-4-turbo"])

# 3. 입력창 구성
col1, col2 = st.columns(2)
with col1:
    artist = st.text_input("아티스트")
with col2:
    song = st.text_input("곡 제목")

# (1) 배경 지식용 URL
url = st.text_input("참고할 URL (곡의 역사/배경 지식용)")

# (2) ★ 가사 입력창 (여기가 핵심!)
lyrics_input = st.text_area("📜 스페인어 가사 원문 (여기에 붙여넣으세요)", height=200,
                            placeholder="Ella durmió al calor de las masas...")

# 4. 실행 버튼
if st.button("🚀 블로그 포스팅 생성하기"):
    if not api_key:
        st.error("API Key가 필요합니다!")
    elif not lyrics_input:
        st.warning("⚠️ 가사를 입력해주세요! 정확한 번역을 위해 원문이 필요합니다.")
    else:
        try:
            # [단계 1] URL에서 '역사/배경' 긁어오기
            with st.spinner(f"🌐 '{url}'에서 곡의 배경 지식을 수집 중..."):
                loader = WebBaseLoader(url)
                docs = loader.load()
                context_text = docs[0].page_content[:4000]

            # [단계 2] 입력받은 가사 + 배경지식으로 글 작성
            with st.spinner("✍️ 가사를 분석하고 번역하는 중..."):
                llm = ChatOpenAI(model=model_name, api_key=api_key, temperature=0.7)

                template = """
                당신은 스페인어어 락(Rock en Español) 전문 음악 평론가입니다.
                사용자가 제공한 [가사 원문]과 [참고 자료]를 바탕으로 블로그 글을 작성하세요.

                [입력 정보]
                1. 아티스트: {artist}
                2. 곡 제목: {song}
                3. 가사 원문: {lyrics}
                4. 참고 자료(Context): {context}

                [⭐ 작성 가이드]
                1. 제목: 이모지 포함, 클릭을 유도하는 제목.
                2. 도입부: 감성적인 오프닝.
                3. 곡의 정보(발매일, 앨범, 작곡가, 편곡가 등): [참고 자료]의 팩트를 활용해 깊이 있게 설명.
                4. 가사 번역 및 해설 (가장 중요):
                   - 사용자가 입력한 [가사 원문] 전체를, 스페인어 가사 한 줄이 나오고 그 다음 줄에 해당하는 한국어 번역이 나오도록 작성하세요.
                   - 예시 형식:
                     > 스페인어 원문 한 줄
                     > 스페인어 가사 밑에 한국어 감성 의역
                   - 모든 가사 라인에 대해 위와 같은 형식으로 번역합니다.
                   - 💡 해설: 전체 번역 하단에 한 번만 제공하며, 가사가 전반적으로 어떤 내용을 담고 있는지(주제, 감정, 메시지 등 포함), 이 곡이 전하는 의미와 해석을 깊이 있게 설명해 주세요.
                5. 마무리: 추천 멘트.

                언어: 한국어 (존댓말/해요체)
                """

                prompt = PromptTemplate.from_template(template)
                chain = prompt | llm | StrOutputParser()
                
                # 실행 (가사 변수 추가됨)
                result = chain.invoke({
                    "artist": artist, 
                    "song": song, 
                    "context": context_text,
                    "lyrics": lyrics_input  # 사용자가 입력한 가사 전달
                })

                st.success("작성 완료! 🎉")
                st.markdown(result)

        except Exception as e:
            st.error(f"에러 발생: {e}")