FROM python:3.9.0

WORKDIR gitlab-extractor

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src ./src

CMD ["python", "-m", "src.server"]
