FROM python:3-slim-buster

EXPOSE 5000

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN apt-get clean


COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir uploads

COPY . .

VOLUME static/images/cache
VOLUME uploads

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app" ]
