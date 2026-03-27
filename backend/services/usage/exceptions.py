class QuotaExceededError(Exception):
    """Raised when a user hits monthly campaign or token limits."""

    def __init__(self, message: str, *, code: str = "quota_exceeded"):
        super().__init__(message)
        self.code = code
