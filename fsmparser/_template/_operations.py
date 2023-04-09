import typing

from fsmparser._template._options import SkipRecord
from fsmparser._template._rule import FSMRule
from fsmparser.exceptions import FSMError


if typing.TYPE_CHECKING:
    from fsmparser._template._template import FSMTemplate


class Operation:
    _line_operation_registry: 'typing.Dict[str, typing.Type[Operation]]' = {}
    _registry: 'typing.Dict[str, typing.Type[Operation]]' = {}
    operations: str
    line_operations: str

    def __init__(self, template: 'FSMTemplate', rule: 'FSMRule') -> None:
        self._template = template
        self._rule = rule

    def validate(self) -> None:
        ...

    def execute(self) -> None:
        ...

    def __init_subclass__(cls: 'typing.Type[Operation]') -> None:
        Operation._registry[cls.__name__.lstrip('Operation')] = cls
        Operation.operations = f'(?P<rec_op>{"|".join(cls._registry.keys())})'
        Operation.line_operations = f'(?P<ln_op>{"|".join(cls._line_operation_registry.keys())})'
        FSMRule._clear_cache()


class OperationRecord(Operation):
    def execute(self) -> None:
        if not self._template._values:
            return
        try:
            self._template.save_record()
        except SkipRecord:
            self._template.clear_record()
            return

        current_record = self._template.current_values()
        if len(current_record) == current_record.count(None):
            return
        self._template._results.append(current_record)
        [value.clear() for value in self._template._values.values()]  # type: ignore[func-returns-value]


class OperationNoRecord(Operation):
    ...


class OperationError(Operation):
    def __init__(self, template: 'FSMTemplate', rule: 'FSMRule') -> None:
        super().__init__(template, rule)
        self.error: 'typing.Union[str,None]' = None

    def execute(self) -> None:
        if self.error is not None:
            raise FSMError(f'Error: {self.error}. Rule Line: {self._rule.line}.')
        raise FSMError(f'State Error raised. Rule Line: {self._rule.line}.')


class LineOperation:
    break_current_state: bool = False
    _registry: 'typing.Dict[str, typing.Type[LineOperation]]' = {}
    operations: str

    def __init_subclass__(cls: 'typing.Type[LineOperation]') -> None:
        LineOperation._registry[cls.__name__.lstrip('Line')] = cls
        LineOperation.operations = f'(?P<ln_op>{"|".join(cls._registry.keys())})'
        FSMRule._clear_cache()


class LineContinue(LineOperation):
    break_current_state = False


class LineNext(LineOperation):
    break_current_state = True
