FROM python:3.12-slim

WORKDIR educ_peduc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /educ_peduc

EXPOSE 8443

# Пути к сертификатам через переменные окружения (можно переопределить)
ENV SSL_KEYFILE=../../certs/bot.key
ENV SSL_CERTFILE=../../certs/bot.crt

CMD cd src/app && uvicorn main:app --host 0.0.0.0 --port 8443 \
    --ssl-keyfile $SSL_KEYFILE \
    --ssl-certfile $SSL_CERTFILE