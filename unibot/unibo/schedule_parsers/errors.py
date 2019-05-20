class ParseError(Exception):
    def __init__(self, url=''):
        super().__init__(f"Invalid input data for url '{url}'")
