FROM python:3.8-slim

RUN apt update
RUN apt install nano -y
RUN apt install vim -y
RUN apt install screen -y
RUN apt install curl -y
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY *.py ./
COPY *.sh ./
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]