import typing

from ._exceptions import TemplateNotFound


if typing.TYPE_CHECKING:
    from pathlib import Path


class FSMTemplate:
    def __init__(
        self,
        template: 'Path',
        /,
    ) -> None:
        if not template.exists() or not template.is_file():
            raise TemplateNotFound(f'No such template: `{template.name}` in `{template.parent.absolute()}`')
        self._template = template
        self._parse_template()
        self.validate()

    def _parse_template(self) -> None:
        ...

    def validate(self) -> None:
        ...

    def parse(self, _input: str, /) -> typing.List[typing.Dict[str, str]]:
        return []
