import re

import fastapi_inspector


def test_version_is_exposed() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", fastapi_inspector.__version__)
    assert "__version__" in fastapi_inspector.__all__
