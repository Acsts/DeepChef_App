FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update -y 
RUN apt-get install nano unzip
RUN apt-get install -y python3.10
RUN apt install curl -y

RUN curl -fsSL https://get.deta.dev/cli.sh | sh

COPY requirements.txt /dependencies/requirements.txt
RUN pip --default-timeout=100 install -r /dependencies/requirements.txt

COPY . /home/app

CMD gunicorn model_api:app  --bind 0.0.0.0:$PORT --timeout 100 --worker-class uvicorn.workers.UvicornWorker