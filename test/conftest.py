from typing import Iterator

import pytest

import koduck


@pytest.fixture(scope="session")
def context() -> Iterator[koduck.KoduckContext]:
    koduck_context = koduck.KoduckContext()
    koduck_context.koduck = koduck.Koduck()
    yield koduck_context
