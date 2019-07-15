class Base:
    def __init__(self):
        self._state = 0


class GPIO(Base):
    pass


class Test(Base):
    pass


class Manager:
    def __init__(self):
        self._relays = {}

    def create(self, id, **kwargs):
        pass

    def delete(self, id):
        pass

    def command(self, id, command, **kwargs):
        pass
