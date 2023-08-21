import time

import boto3
from botocore.exceptions import ClientError
from ..constants import (
    CLIENT_REGISTRATION_TYPE,
    CLIENT_NAME,
    SCOPES,
    START_URL,
    DEVICE_GRANT_TYPE,
    REFRESH_GRANT_TYPE,
    SSO_OIDC,
    OIDC_BUILDER_ID_ENDPOINT,
    OIDC_BUILDER_ID_REGION,
)
from ..utils import (
    generate_succeeded_service_response,
    generate_client_error_oidc_service_response,
)


class CodeWhispererSsoAuthManager:
    _instance = None
    _oidc_client = boto3.client(
        SSO_OIDC,
        endpoint_url=OIDC_BUILDER_ID_ENDPOINT,
        region_name=OIDC_BUILDER_ID_REGION,
    )
    login_cancelled = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def refresh(self, client_registration):
        try:
            new_token_response = self._oidc_client.create_token(
                clientId=client_registration["clientId"],
                clientSecret=client_registration["clientSecret"],
                grantType=REFRESH_GRANT_TYPE,
                refreshToken=client_registration["refreshToken"],
            )
            return generate_succeeded_service_response(new_token_response)
        except ClientError as e:
            return generate_client_error_oidc_service_response(e)

    def register_client(self):
        try:
            client_registration_response = self._oidc_client.register_client(
                clientName=CLIENT_NAME,
                clientType=CLIENT_REGISTRATION_TYPE,
                scopes=SCOPES,
            )
            return generate_succeeded_service_response(client_registration_response)
        except ClientError as e:
            return generate_client_error_oidc_service_response(e)

    def device_authorization(self, client_registration, startUrl=START_URL):
        try:
            device_authorization_response = (
                self._oidc_client.start_device_authorization(
                    clientId=client_registration["clientId"],
                    clientSecret=client_registration["clientSecret"],
                    startUrl=startUrl,
                )
            )
            return generate_succeeded_service_response(device_authorization_response)
        except ClientError as e:
            return generate_client_error_oidc_service_response(e)

    def create_token(self, client_registration, device_authorization):
        device_code = device_authorization["deviceCode"]
        expires_in = device_authorization["expiresIn"]
        interval = device_authorization["interval"]

        for n in range(1, expires_in // interval + 1):
            if self.login_cancelled:
                self.login_cancelled = False
                return None
            time.sleep(interval)
            try:
                token_response = self._oidc_client.create_token(
                    grantType=DEVICE_GRANT_TYPE,
                    deviceCode=device_code,
                    clientId=client_registration["clientId"],
                    clientSecret=client_registration["clientSecret"],
                )
                return generate_succeeded_service_response(token_response)
            except self._oidc_client.exceptions.AuthorizationPendingException:
                pass
            except ClientError as e:
                return generate_client_error_oidc_service_response(e)

    def cancel_login(self):
        self.login_cancelled = True
