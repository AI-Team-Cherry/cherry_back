# 🍒 Musinsa AI 분석 백엔드 (FastAPI + LangGraph)

무신사(의류 커머스) 데이터를 대상으로 **자연어 질의 → 데이터 조회/분석 → 시각화/리포트**까지 한 번에 처리하는 백엔드입니다.
프론트는 React, 백은 FastAPI이며 **LangGraph**를 백엔드 내부에서 **오케스트레이션 레이어**로 사용합니다.
또한 3클래스 감정분석(긍정/중립/부정) 시스템을 포함해 **리뷰 분석 파이프라인**을 제공합니다.

---

## ✨ 주요 기능

- **자연어 Q\&A 분석 파이프라인**

  - 질문 → DSL/복잡도 분류 → MongoDB Aggregation → (선택) RAG 검색 → Q\&A 생성 → Vega-Lite 시각화 → 리포트
  - 결과는 MongoDB에 저장

- **3클래스 감정분석 (리뷰 데이터)**

  - 단일 텍스트/CSV 업로드/몽고DB 일괄 분석
  - 속성(디자인·가격·품질 등 15개)별 감정까지 확장 저장

- **LangGraph 기반 오케스트레이션**

  - 백엔드 내부에서 워크플로우로 단계 실행

- **CPU-Only 환경 지원**

  - Transformers + Torch CPU로 동작 (추후 모델 교체 쉬움)

---

## 🗂 프로젝트 구조

```
app/
├── main.py                          # FastAPI 엔트리포인트
├── core/
│   ├── config.py                    # 환경설정 (DB URI, 모델명 등)
│   └── security.py                  # (선택) 인증/토큰 로직
├── db/
│   └── mongodb.py                   # Motor(MongoDB) 연결 유틸/쿼리
├── models/
│   ├── user.py                      # 유저 스키마 (선택)
│   ├── review.py                    # 리뷰 스키마(Pydantic)
│   ├── image.py                     # 이미지 스키마(선택)
│   └── result.py                    # 질의 결과 스키마(Pydantic)
├── services/
│   ├── ai_model_service.py          # HuggingFace 파이프라인 관리(GPT2 등)
│   ├── qa_model.py                  # Q&A(단계형 프롬프트 → 생성)
│   ├── rag_service.py               # RAG 검색 (현재 모의/플러그형)
│   ├── mongodb_query_generator.py   # 자연어→Mongo Aggregation (간단 DSL)
│   ├── analysis_helpers.py          # Mongo 결과 요약/후처리
│   ├── report_service.py            # 리포트 JSON 생성 유틸
│   ├── sentiment_service.py         # 3클래스 감정분석(텍스트/CSV/몽고)
│   └── huggingface_service.py       # 감정분석 모델 디버깅/헬퍼
├── langgraph/
│   ├── workflows.py                 # LangGraph 워크플로 정의
│   └── dsl.py                       # DSL/프롬프트 빌더(제한/지침 포함)
└── api/
    ├── routes/
    │   ├── query.py                 # 자연어 질문 처리(핵심 엔드포인트)
    │   ├── sentiment.py             # 감정분석: 텍스트/CSV/몽고
    │   └── ingest.py / auth.py ...  # (선택) 추가 라우트
    └── __init__.py
```

---

## 🧭 데이터 & 스키마

### MongoDB 컬렉션

#### 1) `product`

```json
{
  "_id": ObjectId("..."),
  "product_id": "3175071",
  "name": "상품명",
  "brand": "메종 마르지엘라",
  "category_l1": "상의/스웨트",
  "gender": "M",
  "price": 334990,
  "views_1m": 2600,
  "sales_cum": 0,
  "hearts": 444,
  "reviews_count": 7,
  "rating_avg": 5,
  "main_image": "3175071_1",
  "image_files": ["3175071_1", "3175071_2", ...]
}
```

#### 2) `reviews` (감정분석 저장 포함)

- 예시(요약):

