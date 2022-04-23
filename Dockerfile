# ARG PYTHON_VERSION
FROM python:3.6.1-alpine
RUN apk update
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "main.py"]