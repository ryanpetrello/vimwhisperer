import json
import os.path
import sys
import webbrowser

import boto3
from botocore import UNSIGNED
from botocore.client import Config

from .auth import CodeWhispererSsoAuthManager

from .constants import RTS_PROD_ENDPOINT, RTS_PROD_REGION

SSO_START_URL = os.environ.get(
    "VIM_AWS_SSO_START_URL", "https://view.awsapps.com/start"
)
AWS_REGION = os.environ.get("VIM_AWS_SSO_REGION", "us-east-1")
TOKEN_CACHE = f'{os.path.expanduser("~")}/.vim/.aws-code-whisperer-auth'


def get_token():
    manager = CodeWhispererSsoAuthManager()
    registration = manager.register_client()
    deviceAuth = manager.device_authorization(registration.data, startUrl=SSO_START_URL)
    url = deviceAuth.data["verificationUriComplete"]
    print(f"Complete device authorization at {url} to proceed.")
    webbrowser.open(url)
    token = manager.create_token(registration.data, deviceAuth.data).data
    token['clientId'] = registration.data['clientId']
    token['clientSecret'] = registration.data['clientSecret']
    return token


def get_client():
    session = boto3.Session(region_name="us-east-1")
    session._loader.search_paths.extend(
        [os.path.dirname(os.path.realpath(__file__)) + "/data"]
    )
    client = session.client(
        service_name="amazoncodewhispererservice",
        endpoint_url=RTS_PROD_ENDPOINT,
        region_name=RTS_PROD_REGION,
        config=Config(signature_version=UNSIGNED),
    )
    if os.path.exists(TOKEN_CACHE):
        token = json.load(open(TOKEN_CACHE))
    else:
        with open(TOKEN_CACHE, "w") as f:
            json.dump(get_token(), f)
            print(
                f"Successfully authenticated to {RTS_PROD_ENDPOINT}.  "
                f"Credentials cached locally at {TOKEN_CACHE}"
            )

    def add_header(request, **kwargs):
        request.headers.add_header("Authorization", "Bearer " + token["accessToken"])

    client.meta.events.register_first("before-sign.*.*", add_header)
    return client


def complete(prompt):
    client = get_client()
    prompt = prompt or "\n".join(sys.stdin.readlines())

    def _generate_completions():
        return client.generate_completions(
            fileContext={
                "leftFileContent": prompt,
                "rightFileContent": "",
                "filename": __file__,
                "programmingLanguage": {"languageName": "python"},
            }
        )

    try:
        response = _generate_completions()
    except client.exceptions.AccessDeniedException:
        pass

    for c in response.get("completions", []):
        for line in c["content"].strip('\n').splitlines():
            yield line
