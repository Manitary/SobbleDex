from typing import Iterator

import pytest

from koduck import Koduck, KoduckContext

pytest.register_assert_rewrite("helper")


@pytest.fixture(name="koduck_instance", scope="session")
def _koduck_instance() -> Iterator[Koduck]:
    _koduck = Koduck()
    yield _koduck


@pytest.fixture(scope="session")
def context(koduck_instance: Koduck) -> Iterator[KoduckContext]:
    koduck_context = KoduckContext()
    koduck_context.koduck = koduck_instance
    yield koduck_context


@pytest.fixture(scope="session")
def context_with_emoji(koduck_instance: Koduck) -> Iterator[KoduckContext]:
    koduck_context = KoduckContext()
    koduck_context.koduck = koduck_instance
    koduck_context.param_line = "[szard]"
    yield koduck_context
