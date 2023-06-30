class Unit:
    def __init__(self, name: str):
        """Constructor.

        :param str name: The name of the unit
        """

        self._name = name

    @property
    def name(self) -> str:
        """Returns the name of the unit"""
        return self._name

    def __str__(self) -> str:
        return self._name

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Unit):
            return NotImplemented
        return self._name == __value.name
