from functools import wraps

from marshmallow import exceptions

from app.exceptions import ValidationError


def wrap_error(method):
    @wraps(method)
    def wrap(*args, **kwargs):

        try:
            return method(*args, **kwargs)
        except exceptions.ValidationError as err:
            raise ValidationError.wrap(err) from err

    return wrap


class Serializable:
    serializer = None

    def dumps(self):
        return self.serializer.dumps(self)

    def dump(self):
        return self.serializer.dump(self)

    @classmethod
    @wrap_error
    def loads(cls, json_data):
        return cls.serializer.loads(json_data)

    @classmethod
    @wrap_error
    def load(cls, json):
        return cls.serializer.load(json)
