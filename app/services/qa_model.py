from app.services.ai_model_service import ai_model_service
from app.langgraph.dsl import build_prompt
import textwrap

async def answer_question(query: str, mongo_summary: str = "", contexts: list[str] = None):
    if "qa_generator" not in ai_model_service.models:
        return {"answer": "⚠️ Q&A 모델이 아직 로딩되지 않았습니다."}

    # DSL 기반 프롬프트
    prompt = build_prompt(query, mongo_summary, contexts or [])

    # ✅ 인스트럭션 강화
    full_prompt = textwrap.dedent(f"""
    당신은 무신사 데이터 분석가입니다.
    다음 정보를 종합해서 한국어로 간결하고 실무적인 분석 보고서를 작성하세요.

    ### 질문:
    {query}

    ### MongoDB 요약:
    {mongo_summary}

    ### 관련 컨텍스트:
    {chr(10).join(['- ' + c for c in (contexts or [])])}

    ### 작성 지침:
    1. 질문에 직접 답하세요.
    2. MongoDB 결과와 컨텍스트를 근거로 설명하세요.
    3. 불필요한 서론은 쓰지 마세요.
    4. 보고서 스타일로 **답변, 인사이트, 추천사항**을 구분해서 작성하세요.

    ### 최종 답변:
""").strip()
    print("=== Q&A Prompt ===")
    print(full_prompt)

    outputs = ai_model_service.generate_answer(full_prompt, max_new_tokens=256)
    raw = outputs[0]["generated_text"]

    answer = raw.replace(full_prompt, "").strip()
    if not answer:
        answer = "데이터 기반 답변을 생성하지 못했습니다."
    return {"answer": answer}
