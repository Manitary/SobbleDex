from dataclasses import dataclass


@dataclass
class MockAuthor:
    id: int


@dataclass
class MockMessage:
    author: MockAuthor
