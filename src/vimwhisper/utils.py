from datetime import datetime, timedelta

from .constants import ERROR_CODE_TO_USER_MESSAGE_MAP


def time_from_now(time):
    now = datetime.utcnow()
    future = now + timedelta(seconds=time)
    return int(future.timestamp())


def is_expired(time):
    now = datetime.utcnow().timestamp()
    return time <= now


class ServiceErrorInfo:
    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message
        self.user_message = self.get_user_friendly_error_message()

    @property
    def __dict__(self):
        return {
            "error_code": self.error_code,
            "error_message": self.error_message,
            "user_message": self.user_message,
        }

    def get_user_friendly_error_message(self):
        error_key = self.error_code + ": " + self.error_message
        user_message = ERROR_CODE_TO_USER_MESSAGE_MAP.get(error_key)
        return user_message if user_message else error_key


class ServiceResponseStatus:
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class ServiceResponse:
    def __init__(self, status, data, error_info, request_id, session_id):
        self.status = status
        self.data = data
        self.error_info = error_info
        self.request_id = request_id
        self.session_id = session_id

    @property
    def __dict__(self):
        return {
            "status": self.status,
            "data": self.data,
            "error_info": self.error_info.__dict__ if self.error_info else None,
            "x-amzn-requestid": self.request_id,
            "x-amzn-sessionid": self.session_id,
        }


def generate_succeeded_service_response(response):
    request_id = response["ResponseMetadata"]["RequestId"]
    session_id = response["ResponseMetadata"]["HTTPHeaders"].get("x-amzn-sessionid")
    response_data = {k: v for k, v in response.items() if k != "ResponseMetadata"}
    return ServiceResponse(
        ServiceResponseStatus.SUCCESS, response_data, None, request_id, session_id
    )


def generate_client_error_oidc_service_response(e):
    request_id = e.response["ResponseMetadata"]["RequestId"]
    error_info = ServiceErrorInfo(
        e.response["Error"]["Code"], e.response["error_description"]
    )
    return ServiceResponse(
        ServiceResponseStatus.ERROR, None, error_info, request_id, None
    )


def generate_client_error_codewhisperer_service_response(e):
    request_id = e.response["ResponseMetadata"]["RequestId"]
    error_info = ServiceErrorInfo(e.response["Error"]["Code"], e.response["message"])
    return ServiceResponse(
        ServiceResponseStatus.ERROR, None, error_info, request_id, None
    )
