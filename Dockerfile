FROM python:3.9

COPY . /build
COPY poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-dev \
 && pip uninstall --yes poetry

EXPOSE 8089 5557

RUN useradd --create-home locust
USER locust
WORKDIR /home/locust
ENTRYPOINT ["locust"]
ENV PYTHONUNBUFFERED=1
