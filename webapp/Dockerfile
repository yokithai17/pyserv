FROM python:3.10-bookworm

EXPOSE 8080
COPY ../requirements.txt /webapp/requirements.txt

WORKDIR /webapp

RUN pip install -r requirements.txt
RUN apt-get update \
&& apt-get install -y wget curl \
&& apt-get clean
RUN wget -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz \
&& tar -xf geckodriver.tar.gz \
&& chmod +x geckodriver \
&& mv geckodriver /usr/local/bin/
RUN apt-get update && apt-get install -y wget bzip2 libxtst6 libgtk-3-0 libx11-xcb-dev libdbus-glib-1-2 libxt6 libpci-dev && rm -rf /var/lib/apt/lists/*

COPY . /webapp

CMD ["python3", "app.py"]
