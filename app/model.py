# 모델 로딩과 추론
import os
import io
import logging
import joblib
import pandas as pd
from typing import Any
from pathlib import Path


logger = logging.getLogger(__name__)


FIELD_TO_COLUMN = {
    "age": "나이",
    "gender": "성별",
    "annual_income": "연소득",
    "employment_years": "근속연수",
    "housing_type": "주거형태",
    "credit_score": "신용점수",
    "existing_loan_count": "기존대출건수",
    "annual_card_usage": "연간카드사용액",
    "debt_ratio": "부채비율",
    "loan_amount": "대출신청액",
    "loan_purpose": "대출목적",
    "repayment_method": "상환방식",
    "loan_period": "대출기간",
}


class LoanModel:
    def __init__(self):
        self.pipeline = None
        self.label_encoders: dict[str, Any] = {}
        self.feature_name: list[str] = []
        self.threshold: float = 0.5
        self.model_version: str = "1.0.0"


    def load(self, model_dir: str = "models") -> None:
        script_dir = Path(__file__).parent
        model_path = script_dir.parent / model_dir

        pipeline_path = model_path / "loan_pipeline.pkl"
        feature_names_path = model_path / "feature_names.pkl"
        label_encoders_path = model_path / "label_encoders.pkl"

        if not pipeline_path.exists():
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {pipeline_path}")
        if not feature_names_path.exists():
            raise FileNotFoundError(f"특성 이름 파일을 찾을 수 없습니다: {feature_names_path}")
        if not label_encoders_path.exists():
            raise FileExistsError(f"라벨 인코더 파일을 찾을 수 없습니다: {label_encoders_path}")
        
        self.pipeline = joblib.load(pipeline_path)
        self.feature_name = joblib.load(feature_names_path)
        self.label_encoders = joblib.load(label_encoders_path)

        logging.info("모델 로드 완료!!")



    @staticmethod
    # 내부 메소드
    def _map_to_korean(data: dict[str, Any]) -> dict[str, Any]:
        return {FIELD_TO_COLUMN.get(k, k): v for k, v in data.items()} # {"age": 30} → {"나이": 30}
    

    def predict(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.pipeline is None:
            raise RuntimeError("모델이 로드되지 않았습니다. load() 함수를 먼저 호출하세ㅇ요.")
        
        mapped = self._map_to_korean(data)        

        # mapped 에 없는 키가 있으면 KeyError 발생
        df = pd.DataFrame([mapped])[self.feature_name]


        for col, encoder in self.label_encoders.items():
            if col in df.columns:
                df[col] = encoder.transform(df[col]) # 문자 -> 숫자 변환
        
        probability = float(self.pipeline.predict_proba(df)[0,1])  # 대출 승인 확률
        approved = probability >= self.threshold

        risk_grade = self._get_risk_grade(probability)

        return {
            "approved": approved,
            "probability": probability,
            "risK_grade": risk_grade
        }


    @staticmethod
    def _get_risk_grade(probality:float) -> str:
        if probality >= 0.75:
            return "A"
        elif probality >= 0.5:
            return "B"
        elif probality >= 0.25:
            return "C"
        else:
            return "D"



