from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any, TypeAlias


class PolicyBag(Mapping[str, Any]):
    """Optional run-wide overrides; stages pick keys they care about."""

    def __init__(self, data: dict[str, Any] | None = None):
        self._d = dict(data or {})

    def __getitem__(self, k: str) -> Any:
        return self._d[k]

    def __iter__(self) -> Iterator[str]:
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def get(self, k: str, default: Any = None) -> Any:
        return self._d.get(k, default)


PolicyLike: TypeAlias = Mapping[str, Any] | PolicyBag


def as_policy(policy: PolicyLike | None) -> PolicyBag | None:
    if policy is None:
        return None
    if isinstance(policy, PolicyBag):
        return policy
    return PolicyBag(dict(policy))
