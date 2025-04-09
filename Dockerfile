FROM python:3.11-slim

COPY ./change_ip_in_runner.py ./change_ip_in_runner.py
COPY ./requirements.txt ./requirements.txt

WORKDIR /app

VOLUME ["./gitlab-runner-config:/app/gitlab-runner-config"]

RUN pip install --no-cache-dir ./requirements.txt

CMD ["python", "change_ip_in_runner.py"]
