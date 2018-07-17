class Player():

    def __init__(self, **kwargs):
        self.s24_id = kwargs.get("s24_id", None)
        self.name = kwargs.get("name", None)
        self.link = kwargs.get("link", None)
