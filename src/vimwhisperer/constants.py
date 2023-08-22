INVALID_TOKEN_EXCEPTION_MESSAGE = (
    "The security token included in the request is expired"
)
RTS_PROD_ENDPOINT = "https://codewhisperer.us-east-1.amazonaws.com/"
RTS_PROD_REGION = "us-east-1"

ERROR_CODE_TO_USER_MESSAGE_MAP = {
    "InvalidGrantException: Invalid grant provided": "InvalidGrantException: Login failed. Try login again later."
}

START_URL = "https://view.awsapps.com/start"
SSO_OIDC = "sso-oidc"
OIDC_BUILDER_ID_ENDPOINT = "https://oidc.us-west-2.amazonaws.com"
OIDC_BUILDER_ID_REGION = "us-west-2"
SCOPES = ["sso:account:access", "codewhisperer:completions"]
CLIENT_NAME = "CodeWhisperer for Vim"
CLIENT_REGISTRATION_TYPE = "public"
DEVICE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"
REFRESH_GRANT_TYPE = "refresh_token"
