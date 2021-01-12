FROM python:slim
ENV PYTHONUNBUFFERED=1
WORKDIR /opt/project_bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY bot ./bot
RUN mkdir data
CMD ["python", "-m", "bot"]
