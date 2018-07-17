class PageParseException(Exception):
    pass

class MatchPageParseException(PageParseException):
    pass

class PageNotFoundException(PageParseException):
    pass