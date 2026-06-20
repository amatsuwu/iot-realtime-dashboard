# 前端也可以用多階段構建，確保環境乾淨
FROM python:3.9-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ==========================================
# 最終運行階段
# ==========================================
FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY . /app

ENV PYTHONPATH=/app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
