FROM python:slim
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
RUN apt-get -y update && apt-get -y upgrade

# Chrome and chromedriver
RUN \
	apt-get -y install gnupg wget && \
	wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
	sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
	apt-get -y update && apt-get install -y google-chrome-stable && \
	DRIVER_VER=$(wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
	wget -O chromedriver.zip http://chromedriver.storage.googleapis.com/$DRIVER_VER/chromedriver_linux64.zip && \
	python -m zipfile -e chromedriver.zip /usr/local/bin && \
	chmod +x /usr/local/bin/chromedriver && rm chromedriver.zip
ENV DISPLAY=:99

WORKDIR /opt/facebook_apps_bot
COPY requirements.txt .
RUN	python -m pip install --upgrade pip && \
	pip install -r requirements.txt
COPY bot ./bot
RUN mkdir data
CMD ["python", "-m", "bot"]
