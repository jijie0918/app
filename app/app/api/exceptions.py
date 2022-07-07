"""REST API for error."""
from flask import jsonify
from app import app


class RESTAPIException(Exception):
    """REST API exception."""

    def __init__(self, message, status_code):
        """Initialize message and status_code."""
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        """Get message and status_code."""
        respone_value = {}
        respone_value['message'] = self.message
        respone_value['status_code'] = self.status_code
        return respone_value


class NotFoundException(RESTAPIException):
    """404 NotFound error."""

    def __init__(self):
        """Initialize message, status_code for 404."""
        super().__init__("Not Found", 404)


class BadRequestException(RESTAPIException):
    """400 Badrequest error."""

    def __init__(self):
        """Initialize message, status_code for 400."""
        super().__init__("Bad Request", 400)


class ForbiddenException(RESTAPIException):
    """403 Forbidden error."""

    def __init__(self):
        """Initialize message, status_code for 403."""
        super().__init__("Forbidden", 403)


@app.errorhandler(RESTAPIException)
def handle_api_exception(error):
    """Get error message and status_code."""
    response = jsonify(error.to_dict())
    return response, error.status_code
