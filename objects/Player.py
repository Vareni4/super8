class Player():

    def __init__(self, **kwargs):
        self.s24_id = kwargs.get("s24_id", "")
        self.name = kwargs.get("name", "")
        self.link = kwargs.get("link", "")
