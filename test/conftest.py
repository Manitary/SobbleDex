from typing import Iterator

import pytest

import koduck

pytest.register_assert_rewrite("helper")


@pytest.fixture(scope="session")
def context() -> Iterator[koduck.KoduckContext]:
    koduck_context = koduck.KoduckContext()
    koduck_context.koduck = koduck.Koduck()
    yield koduck_context
