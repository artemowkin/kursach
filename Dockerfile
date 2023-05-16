FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /code/
RUN pip install -U pdm
COPY pyproject.toml pdm.lock /code/
RUN pdm install
COPY app/ /code/app/