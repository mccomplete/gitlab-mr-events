FROM python:3.9.0

WORKDIR gitlab-extractor

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src ./src

# 2823570 is the gitlab group ID for the sagemath organization https://gitlab.com/sagemath
ENV GITLAB_GROUP_ID=2823570

CMD ["python", "-m", "src.server"]
