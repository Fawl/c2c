class InstrumentNotFound(Exception):

    def __init__(self, payload):
        super().__init__("REJECTED – INSTRUMENT NOT FOUND")
        self.errors = payload

    def __str__(self):
        return self.message

class MismatchCurrency(Exception):

    def __init__(self, payload):
        super().__init__("REJECTED – MISMATCH CURRENCY")
        self.errors = payload

    def __str__(self):
        return self.message

class InvalidSize(Exception):

    def __init__(self, payload):
        super().__init__("REJECTED – INVALID LOT SIZE")
        self.errors = payload

    def __str__(self):
        return self.message

class PositionCheck(Exception):

    def __init__(self, payload):
        super().__init__("REJECTED – POSITION CHECK FAILED")
        self.errors = payload

    def __str__(self):
        return self.message