```
_id: ObjectId(...)
product_id: "3175071"
user_id: "돈묻은코"
score: 0
text: "..."
photos: ["rimg_3175071_2_1.jpg"]
review_created_at: "2024-10-08"

# 전체 감정
overall_sentiment: "부정"  # 긍정/중립/부정
overall_confidence: 0.7993
overall_neg_prob: 0.7993
overall_neu_prob: 0.1809
overall_pos_prob: 0.0198

# 감지된 속성 (예: 15개)
detected_attributes: "착용감, 디자인, 가격, 품질, 크기, 소재, 배송, 색상, 사이즈, 핏, 편안함, 내구성, 재질, 포장"
num_attributes: 14

# 속성별 감정(예: fit/design/price/quality/...)
fit_mentioned: true
fit_sentiment: "긍정"
fit_confidence: 0.8767
fit_neg_prob: 0.0699
fit_neu_prob: 0.0534
fit_pos_prob: 0.8767

design_... (이하 유사 구조 반복)
...
```

#### 3) `sellers`

```json
{
  "_id": ObjectId("..."),
  "seller_id": "a32pwo618xwh",
  "brand_name": "1989스탠다드",
  "email": "snc78z@1989스탠다드.example.com",
  "categories": "상의/스웨트"
}
```

#### 4) `results` (질의 기록/리포트 저장)

- `/api/routes/query.py`에서 한 번의 질문 처리 결과를 저장

```json
{
  "_id": ObjectId("..."),
  "userId": "u1",
  "query": "브랜드별 매출 현황을 막대그래프로 보여줘",
  "output": {
    "mongodb_results": { "collection": "product", "pipeline": [...], "data": [...], "summary": "..." },
    "vector_results": { "context": [...], "similarity_scores": [...] },
    "ai_analysis": { "answer": "...", "insights": "...", "recommendations": "..." },
    "visualizations": [ { "$schema": "...", "title": "...", "data": { "values": [...] }, "mark": "bar", "encoding": {...} } ],
    "report": { "title": "...", "createdAt": "...", "summary": "...", "details": {...} }
  },
  "createdAt": "UTC 타임스탬프"
}
```

> **참고:** 응답 직전에 `ObjectId` 등 직렬화 불가 타입을 문자열로 변환해 JSON 오류를 방지합니다.

---

## 🧠 LangGraph 사용 전략 (이번 프로젝트 컨벤션)

> “LangGraph를 백엔드 내부에 포함”하는 방식이 유리합니다.
> 별도 모델 서버를 두지 않고, FastAPI에서 LangGraph 노드를 호출하여 **질문 → 분류 → 쿼리 생성/실행 → RAG → Q\&A → 시각화/리포트**를 직렬/분기 처리합니다.

### 왜 백엔드 내 LangGraph?

- 호출 지연 감소 (네트워크 홉 축소)
- 상태/캐싱을 서비스 코드와 함께 관리
- Pythonic하게 서비스/DB/모델 레이어 연결 용이

### 현재 워크플로 개요 (`app/langgraph/workflows.py`)

- 입력: `{ "query": str }`
- 노드(개념):

  1. DSL/복잡도 분류 (간단 규칙/의도 분류기로 “단순/중간/복잡”)
  2. MongoDB 쿼리 생성 (간단 DSL → Aggregation Pipeline)
  3. MongoDB 실행
  4. (선택) RAG 검색 (현재 플러그형/모의)
  5. 단계형 프롬프트 Q\&A 생성 (GPT2)
  6. Vega-Lite 시각화 및 리포트 구성

- 출력: 위의 `results` 구조

---

## 🤖 모델 & 프롬프트

### Q\&A 생성기

- **기본**: `gpt2` (CPU 환경, 1024 토큰 제한)
- **프롬프트 원칙**

  - **도메인 고정**: “당신은 무신사 데이터 분석가입니다. (의류 커머스 도메인)”
  - **출력 고정**: `답변 / 인사이트 / 추천사항` 3섹션 반드시 구분
  - **근거 제한**: 주어진 **Mongo 요약 + 컨텍스트(Facts)** 외 추론 금지
  - **안전장치**: 데이터 부족/부적합 시 **정직한 한계 진술**

- **토큰 관리**:

  - 입력이 1024 초과되지 않도록 **요약/절단**
  - `max_new_tokens`는 200\~400 권장

