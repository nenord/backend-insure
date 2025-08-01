
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code


CMD ["uvicorn", "main:app", "--port", "8080", "--host", "0.0.0.0"]