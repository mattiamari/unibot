class ParseError(Exception):
    def __init__(self, url=''):
        super().__init__("Invalid input data for url '{}'".format(url))
