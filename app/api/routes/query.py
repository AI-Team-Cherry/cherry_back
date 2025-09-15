from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
from app.langgraph.workflows import workflow
from app.db.mongodb import run_aggregation, insert_result
from app.services.rag_service import search as rag_search
from app.langgraph.dsl import build_prompt
from app.services.qa_model import answer_question
from app.services.report_service import generate_report
from app.services.analysis_helpers import summarize_results

router = APIRouter()

class QueryIn(BaseModel):
    userId: str
    query: str

@router.post("/")
async def run_query(body: QueryIn):
    state = workflow.invoke({"query": body.query})

    # Mongo 실행
    mongo_results: List[Dict[str, Any]] = []
    collection, pipeline = None, []
    if "mongo_results" in state:
        collection = state["mongo_results"]["collection"]
        pipeline = state["mongo_results"]["pipeline"]
        mongo_results = await run_aggregation(collection, pipeline)

    # RAG
    rag_docs = await rag_search(body.query, top_k=5)
    contexts = [c.get("text", "") for c in rag_docs]
    scores = [float(c.get("score", 0.5)) for c in rag_docs]

    # 요약
    summary = summarize_results(mongo_results)
    prompt = build_prompt(body.query, summary, contexts)
    qa = await answer_question(prompt)

    # 시각화 (데이터 없으면 생략)
    viz = []
    if mongo_results:
        keys = list(mongo_results[0].keys())
        x_field = keys[0]
        y_field = next((k for k in keys if k != x_field), x_field)
        viz = [{
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": f"{body.query} - 시각화",
            "data": {"values": mongo_results[:10]},
            "mark": "bar",
            "encoding": {
                "x": {"field": x_field, "type": "nominal"},
                "y": {"field": y_field, "type": "quantitative"}
            }
        }]

    # 리포트
    report = generate_report(f"{body.query} 리포트", {
        "summary": summary,
        "insights": qa.get("answer", ""),
        "recommendations": ["추천 1", "추천 2"]
    })

    # 저장 & 응답
    result_doc = {
        "userId": body.userId,
        "query": body.query,
        "output": {
            "mongodb_results": {
                "collection": collection,
                "pipeline": pipeline,
                "data": mongo_results,
                "summary": summary
            },
            "vector_results": {
                "context": contexts,
                "similarity_scores": scores
            },
            "ai_analysis": {
                "answer": qa.get("answer", ""),
                "insights": "인사이트 예시",
                "recommendations": "추천사항 예시"
            },
            "visualizations": viz,
            "report": report
        },
        "createdAt": datetime.utcnow(),
    }
    await insert_result(result_doc)

    return {
        "status": "success",
        "query": body.query,
        "mongodb_results": result_doc["output"]["mongodb_results"],
        "vector_results": result_doc["output"]["vector_results"],
        "ai_analysis": result_doc["output"]["ai_analysis"],
        "visualizations": viz,
        "report": report
    }