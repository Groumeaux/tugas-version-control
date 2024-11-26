
FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install flake8

RUN flake8 certificate_checker.py

CMD ["python", "certificate_checker.py"]
