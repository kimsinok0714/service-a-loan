
# Base 이미지
FROM python:3.10-slim


# 컨테이너 내부 작업 폴더를 app으로 설정합니다
WORKDIR /app

COPY requirements.txt .

# --no-cache-dir는 pip 캐시를 남기지 않아 이미지 크기를 줄이는 데 도움이 됩니다.
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 8000

# 컨테이너 시작 시 Uvicorn으로 FastAPI 앱을 실행합니다.
# 0.0.0.0으로 바인딩해서 컨테이너 외부에서도 접근 가능하게 합니다.

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
