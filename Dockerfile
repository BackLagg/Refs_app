FROM python:3.9.13

RUN mkdir /fastapi_app_refs

WORKDIR /fastapi_app_refs

COPY requirements .

RUN pip install -r requirements

COPY . .

CMD alembic upgrade head && gunicorn src.app:app --bind=0.0.0.0:8080

