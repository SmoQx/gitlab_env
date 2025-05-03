FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt update

RUN apt install -y git unzip

RUN unzip proj.zip

RUN pip install --no-cache-dir -r requirements.txt

CMD ["git", "push", "http://usr:123password@gitlab/usr/automatyzacja"]
