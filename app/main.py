import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.model import LoanModel
from app.schemas import LoanRequest, LoanResponse
from fastapi import HTTPException
import uuid
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FastAPI 앱의 시작/종료 시 실행할 코드를 정의한다.
# yield 이전 — 서버가 요청을 받기 전에 실행 (모델 로드, DB 연결 등 초기화)
# yield 이후 — 서버가 종료될 때 실행 (리소스 해제, 연결 종료 등 정리)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("대출 심사 모델을 로드합니다.")

    model = LoanModel()
    try:
        model.load() # 모델 로드
        logger.info("모델 로드 성공")
    except Exception as e:
        logger.error(f"모델 로드 실패: {e}")
        logger.warning("/predict 엔드 포인트는  모델 로드 후 사용가능합니다.")

    # app.state는 FastAPI가 제공하는 전역 저장소입니다.
    # 로드된 LoanModel 객체를 앱 전체에서 공유할 수 있도록 저장합니다.
    # 모델 로드는 비용이 크기 때문에 요청마다 새로 로드하면 안 됩니다.
    app.state.model = model

    yield

    logger.info("대출 심사 API 서비스를 종료합니다.")


app = FastAPI(
    title='대출 심사 예측 API', 
    description='ML 모델 기반 대출 승인 여부를 예측하는 API',
    version='1.0.0',
    lifespan=lifespan        
)


@app.get("/")
async def root():
    logger.info("Start FastAPI Server")
    return {"message": "FastAPI 서버 동작"}


@app.get("/health")
async def health_check():
    model = app.state.model
    if model.pipeline is not None:
        return {"status": "healthy", "model_version": model.model_version}
    else:
        return {"status": "unhealthy", "message": "모델이 로드되지 않았습니다."}
    

# 추론 
@app.post("/predict", response_model=LoanResponse)
async def predict(request: LoanRequest):
    model = app.state.model
    request_id = str(uuid.uuid4()) 
    start_time = datetime.now()

    try:
        # Pydantic 객체를 딕셔너리로 변환해 모델에 전달
        result = model.predict(request.model_dump())
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        # CloudWatch에 남길 예측 로그
        log_data = {
            "request_id": request_id,
            "timestamp": start_time.isoformat(),
            **request.model_dump(),
            "approved": result["approved"],
            "probability": result["probability"],
            "risk_grade": result["risk_grade"],
            "model_version": model.model_version,
            "latency_ms": round(latency_ms, 2)
        }

        # CloudWatch Logs Insights에서 이 패턴으로 필터링하여 예측 로그만 쿼리하기 위한 키워드입니다.
        # log_data 딕셔너리를 JSON 문자열로 변환해 logger.info()로 출력합니다
        # logger.info(f"PREDICTION_LOG: {json.dumps(log_data, ensure_ascii=False)}")
        log_data["log_type"] = "PREDICTION_LOG"
        logger.info(json.dumps(log_data, ensure_ascii=False))

        #  결과 딕셔너리를 응답 스키마로 변환하여 반환
        return LoanResponse(**result)
    
    except RuntimeError as e:  # 모델이 로드되지 않은 경우
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e: 
        raise HTTPException(status_code=422, detail='입력값 처리 오류')
    except Exception as e: # 그 외 서버 내부 오류
        raise HTTPException(status_code=500)
    