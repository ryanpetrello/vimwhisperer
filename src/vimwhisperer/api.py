import json
import os.path
import sys
import webbrowser

import boto3
from botocore import UNSIGNED
from botocore.client import Config

from .auth import CodeWhispererSsoAuthManager

from .constants import RTS_PROD_ENDPOINT, RTS_PROD_REGION, SSO_START_URL, TOKEN_CACHE



def get_token(registration = None):
    manager = CodeWhispererSsoAuthManager()
    registration = registration or manager.register_client().data
    deviceAuth = manager.device_authorization(registration, startUrl=SSO_START_URL)
    url = deviceAuth.data["verificationUriComplete"]
    print(f"Complete device authorization at {url} to proceed.")
    webbrowser.open(url)
    token = manager.create_token(registration, deviceAuth.data).data
    token['clientId'] = registration['clientId']
    token['clientSecret'] = registration['clientSecret']
    return token


def refresh_token():
    token = json.load(open(TOKEN_CACHE))
    try:
        return CodeWhispererSsoAuthManager().refresh(token).data
    except:
        # generally speaking, the refresh token has expired
        token = get_token(token)
        with open(TOKEN_CACHE, "w") as f:
            json.dump(token, f)
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
        token = refresh_token()
    else:
        with open(TOKEN_CACHE, "w") as f:
            token = get_token()
            json.dump(token, f)
            print(
                f"Successfully authenticated to {RTS_PROD_ENDPOINT}.  "
                f"Credentials cached locally at {TOKEN_CACHE}"
            )

    def add_header(request, **kwargs):
        request.headers.add_header("Authorization", "Bearer " + token["accessToken"])

    client.meta.events.register_first("before-sign.*.*", add_header)
    return client


def complete(prompt, language='python'):
    prompt = prompt or "\n".join(sys.stdin.readlines())

    def _generate_completions():
        client = get_client()
        try:
            return client.generate_completions(
                fileContext={
                    "leftFileContent": prompt,
                    "rightFileContent": "",
                    "filename": __file__,
                    "programmingLanguage": {"languageName": language},
                }
            )
        except client.exceptions.AccessDeniedException:
            refresh_token()
            return _generate_completions()

    response = _generate_completions()
    for c in response.get("completions", []):
        for line in c["content"].strip('\n').splitlines():
            yield line
