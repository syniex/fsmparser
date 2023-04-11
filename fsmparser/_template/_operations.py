import typing

from fsmparser._template._options import SkipRecord
from fsmparser._template._rule import FSMRule


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

    @staticmethod
    def execute(template: 'FSMTemplate') -> None:
        ...

    def __init_subclass__(cls: 'typing.Type[Operation]') -> None:
        Operation._registry[cls.__name__.lstrip('Operation')] = cls
        Operation.operations = f'(?P<rec_op>{"|".join(cls._registry.keys())})'
        Operation.line_operations = f'(?P<ln_op>{"|".join(cls._line_operation_registry.keys())})'
        FSMRule._clear_cache()


class OperationRecord(Operation):
    @staticmethod
    def execute(template: 'FSMTemplate') -> None:
        if not template._values:
            return
        try:
            template.save_record()
        except SkipRecord:
            template.clear_record()
            return

        current_record = template.current_values()
        if len(current_record) == current_record.count(None):
            return
        template._results.append(current_record)
        [value.clear() for value in template._values.values()]  # type: ignore[func-returns-value]


class OperationNoRecord(Operation):
    ...


class OperationError(Operation):
    ...


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
