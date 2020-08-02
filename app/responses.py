import json
import uuid
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from functools import singledispatch
from http import HTTPStatus
from typing import Any, Dict

from app.exceptions import ServiceError


class ResponseBodyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat(timespec="milliseconds")
        if isinstance(o, uuid.UUID):
            return str(o)
        if is_dataclass(o):
            return asdict(o)
        return json.JSONEncoder.default(self, o)


def get_json_headers():
    return {"content-type": "application/json"}


@dataclass
class Response:
    headers: Dict = field(default_factory=get_json_headers)
    code: int = HTTPStatus.OK
    body: Any = None


def jsonify(response):
    """Returns a response dictionary.

        Format:
        {
            "statusCode": <HTTP status code>,
            'headers': {'content-type': 'application/json'},
            "body": "<Stringified body>",
        }
    """
    return make_response(response)


def make_response(obj):
    response = {
        "statusCode": obj.code,
    }
    if obj.headers:
        response["headers"] = obj.headers
    if obj.body:
        body = obj.body
        if isinstance(body, list):
            body = {"data": body}
        response["body"] = json.dumps(body, cls=ResponseBodyEncoder)
    return response


def ok(body, headers=None):
    """Create a response object representing a successful operation.

        :param headers: a dict
        :return: a RedirectResponse
    """
    return Response(headers=headers, body=body)


def no_content(headers=None):
    """Create a response object representing a successful operation with no content.

        :param headers: a dict
        :return: a RedirectResponse
    """
    return Response(headers=headers, code=HTTPStatus.NO_CONTENT)


def redirect(url):
    """Create a response object representing redirection.

        :param url: a URL
        :return: a RedirectResponse
    """
    headers = {
        "Location": url,
    }
    return Response(headers=headers, code=HTTPStatus.FOUND)


@singledispatch
def error(err):
    """Create a properly formatted error response from an unexpected exception.

        :param err: an unexpected Exception
        :return: a Response
    """
    body = {"error": {"message": str(err), "type": type(err).__name__}}
    return Response(code=HTTPStatus.INTERNAL_SERVER_ERROR, body=body)


@error.register(ServiceError)
def _(err):
    """Create a properly formatted error response from a ServiceError.

        :param err: a ServiceError
        :return: a Response
    """
    return Response(code=err.code, body=err.to_dict())
