FROM python:3.11-slim
LABEL authors="Roman F."

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip


COPY app/ ./app/
COPY main.py ./main.py
COPY config.py ./config.py

CMD ["python", "main.py"]

