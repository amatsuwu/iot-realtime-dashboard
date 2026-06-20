# 採用多階段構建 (Multi-stage build) 來減小最後的 Image 大小
FROM python:3.9-slim as builder

WORKDIR /app
# 安裝編譯 C extension 所需的系統套件 (asyncmy, bcrypt 需要)
RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev

COPY requirements.txt .
# 產生 wheel 檔，方便下一階段直接安裝
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ==========================================
# 最終運行階段 (Production Image)
# ==========================================
FROM python:3.9-slim

WORKDIR /app

# 安裝 MariaDB client lib，因為 asyncmy 執行期需要
RUN apt-get update && apt-get install -y libmariadb3 && rm -rf /var/lib/apt/lists/*

# 從 builder 階段複製編譯好的 wheel 檔並安裝
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# 複製專案程式碼
COPY . /app

# 設定 PYTHONPATH 讓 Python 找得到 backend 模組
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
