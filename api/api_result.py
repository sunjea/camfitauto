class ApiResult:
    def __init__(self, status: int, data: dict):
        self.status = status
        self.data = data

    def __str__(self):
        return str(
            {
                "status": self.status,
                "data": self.data,
            }
        )