> **모델 교체 팁**: 한국어 인스트럭션 튜닝 모델(예: ko-LLM, Qwen2.5-1.8B-Instruct 등)로 바꾸면 품질이 즉시 개선됩니다. (HF 토큰/모델 가용성 필요)

### 감정분석

- 기본: `solbi12/ecommers_fasion_fine_tuned_3class_model` (허깅페이스)
- 기능:

  - 전체 감정/확률
  - 속성 15개 자동 감지 + 속성별 감정/확률
  - MongoDB에 결과 병합 저장

---

## ⚙️ 설치 & 실행

### 1) Python/의존성

```bash
# 가상환경 권장
pip install -r requirements.txt
```

**requirements.txt (요약)**

```
# Web
fastapi==0.114.2
uvicorn[standard]==0.30.6
python-multipart==0.0.9

# DB
motor==3.6.0
pymongo==4.9.1
python-dotenv==1.0.1

# Security
passlib[bcrypt]==1.7.4
PyJWT==2.9.0
python-jose==3.3.0

# AI
transformers==4.44.2
torch>=2.2.0
langgraph==0.2.39
hnswlib==0.7.0
chromadb==0.5.5
sentence-transformers==3.1.1
sentencepiece
sacremoses

# Utils
pydantic==2.9.2
numpy>=1.26.4
```

### 2) 환경 변수 (`.env`)

```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=musinsa_db

# (선택) HuggingFace 토큰 (private/gated 모델 쓸 때)
HUGGINGFACE_HUB_TOKEN=hf_xxx
```

### 3) 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔌 API 엔드포인트

### 1) 자연어 질의 → 분석 (핵심)

`POST /query/`

**Request**

```json
{
  "userId": "u1",
  "query": "브랜드별 매출 현황을 막대그래프로 보여줘"
}
```

**Response (예시)**

```json
{
  "status": "success",
  "query": "브랜드별 매출 현황을 막대그래프로 보여줘",
  "mongodb_results": {
    "collection": "product",
    "pipeline": [ ... ],
    "data": [ {"_id":"토피","total_sales":979300}, ... ],
    "summary": "10건의 결과가 검색되었습니다."
  },
  "vector_results": {
    "context": ["관련 컨텍스트 1 ...", "..."],
    "similarity_scores": [0.5, 0.5, ...]
  },
  "ai_analysis": {
    "answer": "답변/인사이트/추천사항 형식",
    "insights": "인사이트 예시",
    "recommendations": "추천사항 예시"
  },
  "visualizations": [
    {
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "title": "브랜드별 매출 현황을 막대그래프로 보여줘 - 시각화",
      "data": { "values": [ ... ] },
      "mark": "bar",
      "encoding": { "x": {"field":"_id"}, "y": {"field":"total_sales"} }
    }
  ],
  "report": {
    "title": "브랜드별 매출 현황을 막대그래프로 보여줘 리포트",
    "createdAt": "2025-09-15T...",
    "summary": "10건의 결과가 검색되었습니다.",
    "details": {
      "insights": "상세 인사이트",
      "recommendations": [ "추천 1", "추천 2" ]
    }
  }
}
```

> **주의:** 응답 구조는 프론트에서 그대로 사용 가능하도록 **평평한 JSON**으로 리턴됩니다.

---

### 2) 감정분석 API

#### (1) 단일 텍스트

`POST /sentiment/analyze-text`
Body:

```json
{ "text": "배송 빠르고 품질 좋아요" }
```

Response:

```json
{ "status":"success", "input":"...", "result": { "overall_sentiment":"긍정", ... } }
```

#### (2) CSV 업로드

`POST /sentiment/analyze-csv` (form-data: `file`=CSV)
Response:

```json
{
  "status":"success",
  "rows": 1234,
  "output_file":"sentiment_output_20240901_...csv",
  "sample":[ {...}, {...}, ... ]
}
```

#### (3) MongoDB 일괄 분석

`POST /sentiment/analyze-mongo?limit=1000`
Response:

```json
{ "status": "success", "processed": 1000 }
```

#### (4) 모델 디버그 (폼/JSON 둘 다)

`POST /sentiment/debug-model`

- form-data: `text=...`
  또는
- JSON: `{ "text": "..." }`

Response:

```json
{ "status":"success", "result": { "raw": {...}, "parsed": {...} } }
```

