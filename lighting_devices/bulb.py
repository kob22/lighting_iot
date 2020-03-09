class LightBulb:
    """Light Bulb

    name is the name of light bulb
    light is boolean, if lighting
    status is boolean, true if light bulb is working
    """
    def __init__(self, name, light, status=False):

        self.name = name
        self.light = light
        self.status = status

    @property
    def light(self):
        return self.__light

    @light.setter
    def light(self, light: bool = False):

        if isinstance(light, bool):
            self.__light = light
        else:
            raise TypeError("Light must be a boolean")

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status: bool = False):
        if isinstance(status, bool):
            self.__status = status
        else:
            raise TypeError("Status must be a boolean")