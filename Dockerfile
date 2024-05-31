# syntax=docker/dockerfile:1.4

FROM python:3.9
EXPOSE 8000

WORKDIR /app 
COPY requirements.txt /app

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
COPY src /app/src

CMD ["fastapi", "run", "src/app.py", "--port", "8000"]