---

## 🧩 LangGraph 워크플로 상세

1. **질문 수신**

   - `api/routes/query.py` → `workflow.invoke({"query": ...})`

2. **분류/DSL/쿼리생성**

   - `langgraph/dsl.py` 간단 템플릿/룰
   - `services/mongodb_query_generator.py` 에서 aggregation pipeline 생성

3. **Mongo 실행**

   - `db/mongodb.py` → `run_aggregation(collection, pipeline)`

4. **RAG (플러그형)**

   - `services/rag_service.py`
   - 현재는 모의/고정 컨텍스트.
   - 실제 적용 시: Tavily/ChromaDB/Elastic 등으로 교체

5. **Q\&A 생성 (단계형 프롬프트)**

   - `services/qa_model.py`
   - 입력을 “지침 + FACTS + 출력형식”으로 강하게 제한
   - GPT2 토큰 제한 고려해 입력 자르기/요약

6. **시각화/리포트 조립**

   - `visualizations`: Vega-Lite 스펙 JSON 반환
   - `report_service.py`: 제목/요약/세부/추천 등 구성

7. **저장 & 응답**

   - `results` 컬렉션에 `output` 전체 저장
   - 응답에서 직렬화 문제(ObjectId 등) 제거

---

## 🧪 Postman 테스트 팁

- **/query/**

  - POST → Body(raw/JSON): `{"userId":"u1","query":"브랜드별 매출 현황을 막대그래프로 보여줘"}`
  - 응답의 `mongodb_results.data`가 있으면 Vega-Lite로 그대로 그릴 수 있습니다.

- **/sentiment/analyze-text**

  - POST → JSON: `{"text":"재질이 좋고 디자인이 예뻐요"}`

- **/sentiment/analyze-csv**

  - POST → form-data: `file=@reviews.csv`

- **/sentiment/debug-model**

  - POST → form-data: `text=...` **또는** Body JSON: `{"text": "..."}`

---

## 🚑 트러블슈팅

- **ObjectId 직렬화 오류**

  - 응답 직전에 `_id`를 문자열로 변환(코드 내 처리 완료)

- **GPT2 길이 초과/IndexError**

  - 1024 토큰 제한 → 프롬프트 절단/요약
  - `max_new_tokens`는 200\~400 권장

- **HF 모델 404/권한 오류**

  - 모델명 오타/Private Repo → `HUGGINGFACE_HUB_TOKEN` 필요
  - 가능하면 공개 모델/미러 사용

- **번역 모델 오류**

  - 번역 파이프라인은 현재 기본 비활성 (영→한 자동 번역 필요 시 NLLB/M2M 등 추가)

---

## ⚡ 성능/품질 팁

- **모델 교체**: 한국어 Instruct LLM으로 교체하면 Q\&A 품질 급상승
- **RAG 실제화**: ChromaDB/HNSW로 인덱싱, 실제 컨텍스트 검색 반영
- **프롬프트 가이드라인**:

  - 도메인/데이터 출처/출력 포맷을 강하게 규정
  - “주어진 데이터 외 추론 금지” 문구 명시

- **비동기/캐싱**: Mongo 쿼리/벡터 검색 결과 캐싱

---

## 🔒 보안

- JWT/세션은 `core/security.py`로 확장 가능
- 파일 업로드 사이즈 제한/확장자 검증(필요 시 `python-multipart` 설정)

---

## 🧭 다음 단계(옵션)

- **RAG → Tavily/Chroma로 교체** (실검색)
- **보고서 자동 생성 고도화** (감정분석 결과 반영, 부정 상위 속성 개선안 도출)
- **프론트 연동**: Vega-Lite Embed, 테이블/필터 UI, LangGraph 상태 표시

---

## ✅ 요약

- **LangGraph는 백엔드 내부 오케스트레이터**로 사용 (별도 서버 불필요)
- `/query/` 엔드포인트는 **자연어→데이터→Q\&A→시각화** 전 과정을 처리
- `/sentiment/*` 4개 엔드포인트로 **리뷰 감정분석** 단일/배치/DB 일괄 처리 가능
- 결과는 MongoDB에 저장되고, 프론트는 응답 JSON을 그대로 시각화/표출 가능
