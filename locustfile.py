#!/usr/bin/env python
from locust import events, HttpUser, task
from google.cloud import secretmanager
import google.auth.crypt, google.auth.jwt
import json, time, logging

project_id = "db-dns-01"
sa_name = "sample-sa@db-dns-01.iam.gserviceaccount.com"
secret_id = "sample-sa"
target_url = "https://sample-l6wc7ausiq-ew.a.run.app"
version_id = "1"

def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    sa_raw = response.payload.data.decode('UTF-8')
    sa = json.loads(sa_raw)

    return sa


def generate_jwt(sa, sa_name, target_url):
    """
    Generate the connection token for endpoints. creating the signing payload. sign. return the token.
    - iat expires after 'expiry_length' seconds.
    - iss must match 'issuer' in the security configuration in your swagger spec (e.g. service account email). It can be any string.
    - aud must be either your Endpoints service name, or match the value specified as the 'x-google-url' in the OpenAPI document.
    - sub and email should match the service account's email address.
    """
    now = int(time.time())

    payload = {
        "iat": now,
        "exp": now + 3600,
        "iss": sa_name,
        "aud": target_url,
        "sub": sa_name,
        "email": sa_name,
    }

    signer = google.auth.crypt.RSASigner.from_service_account_info(sa)
    jwt = google.auth.jwt.encode(signer, payload)
    
    return jwt

class EndpointTest(HttpUser):
    """
    This class defines a set of tasks to be completed by locust.
    - we are taking the token we signed in common.auth and adding it to the header for auth.
    - we are hitting a particular endpoint.
    - we can add multiple tasks here
    """
    def on_start(self):
        self.sa = access_secret_version(project_id, secret_id, version_id)
        self.jwt = generate_jwt(self.sa, sa_name, target_url)

    @task
    def device_type(self):
        headers = {
            "Authorization": "Bearer {}".format(self.jwt.decode("utf-8")),
            "content-type": "application/json",
        }
        self.client.get("/hello", headers=headers, verify=False)

    @events.quitting.add_listener
    def _(environment, **kw):
        """
        On quit determine exit code based on test results. 
        useful in CI.
        """
        if environment.stats.total.fail_ratio > 0.01:
            logging.error("Test failed due to failure ratio > 1%")
            environment.process_exit_code = 1
        elif environment.stats.total.avg_response_time > 200:
            logging.error(
                "Test failed due to average response time ratio > 200 ms"
            )
            environment.process_exit_code = 1
        elif environment.stats.total.get_response_time_percentile(0.95) > 800:
            logging.error(
                "Test failed due to 95th percentile response time > 800 ms"
            )
            environment.process_exit_code = 1
        else:
            environment.process_exit_code = 0
