from enum import Enum

class UpscaleErrorCode(Enum):
    NonTokenError = {
    "code": 401,
    "message": "Failed to connect. Contact service administrator.",
    "log": "Upscale API request error with non token. Please purchase token."
    }
    APIError = {
        "code": 500,
        "message": "Failed to request. Contact service administrator.",
        "log": "API Error. Please check api."
    }