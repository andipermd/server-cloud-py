FROM python:3.11.7

WORKDIR /app

RUN python -m venv myvenv
COPY requirements.txt .

RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


