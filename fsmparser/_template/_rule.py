import functools
import re
import string
import typing

from fsmparser.exceptions import TemplateError


if typing.TYPE_CHECKING:
    from fsmparser._template._template import FSMTemplate


class FSMRuleMetaclass(type):
    match_action_re = re.compile(r'(?P<match>.*)(\s->(?P<action>.*))')

    @property
    def new_state(cls) -> str:
        return r'(?P<new_state>\w+|\".*\")'

    @functools.lru_cache(maxsize=1)
    def _action_re(cls) -> 're.Pattern[str]':
        operator_re = fr'({operation.LineOperation.operations}(\.{operation.Operation.operations})?)'
        return re.compile(fr'\s+{operator_re}(\s+{cls.new_state})?$')

    @functools.lru_cache(maxsize=1)
    def _action2_re(cls) -> 're.Pattern[str]':
        print(fr'\s+{operation.Operation.operations}(\s+{cls.new_state})?$')
        return re.compile(fr'\s+{operation.Operation.operations}(\s+{cls.new_state})?$')

    @functools.lru_cache(maxsize=1)
    def _action3_re(cls) -> 're.Pattern[str]':
        return re.compile(fr'(\s+{cls.new_state})?$')

    @property
    def action_re(cls) -> 're.Pattern[str]':
        return cls._action_re()

    @property
    def action2_re(cls) -> 're.Pattern[str]':
        return cls._action2_re()

    @property
    def action3_re(cls) -> 're.Pattern[str]':
        return cls._action3_re()

    def _clear_cache(cls) -> None:
        cls._action_re.cache_clear()
        cls._action2_re.cache_clear()
        cls._action3_re.cache_clear()


class FSMRule(metaclass=FSMRuleMetaclass):
    def validate(self) -> None:
        if self._operation is not None:
            self._operation.validate()

    def match(self, line: str) -> 're.Match[str] | None':
        return self._regex.match(line)

    def __init__(self, fsm: 'FSMTemplate', line: str, line_no: int) -> None:
        self._parent = fsm
        self.line = line.strip()
        self._new_state: 'typing.Union[str,None]' = None
        self._line_no = line_no
        if len(self.line) == 1:
            raise TemplateError(f'rule cannot be empty template: `{self.location}')
        self._operation: 'operation.Operation | None' = None
        self._line_operation: 'type[operation.LineOperation]' = operation.LineNext
        self._parse()

    @property
    def location(self) -> str:
        return f'{self._parent.location}:{self._line_no}'

    def _parse(self) -> None:
        if (action_match := FSMRule.match_action_re.match(self.line)) is not None:
            self._match = action_match.group('match')
        else:
            self._match = self.line
        try:
            self._regex = re.compile(string.Template(self._match).substitute(self._parent._values_map))
        except KeyError as exc:
            raise TemplateError(f'value {exc} does not exists in template `{self.location}`') from exc
        if action_match is None:
            return
        _new_state: 'typing.Union[str,None]' = None
        action = action_match.group('action')
        if (action_re := FSMRule.action_re.match(action)) is not None:
            record_op = action_re.group('rec_op')
            if record_op is not None and record_op in operation.Operation._registry:
                self._operation = operation.Operation._registry[record_op](self._parent, self)
            line_op = action_re.group('ln_op')
            if line_op is not None and line_op in operation.LineOperation._registry:
                self._line_operation = operation.LineOperation._registry[line_op]

        elif (action_re := FSMRule.action2_re.match(action)) is not None:
            record_op = action_re.group('rec_op')
            if record_op is not None and record_op in operation.Operation._registry:
                self._operation = operation.Operation._registry[record_op](self._parent, self)
            _new_state = typing.cast(typing.Union[str, None], action_re.group('new_state'))
            if isinstance(self._operation, operation.OperationError):
                self._operation.error = _new_state
                _new_state = None

        elif (action_re := FSMRule.action3_re.match(action)) is not None:
            _new_state = typing.cast(typing.Union[str, None], action_re.group('new_state'))
        if _new_state is not None:
            self._new_state = _new_state

    def run_operation(self) -> None:
        if self._operation is not None:
            self._operation.execute()
        if self._new_state is not None:
            self._parent._current_state = self._parent._states[self._new_state]

    def break_current_state(self) -> bool:
        return self._line_operation.break_current_state

    def __str__(self) -> str:
        return f"""
        {self.line}"""


from fsmparser._template import _operations as operation  # pylint: disable=C0413
