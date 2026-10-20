class AuthError(Exception):
    """Base class for authentication errors."""

    def __init__(self, error, status_code):
        super().__init__(error)
        self.error = error
        self.status_code = status_code