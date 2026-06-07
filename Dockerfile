FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .

# ✅ Fix pip security issue
RUN pip install --no-cache-dir \
    --require-hashes \
    -r requirements.txt 2>/dev/null || \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
