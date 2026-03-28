import pytest

from src.enums import TransportMode


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("train", TransportMode.TRAIN),
        ("walking", TransportMode.WALKING),
        ("bus", TransportMode.BUS),
        ("underground", TransportMode.UNDERGROUND),
        ("driving", TransportMode.DRIVING),
    ],
)
def test_from_str(string: str, expected: TransportMode) -> None:
    assert TransportMode.from_str(string) is expected


def test_from_str_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown TransportMode"):
        TransportMode.from_str("hovercraft")


def test_name_lower_roundtrips_from_str() -> None:
    for member in TransportMode:
        assert TransportMode.from_str(member.name.lower()) is member


def test_all_members_unique() -> None:
    values = [m.value for m in TransportMode]
    assert len(values) == len(set(values))
