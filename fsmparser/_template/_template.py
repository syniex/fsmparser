import io
import re
import typing
from pathlib import Path

from ._exceptions import TemplateError, TemplateNotFound
from ._state import FSMState
from ._value import FSMValue


if typing.TYPE_CHECKING:
    ...


class FSMTemplate:
    _comment_re = re.compile(r'^\s*#')

    def __init__(self, template: 'typing.Union[Path,bytes,str]', /) -> None:
        self._content = self._load_content(template)
        self._template = template
        self._values: 'typing.Dict[str, FSMValue]' = {}
        self._states: 'typing.Dict[str, FSMState]' = {}
        self._results: 'typing.List[typing.List[typing.Union[str, None]]]' = []
        self._parse_template()
        self.validate()

    @classmethod
    def _load_content(cls, template: 'typing.Union[Path,bytes,str]') -> 'io.StringIO':
        if isinstance(template, str):
            return io.StringIO(template)
        if isinstance(template, bytes):
            return io.StringIO(template.decode())
        if isinstance(template, Path) and template.is_file():
            return io.StringIO(template.read_text())
        raise TemplateNotFound(f'No such template: `{template.name}` in `{template.parent.absolute()}`')

    @property
    def location(self) -> str:
        if isinstance(self._template, Path):
            return str(self._template.absolute())
        return ''

    @property
    def _values_map(self) -> 'dict[str, str]':
        return {value.name: value.template for value in self._values.values()}

    def reset(self) -> None:
        self._current_state: 'FSMState' = self._states['Start']  # pylint: disable=W0201
        self._results.clear()

    def _parse_template(self) -> None:
        self._parse_variables()
        self._parse_states()

    def _parse_variables(self) -> None:
        for index, line in enumerate(self._content, start=1):
            line = line.rstrip()
            if self._comment_re.match(line):
                continue
            if not line.startswith('Value '):
                continue
            value = FSMValue(self, line, index)
            if value.name in self._values:
                raise TemplateError(
                    f'Duplicate value name in `{self._values[value.name].location}` and `{value.location}`'
                )
            self._values[value.name] = value
        # Reset the TextIOWrapper to first line
        self._content.seek(0)

    def _parse_states(self) -> None:
        state: 'None | FSMState' = None
        for index, line in enumerate(self._content, start=1):
            line = line.rstrip()
            if not line or self._comment_re.match(line):
                continue
            if FSMState.name_re.match(line):
                state = FSMState(self, line, index)
                if state.name in self._states:
                    raise TemplateError(f'Duplicate state `{self._states[state.name].location}` and `{state.location}`')
                self._states[state.name] = state
                continue
            if state is None:
                continue
            if line.startswith((' ^', '  ^', '\t^')):
                state.add_rule(line, index)
        # Reset the TextIOWrapper to first line
        self._content.seek(0)

    def validate(self) -> None:
        if 'Start' not in self._states:
            raise TemplateError(f'`Start` state doe not exists in template: `{self.location}`')
        for value in self._values.values():
            value.validate()
        for state in self._states.values():
            state.validate()

    @property
    def results(self) -> 'typing.List[typing.Dict[str, str | typing.List[str] | None]]':
        results: 'typing.List[typing.Dict[str, str | typing.List[str] | None]]' = []
        for result in self._results:
            results.append({value.name: value_data for value, value_data in zip(self._values.values(), result)})
        return results

    def _check_line(self, line: str) -> None:
        for rule in self._current_state.rules:
            if (matched := rule.match(line)) is None:
                continue
            for name, value in matched.groupdict().items():
                if (fsm_value := self._values.get(name)) is not None:
                    fsm_value.value = value
            rule.run_operation()
            if rule.break_current_state():
                break

    def parse(self, _input: str, /) -> 'typing.List[typing.Dict[str, str | typing.List[str] | None]]':
        self.reset()
        for line in _input.splitlines():
            self._check_line(line)
        return self.results

    def clear_record(self) -> None:
        [value.clear() for value in self._values.values()]  # type: ignore[func-returns-value]

    def save_record(self) -> None:
        [value.save() for value in self._values.values()]  # type: ignore[func-returns-value]

    def current_values(self) -> 'list[str | None]':
        return [value.value for value in self._values.values()]
