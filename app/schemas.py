# 입출력 확정, Pydantic을 사용하여 타입 검증

from pydantic import BaseModel, Field

class LoanRequest(BaseModel):
    """대출 심사를 위한 고객 정보 입력 스키마 생성"""
    age: int = Field(..., description="고객의 나이", ge=19, le=100)  # 필수 입력 값
    gender: str = Field(..., description="고객의 성별", examples=["남", "여"])
    annual_income: float = Field(..., description="고객의 연간 소득", examples=[5000.0])
    employment_years: int = Field(..., description="고갱의 근속연수", ge=0, le=50, examples=[5])
    housing_type: str = Field(..., description="주거형태", examples=["자가"])
    credit_score: int = Field(..., description="고객의 신용 점수", ge=300, le=900, examples=[720])
    existing_loan_count: int = Field(..., description="기존대출건수", examples=[2])
    annual_card_usage: float = Field(..., description="연간카드사용액", ge=0, examples=[2000.0])
    debt_ratio: float = Field(..., description="부채비율", ge=0, le=100, examples=[35.5])
    loan_amount: float = Field(..., description="대출신청액", ge=100, examples=[3000.0])
    loan_purpose: str = Field(..., description="대출목적", examples=["주택구입"])
    loan_period: int = Field(..., description="대출기간", ge=6, le=360, examples=[36])
    repayment_method: str = Field(..., description="상환방식", examples=["원리금균등"])
    model_config = {  # FastAPI의 /docs (Swagger UI)에 표시될 요청 예시 데이터를 정의하는 설정입니다.
        "json_schema_extra": {
            #  Swagger UI에서 "Try it out" 버튼을 눌렀을 때 자동으로 채워지는 샘플 값입니다.
            "examples": [
                {
                    "age": 35,
                    "gender": "남",
                    "annual_income": 5000.0,
                    "employment_years": 5,
                    "housing_type": "자가",
                    "credit_score": 720,
                    "existing_loan_count": 2,
                    "annual_card_usage": 2400.0,
                    "debt_ratio": 35.5,
                    "loan_amount": 3000.0,
                    "loan_purpose": "주택구입",
                    "repayment_method": "원리금균등",
                    "loan_period": 36,
                }
            ]
        }
    }



class LoanResponse(BaseModel):
    approved: bool = Field(..., description="대출 숭인 여부(True: 승인, False: 거부)")
    probability: float = Field(..., description="대출 승인 확률", ge=0.0, le=1.0)
    risK_grade: str = Field(..., description="리스크 등급('A', 'B', 'C', 'D')")

    
