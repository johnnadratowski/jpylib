class ResponseException(Exception):
    def __init__(self, response):
        super(Exception, self).__init__()
        self.response = response
