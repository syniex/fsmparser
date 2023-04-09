import re
import typing
from pathlib import Path

from fsmparser.exceptions import TableError, TemplateNotFound

from ._row import FSMRow


if typing.TYPE_CHECKING:
    from fsmparser._template._template import FSMTemplate


class FSMTable:
    _comment_re = re.compile(r'^\s*#')

    def __init__(self, index_file: str, template_folder: Path) -> None:
        self._index = template_folder.joinpath(index_file)
        if not self._index.exists():
            raise TableError(f'No such index: `{index_file}` in `{template_folder.absolute()}`')
        self._template_folder = template_folder
        self._headers: list[str] = []
        self._rows: list[FSMRow] = []
        self._parse_index()

    def __len__(self) -> int:
        return len(self._rows)

    def add_template(self, **attributes: str) -> None:
        valid = {header: attributes[header] for header in self._headers if header in attributes}
        if len(self._headers) != len(valid.keys()):
            raise TableError('cannot add template missing attributes')
        self._rows.append(FSMRow(self._headers, valid.values(), Path('/')))

    def __str__(self) -> str:
        return '\n'.join([str(row) for row in self._rows])

    def _clean_row(self, row: str) -> list[str]:
        return [column.strip() for column in row.split(',')]

    def _find_template(self, command: str, **attributes: str) -> 'typing.Union[FSMTemplate, None]':
        if any(attribute not in self._headers for attribute in attributes):
            return None
        for row in self._rows:
            if row.match_row(command, **attributes):
                return row._template
        return None

    # TODO when sperating FSMTemplate to FSMTemplate and FSMTemplateAggregator fix the typing
    def parse(
        self, output: str, **attributes: str
    ) -> 'typing.List[typing.Dict[str, typing.Union[str,None, typing.List[str]]]]':
        if (command := attributes.pop('command')) is None:
            raise TableError('command must be provided to find the template')
        if (template := self._find_template(command, **attributes)) is None:
            raise TemplateNotFound(f'could not find matching template with the attribute {attributes}')
        return template.parse(output)

    def add_row(self, row: str) -> None:
        self._rows.append(FSMRow(self._headers, self._clean_row(row), self._template_folder))

    def _parse_index(self) -> None:
        index = self._index.read_text()
        rows = [row.strip() for row in index.splitlines() if self._comment_re.match(row) is None]
        for row in rows:
            row = row.strip()
            if not row:
                # ignore empty lines
                continue
            if row.startswith('template') and row.endswith('command'):
                self._headers = self._clean_row(row)
                continue
            if not self._headers:
                continue
            self.add_row(row)
