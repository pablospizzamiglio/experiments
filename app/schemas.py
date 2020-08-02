from dataclasses import dataclass
from uuid import UUID

from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    post_load,
    pre_load,
    validate,
)

from app.serializable import Serializable


class AuthQuerySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    customer_id = fields.UUID(required=True)
    provider = fields.Str(required=True, validate=validate.OneOf(["a", "b"]))
    role = fields.Str(required=True)
    return_url = fields.URL(required=True)

    @post_load
    def create_auth_request(self, data, **_):
        return AuthQuery(**data)


class AuthRequestSchema(Schema):
    http_method_key = "httpMethod"
    query_key = "queryStringParameters"

    class Meta:
        unknown = EXCLUDE

    http_method = fields.Str(data_key=http_method_key)
    path = fields.Str()
    query = fields.Nested(AuthQuerySchema, data_key=query_key,)

    @pre_load
    def set_defaults(self, data, **_):
        try:
            data[self.query_key] = data[self.query_key] or {}
        except KeyError as err:
            raise ValidationError(str(err)) from err
        return data

    @post_load
    def create_request(self, data, **_):
        return AuthRequest(**data)


@dataclass
class AuthQuery(Serializable):
    customer_id: UUID
    provider: str
    role: str
    return_url: str


@dataclass
class AuthRequest(Serializable):
    serializer = AuthRequestSchema()
    http_method: str
    path: str
    query: AuthQuery

    @classmethod
    def validate(cls, data):
        return cls.serializer.validate(data)
