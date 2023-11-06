# Exception raised when an sdf file failed to parse correctly
class InvalidSdf (Exception):
    def __init__(self, message):
        self.message = "ERROR: " + message
        super().__init__(self.message)

# Exception raised when trying to insert a duplicate entry into database
class DuplicateEntry (Exception):
    def __init__(self, message):
        self.message = "ERROR: " + message
        super().__init__(self.message)
