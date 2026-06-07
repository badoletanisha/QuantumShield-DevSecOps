FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .

# ✅ Fix 1: Lock versions with --only-binary
RUN pip install --no-cache-dir \
    --only-binary :all: \
    -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
