class Conversion:
    """
    A helper class handling type conversion for @dataclass arguments

    :param conv: A type constructor such as str, Decimal, etc.
    :param default: Default value to be used if incoming value is None

    `default` will not be converted, it should already have the desired type, e.g.
    `decimal_field: Decimal = Conversion(Decimal, default=Decimal("0"))`
    or `str_field: str = Conversion(str, "")`
    """

    def __init__(self, conv, default=None):
        self.conv = conv
        self._default = default

    def __set_name__(self, owner, name):
        self._name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self._default
        return getattr(instance, self._name, self._default)

    def __set__(self, instance, value):
        if isinstance(value, self.conv):
            setattr(instance, self._name, value)
        else:
            try:
                setattr(instance, self._name, self.conv(value))
            except Exception as e:
                raise ValueError(f"Conversion error for '{self._name}': {value}") from e
