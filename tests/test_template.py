import typing

import pytest

from fsmparser import FSMTemplate, exceptions


if typing.TYPE_CHECKING:
    from pathlib import Path


def test_template_not_exist(template_folder: 'Path') -> None:
    with pytest.raises(exceptions.TemplateNotFound):
        _ = FSMTemplate(template_folder.joinpath('notexists.fsm'))
