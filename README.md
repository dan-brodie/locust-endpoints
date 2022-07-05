[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Locust

Locust is a load testing suite for python.

This example repo shows you how to test an endpoint which requires authentication with a Google Service Account.

## Running

This repo uses poetry - use the provided vscode devcontainer - further details here `https://python-poetry.org/docs/basic-usage/`
A dockerfile is provided also.
You will however need your GOOGLE_APPLICAION_CREDENTIALS environment variable to be accessible for secret manager to work.

```sh
poetry run locust --host=https://sample-l6wc7ausiq-ew.a.run.app
```

## Installing

```sh
poetry install
```

## Testing

```sh
poetry run bandit .
poetry run black .
```

## Sample

The Sample folder contains an endpoints spec which can be used with the google cloudrun/endpoints demo instructions
`https://cloud.google.com/endpoints/docs/openapi/set-up-cloud-run-espv2`
