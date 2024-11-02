FROM python

RUN apt-get update && \
    apt-get install -y mariadb-server nginx


WORKDIR /app

COPY nginx.conf /etc/nginx/sites-available/default
COPY . /app/

RUN pip install -r requirements.txt

RUN service mariadb start && \
    mariadb -e "CREATE DATABASE IF NOT EXISTS Productivity_2;" && \
    mariadb -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'app_password'; FLUSH PRIVILEGES;"

EXPOSE 80
EXPOSE 8000

CMD service mariadb start && \
    sleep 5 && \
    python database.py && \
    python fill_db.py && \
    service nginx start && \
    gunicorn main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000