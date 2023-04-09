import re
import typing

from fsmparser._template._rule import FSMRule


if typing.TYPE_CHECKING:
    from fsmparser._template._template import FSMTemplate


class FSMState:
    name_re = re.compile(r'^(\w+)$')

    def __init__(self, fsm: 'FSMTemplate', name: str, line_no: int) -> None:
        self._parent = fsm
        self.name = name
        self._line_no = line_no
        self.rules: 'typing.List[FSMRule]' = []

    @property
    def location(self) -> str:
        return f'{self._parent.location}:{self._line_no}'

    def validate(self) -> None:
        for rule in self.rules:
            rule.validate()

    def __str__(self) -> str:
        output: list[str] = [self.name]
        for rule in self.rules:
            output.append(str(rule))
        return ''.join(output)

    def add_rule(self, line: str, index: int) -> None:
        rule = FSMRule(self._parent, line, index)
        self.rules.append(rule)
