from http import HTTPStatus


class ServiceError(Exception):
    """Base class for all service-related errors."""

    code = None
    description = None

    def __init__(self, code=None, description=None):
        if code:
            self.code = code

        if description:
            self.description = description

        super().__init__(self.description)

    def to_dict(self):
        return {"error": {"message": self.description, "type": type(self).__name__}}

    @classmethod
    def wrap(cls, exception):
        return cls(code=HTTPStatus.INTERNAL_SERVER_ERROR, description=str(exception))


class BadRequest(ServiceError):
    code = HTTPStatus.BAD_REQUEST
    description = "The client sent a request that this server could not understand."

    def __init__(self, context=None):
        self.context = context
        super().__init__(self.code, self.description)

    def to_dict(self):
        d = super().to_dict()
        d["error"]["context"] = self.context
        return d

    @classmethod
    def wrap(cls, exception):
        """Wrap third-party library exceptions.

        Helps with keeping the code lowly coupled to the implementation
        details of third party libraries like `marshmallow`.

        :return a ValidationError instance
        """
        try:
            context = exception.normalized_messages()
        except AttributeError:
            context = None
        finally:
            return cls(context=context)


class ValidationError(BadRequest):
    description = "One or more parameters are invalid."


class NotFound(ServiceError):
    code = HTTPStatus.NOT_FOUND
    description = "The requested URL was not found on the server."


class InternalServerError(ServiceError):
    code = HTTPStatus.INTERNAL_SERVER_ERROR
    description = (
        "The server encountered an internal error and was unable to"
        " complete your request."
    )

    def __init__(self, description=None, original_exception=None):
        self.original_exception = original_exception
        super().__init__(description=description)

    @classmethod
    def wrap(cls, exception):
        return cls(description=str(exception), original_exception=exception)
