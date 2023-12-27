from dataclasses import dataclass, field
from typing import Any


@dataclass
class MockAuthor:
    id: int = 1
    name: str = "Mock_Author"
    discriminator: int = 123
    bot: bool = False


@dataclass
class MockGuild:
    id: int = 7
    name: str = "Mock_Guild"


@dataclass
class MockChannel:
    id: int = 3

    async def send(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        print("Message to send:", args, kwargs)
        return kwargs


@dataclass
class MockMessage:
    content: str = ""
    author: MockAuthor = field(default_factory=MockAuthor)
    guild: MockGuild = field(default_factory=MockGuild)
    channel: MockChannel = field(default_factory=MockChannel)
