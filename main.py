import functools

from app.exceptions import ValidationError
from app.responses import error, jsonify, ok
from app.schemas import AuthRequest


def service(event):
    return "awesome result after calculation"


def validate_request(data):
    return AuthRequest.validate(data)


def handler(validate=None):
    validators = []
    if callable(validate):
        validators = [validate]
    elif isinstance(validate, list):
        validators = validate
    else:
        raise ValueError(
            "The 'validate' parameter must be a callable "
            "or a collection of callables."
        )

    def validate_params(func):
        @functools.wraps(func)
        def serialize(*args, **kwargs):
            event = args[0]
            try:
                errors = []
                for validate in validators:
                    validation_result = validate(event)
                    if validation_result:
                        errors.append(validation_result)
                if errors:
                    raise ValidationError(context=errors)

                response = func(*args, **kwargs)
            except Exception as err:
                response = error(err)
            return jsonify(response)

        return serialize

    return validate_params


@handler(validate=validate_request)
def main(event, context):  # simulates an AWS lambda function
    return ok(service(event))


if __name__ == "__main__":
    event = {
        "httpMethod": "GET",
        "path": "/v1/oauth2/auth",
        "queryStringParameters": {
            "customer_id": "2a170066-62fa-4a6e-afee-965ec3615fd2",
            "provider": "a",
            "role": "admin",
            "return_url": "https://www.reddit.com",
        },
    }
    print(main(event, None))
