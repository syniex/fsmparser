import re
import typing

from ._exceptions import ParseError
from ._options import FSMBaseOption


if typing.TYPE_CHECKING:
    from ._template import FSMTemplate


class FSMValue:
    def __init__(self, parent: 'FSMTemplate', line: str, line_no: int) -> None:
        self._parent = parent
        self._line = line
        self._line_no = line_no
        self._value: 'str | None' = None
        self._options: 'list[FSMBaseOption]' = []
        self._parse()

    def validate(self) -> None:
        for option in self._options:
            option.validate()

    def __str__(self) -> str:
        return f"""{self.name}<{self._regex}>
        """

    @property
    def location(self) -> str:
        return f'{self._parent.location}:{self._line_no}'

    def _parse(self) -> None:
        value_params = self._line.split(' ')
        options: list[str] = []
        if len(value_params) < 3:
            raise ParseError(f'line does not have at least 3 tokens `{self.location}`')
        if not value_params[2].startswith('('):
            options = value_params[1].split(',')
            self.name = value_params[2]
            self._regex = ' '.join(value_params[3:])
        else:
            self.name = value_params[1]
            self._regex = ' '.join(value_params[2:])
        for option in options:
            self._add_option(option)
        [option.create() for option in self._options]  # type: ignore[func-returns-value]
        try:
            self.compiled_regex = re.compile(self._regex)
        except Exception as exc:
            raise ParseError from exc
        self.template = re.sub(r'^\(', rf'(?P<{self.name}>', self._regex)

    def _add_option(self, option: str) -> None:
        if (match := FSMBaseOption.option_re.match(option)) is None:
            raise ParseError(f'Invalid option: {repr(option)}')
        option_name = match.group('name')
        if option_name in [option.name for option in self._options]:
            raise ParseError(f'Duplicate option: {repr(option)}')
        self._options.append(FSMBaseOption.registry[option_name](self, match.group('param')))

    @property
    def value(self) -> 'str | None':
        return self._value

    @value.setter
    def value(self, value: 'str | None') -> None:
        self._value = value
        [option.assign() for option in self._options]  # type: ignore[func-returns-value]

    def save(self) -> None:
        [option.save() for option in self._options]  # type: ignore[func-returns-value]

    def clear(self) -> None:
        self._value = None
        [option.clear() for option in self._options]  # type: ignore[func-returns-value]

    def clear_all(self) -> None:
        [option.clear_all() for option in self._options]  # type: ignore[func-returns-value]
