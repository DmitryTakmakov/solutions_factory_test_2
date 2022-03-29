FROM python:3.8.10

WORKDIR /backend
RUN pip install --upgrade pip
COPY ./ ./
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN mv wait-for /bin/wait-for
RUN apt-get update && apt-get install -y netcat