from pathlib import Path

import pytest


@pytest.fixture(scope='package')
def template_folder() -> 'Path':
    return Path(__file__).parent.joinpath('templates')
