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
