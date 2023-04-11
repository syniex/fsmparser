import re
import typing


if typing.TYPE_CHECKING:
    from fsmparser._template._value import FSMValue


class OptionError(Exception):
    ...


class SkipRecord(OptionError):
    ...


class FSMBaseOption:
    registry: 'typing.Dict[str, type[FSMBaseOption]]' = {}
    option_re: 're.Pattern[str]'

    def __init__(self, value: 'FSMValue', param: str) -> None:
        self.value = value
        self._param = param

    def __init_subclass__(cls: 'type[FSMBaseOption]') -> None:
        FSMBaseOption.registry[cls.__name__] = cls
        FSMBaseOption.option_re = re.compile(fr'(?P<name>{"|".join(cls.registry.keys())})(?:\[(?P<param>.*)\])?')

    def validate(self) -> None:
        ...

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def create(self) -> None:
        return None

    def clear(self) -> None:
        return None

    def save(self) -> None:
        return None

    def assign(self) -> None:
        return None

    def clear_all(self) -> None:
        return None


class Key(FSMBaseOption):
    ...


class Required(FSMBaseOption):
    """The Value must be non-empty for the row to be recorded."""

    def save(self) -> None:
        if self.value._value is None:
            self.value.clear()
            raise SkipRecord


class List(FSMBaseOption):
    def create(self) -> None:
        self._value = []

    def clear(self) -> None:
        if 'Filldown' not in self.value.options:
            self._value = []

    def clear_all(self) -> None:
        self._value = []

    def assign(self) -> None:
        match = self.value.compiled_regex.match(self.value.value) if self.value.compiled_regex.groups > 1 else None
        if match and match.groupdict():
            self._value.append(match.groupdict())
        else:
            self._value.append(self.value.value)

    def save(self):
        self.value._value = list(self._value)


class Fillup(FSMBaseOption):
    def assign(self) -> None:
        if self.value._value is None:
            return
        index = list(self.value._parent._values.values()).index(self.value)
        for result in reversed(self.value._parent._results):
            if result[index] is not None:
                break
            result[index] = self.value._value


class Filldown(FSMBaseOption):
    def create(self) -> None:
        self._value: 'str | None' = None

    def assign(self) -> None:
        self._value = self.value.value

    def clear(self) -> None:
        self.value._value = self._value

    def clear_all(self) -> None:
        self._value = None
