import pytest

from src.enums.transport_mode import TransportMode


@pytest.mark.parametrize(
    ("member", "value"),
    [
        (TransportMode.TRAIN, "train"),
        (TransportMode.WALKING, "walking"),
        (TransportMode.BUS, "bus"),
        (TransportMode.UNDERGROUND, "underground"),
        (TransportMode.DRIVING, "driving"),
    ],
)
def test_transport_mode_values(member: TransportMode, value: str) -> None:
    assert member.value == value
    assert isinstance(member, str)


def test_all_modes_unique() -> None:
    values = [m.value for m in TransportMode]
    assert len(values) == len(set(values))
