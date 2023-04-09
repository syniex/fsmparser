import re
import typing

from fsmparser._template._template import FSMTemplate

from ._exceptions import TableError


if typing.TYPE_CHECKING:
    from pathlib import Path


class FSMRow:
    _double_square_bracket_re = re.compile(r'(\[\[.+?\]\])')

    def __init__(
        self, columns: 'list[str]', values: 'typing.Union[list[str] , typing.ValuesView[str]]', template_folder: 'Path'
    ) -> None:
        if len(columns) != len(values):
            raise TableError(f'number of columns({len(columns)})/values({len(values)}) mismatch {columns=} {values=}')
        _attributes = dict(zip(columns, values))
        if (_template := _attributes.pop('template')) is None:
            raise TableError('template must be')
        template = template_folder.joinpath(str(_template))
        self._template = FSMTemplate(template)
        self._attributes: 'dict[str, re.Pattern[str]]' = {}
        for column, value in _attributes.items():
            self._attributes[column] = re.compile(
                re.sub(self._double_square_bracket_re, self._create_optional_re, value)
            )
        self._command = self._attributes.pop('command')

    def __str__(self) -> str:
        return ' '.join([f'{column}:{value}' for column, value in self._attributes.items()])

    def _create_optional_re(self, match: 're.Match[str]') -> str:
        # removes leading `[[` and ending `]]`
        word = match.group()[2:-2]
        return '(' + ('(').join(word) + ')?' * len(word)

    def match_row(self, command: str, **attributes: str) -> bool:
        if self._command.match(command) is None:
            return False
        for attribute, attribute_re in self._attributes.items():
            if attribute not in attributes or attribute_re.match(attributes[attribute]) is None:
                return False
        return True
