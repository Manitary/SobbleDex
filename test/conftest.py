import os
import sys
from typing import Iterator

import pytest

import koduck

sys.path.append(os.path.join(os.path.dirname(__file__), "helper"))


@pytest.fixture(scope="session")
def context() -> Iterator[koduck.KoduckContext]:
    koduck_context = koduck.KoduckContext()
    koduck_context.koduck = koduck.Koduck()
    yield koduck_context
