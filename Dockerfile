FROM python:3.10

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# HuggingFace cross-encoder 모델 미리 다운로드
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

COPY ./app ./app
COPY ./frontend ./frontend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh