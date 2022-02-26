from __future__ import annotations

import re
from typing import List

UK_STREET_ABBR = [
    "Ave",
    "Blvd",
    "Bdwy",
    "Cir",
    "Cl",
    "Ct",
    "Cr",
    "Dr",
    "Gdn",
    "Gdns",
    "Gn",
    "Gr",
    "J",
    "Ln",
    "Mt",
    "Pl",
    "Pk",
    "Rdg",
    "Rd",
    "St.",
    "Sq",
    "Square",
    "St",
    "Ter",
    "Val",
    "Way",
]


class Address:
    def __init__(
        self,
        address_lines: List[str],
        house_no: str,
        street: str,
        district: str,
        postal_code: str,
        city: str,
        state: str,
        country_code: str,
    ):
        self.address_lines = address_lines
        self.house_no = house_no
        self.street = street
        self.district = district
        self.postal_code = postal_code
        self.city = city
        self.state = state
        self.country_code = country_code

    @classmethod
    def deserialise(cls, serialised: dict):
        return cls(**serialised)

    @classmethod
    def get_address_for_country(cls, serialised: dict) -> Address:
        return COUNTRY_ADDRESSES[serialised["country_code"]].deserialise(serialised)

    @staticmethod
    def parse_postal_code(city_and_postal_code):
        postal_code, city = ["", ""]
        postal_codes = re.findall(r"[0-9][0-9][0-9][0-9]", city_and_postal_code)
        if postal_codes:
            postal_code = postal_codes[0] if postal_codes else ""
            city = re.sub(f"{postal_code} ", "", city_and_postal_code)
        else:
            city = city_and_postal_code
        return city, postal_code

    @staticmethod
    def parse_other_parts(other_parts):
        if not other_parts:
            return "", "", ""

        address_lines, street, house_no = [[], "", ""]
        street = other_parts[-1]
        address_lines = other_parts[:-1]

        if street and str.isdigit(street.split(" ")[-1]):
            house_no = street.split(" ")[-1]
            street = " ".join(street.split(" ")[:-1])

        return address_lines, house_no, street


class UKAddress(Address):
    def __init__(
        self,
        address_lines: List[str] = list,
        house_no: str = "",
        street: str = "",
        district: str = "",
        postal_code: str = "",
        city: str = "",
    ):
        super().__init__(
            address_lines, house_no, street, district, postal_code, city, "", "UK"
        )

    def __str__(self) -> str:
        address = ", ".join(line for line in self.address_lines if line)
        street = " ".join(part for part in [self.house_no, self.street] if part)
        city = " ".join(part for part in [self.city, self.postal_code] if part)
        address_string = [address, street, self.district, city, self.country_code]
        return ", ".join(part for part in address_string if part)

    @classmethod
    def deserialise(cls, serialised: dict) -> UKAddress:
        serialised.pop("state")
        serialised.pop("country_code")
        return cls(**serialised)

    @classmethod
    def parse_from_string(cls, address_string) -> UKAddress:
        address_split = address_string.split(", ")
        address_lines, house_no, street, district = UKAddress.parse_other_parts_uk(
            address_split[:-2]
        )
        city, postal_code = UKAddress.parse_postal_code_uk(address_split[-2])
        return cls(
            address_lines=address_lines,
            house_no=house_no,
            street=street,
            district=district,
            postal_code=postal_code,
            city=city,
        )

    @staticmethod
    def parse_postal_code_uk(city_and_postal_code):
        postal_code, city = ["", ""]
        postal_codes = re.findall(
            r"[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}", city_and_postal_code
        )
        if not postal_codes:
            postal_codes = re.findall(r"[A-Z]{1,2}[0-9][0-9A-Z]?", city_and_postal_code)
        if postal_codes:
            postal_code = postal_codes[0] if postal_codes else ""
            city = re.sub(f" {postal_code}", "", city_and_postal_code)
        else:
            city = city_and_postal_code
        return city, postal_code

    @staticmethod
    def parse_other_parts_uk(other_parts):
        address_lines, street, house_no, district = [[], "", "", [""]]
        for index, part in enumerate(other_parts):
            if any(
                [part.endswith(" " + street_abbr) for street_abbr in UK_STREET_ABBR]
            ):
                street = part
                address_lines = other_parts[:index]
                if len(other_parts) > index + 1:
                    district = other_parts[index + 1:]
                break

        if other_parts and not street:
            district[0] = other_parts[-1]
            address_lines = other_parts[:-1]

        if street and str.isdigit(street[0]):
            house_no = street.split(" ")[0]
            street = " ".join(street.split(" ")[1:])

        if not house_no and address_lines:
            house_no_index = -1
            for index, address_line in enumerate(address_lines):
                if str.isdigit(address_line[0]) and len(address_line.split(" ")) == 1:
                    house_no_index = index
            if house_no_index > 0:
                house_no = address_lines.pop(house_no_index)

        if len(district) > 1:
            raise Exception(f"Can only add one district: {district}")
        return address_lines, house_no, street, district[0]


class BEAddress(Address):
    def __init__(
        self,
        address_lines: List[str],
        house_no: str,
        street: str,
        postal_code: str,
        city: str,
    ):
        Address.__init__(
            self, address_lines, house_no, street, "", postal_code, city, "", "BE"
        )

    def stringify(self) -> str:
        address = ", ".join(line for line in self.address_lines if line)
        street = " ".join(part for part in [self.street, self.house_no] if part)
        city = " ".join(part for part in [self.postal_code, self.city] if part)
        address_string = [address, street, city, "Belgium"]
        return ", ".join(part for part in address_string if part)

    @classmethod
    def deserialise(cls, serialised: dict) -> BEAddress:
        serialised.pop("district")
        serialised.pop("state")
        serialised.pop("country_code")
        return cls(**serialised)

    @staticmethod
    def parse_from_string(address_string) -> BEAddress:
        address_split = address_string.split(", ")
        address_lines, house_no, street = BEAddress.parse_other_parts(
            address_split[:-2]
        )
        city, postal_code = BEAddress.parse_postal_code(address_split[-2])
        return BEAddress(
            address_lines=address_lines,
            house_no=house_no,
            street=street,
            postal_code=postal_code,
            city=city,
        )


class ATAddress(Address):
    def __init__(
        self,
        address_lines: List[str],
        house_no: str,
        street: str,
        postal_code: str,
        city: str,
    ):
        Address.__init__(
            self, address_lines, house_no, street, "", postal_code, city, "", "AT"
        )

    def stringify(self) -> str:
        address = ", ".join(line for line in self.address_lines if line)
        street = " ".join(part for part in [self.street, self.house_no] if part)
        city = " ".join(part for part in [self.postal_code, self.city] if part)
        address_string = [address, street, city, "Austria"]
        return ", ".join(part for part in address_string if part)

    @classmethod
    def deserialise(cls, serialised: dict) -> ATAddress:
        serialised.pop("district")
        serialised.pop("state")
        serialised.pop("country_code")
        return cls(**serialised)

    @staticmethod
    def parse_from_string(address_string) -> ATAddress:
        address_split = address_string.split(", ")
        address_lines, house_no, street = ATAddress.parse_other_parts(
            address_split[:-2]
        )
        city, postal_code = ATAddress.parse_postal_code(address_split[-2])
        return ATAddress(
            address_lines=address_lines,
            house_no=house_no,
            street=street,
            postal_code=postal_code,
            city=city,
        )


class CHAddress(Address):
    def __init__(
        self,
        address_lines: List[str],
        house_no: str,
        street: str,
        postal_code: str,
        city: str,
    ):
        Address.__init__(
            self, address_lines, house_no, street, "", postal_code, city, "", "CH"
        )

    def stringify(self) -> str:
        address = ", ".join(line for line in self.address_lines if line)
        street = " ".join(part for part in [self.street, self.house_no] if part)
        city = " ".join(part for part in [self.postal_code, self.city] if part)
        address_string = [address, street, city, "Switzerland"]
        return ", ".join(part for part in address_string if part)

    @classmethod
    def deserialise(cls, serialised: dict) -> CHAddress:
        serialised.pop("district")
        serialised.pop("state")
        serialised.pop("country_code")
        return cls(**serialised)

    @staticmethod
    def parse_from_string(address_string) -> CHAddress:
        address_split = address_string.split(", ")
        address_lines, house_no, street = CHAddress.parse_other_parts(
            address_split[:-2]
        )
        city, postal_code = CHAddress.parse_postal_code(address_split[-2])
        return CHAddress(
            address_lines=address_lines,
            house_no=house_no,
            street=street,
            postal_code=postal_code,
            city=city,
        )


class FRAddress(Address):
    def __init__(
        self,
        address_lines: List[str],
        house_no: str,
        street: str,
        postal_code: str,
        city: str,
    ):
        Address.__init__(
            self, address_lines, house_no, street, "", postal_code, city, "", "FR"
        )

    def stringify(self) -> str:
        address = ", ".join(line for line in self.address_lines if line)
        street = " ".join(part for part in [self.street, self.house_no] if part)
        city = " ".join(part for part in [self.postal_code, self.city] if part)
        address_string = [address, street, city, "France"]
        return ", ".join(part for part in address_string if part)

    @classmethod
    def deserialise(cls, serialised: dict) -> FRAddress:
        serialised.pop("district")
        serialised.pop("state")
        serialised.pop("country_code")
        return cls(**serialised)

    @staticmethod
    def parse_from_string(address_string) -> FRAddress:
        address_split = address_string.split(", ")
        address_lines, house_no, street = FRAddress.parse_other_parts(
            address_split[:-2]
        )
        city, postal_code = FRAddress.parse_postal_code(address_split[-2])
        return FRAddress(
            address_lines=address_lines,
            house_no=house_no,
            street=street,
            postal_code=postal_code,
            city=city,
        )


class DEAddress(Address):
    def __init__(
        self,
        address_lines: List[str],
        house_no: str,
        street: str,
        postal_code: str,
        city: str,
    ):
        Address.__init__(
            self, address_lines, house_no, street, "", postal_code, city, "", "DE"
        )

    def stringify(self) -> str:
        address = ", ".join(line for line in self.address_lines if line)
        street = " ".join(part for part in [self.street, self.house_no] if part)
        city = " ".join(part for part in [self.postal_code, self.city] if part)
        address_string = [address, street, city, "Germany"]
        return ", ".join(part for part in address_string if part)

    @classmethod
    def deserialise(cls, serialised: dict) -> DEAddress:
        serialised.pop("district")
        serialised.pop("state")
        serialised.pop("country_code")
        return cls(**serialised)

    @staticmethod
    def parse_from_string(address_string) -> DEAddress:
        address_split = address_string.split(", ")
        address_lines, house_no, street = DEAddress.parse_other_parts(
            address_split[:-2]
        )
        city, postal_code = DEAddress.parse_postal_code(address_split[-2])
        return DEAddress(
            address_lines=address_lines,
            house_no=house_no,
            street=street,
            postal_code=postal_code,
            city=city,
        )


class NOAddress(Address):
    def __init__(
        self,
        address_lines: List[str],
        house_no: str,
        street: str,
        postal_code: str,
        city: str,
    ):
        Address.__init__(
            self, address_lines, house_no, street, "", postal_code, city, "", "NO"
        )

    def stringify(self) -> str:
        address = ", ".join(line for line in self.address_lines if line)
        street = " ".join(part for part in [self.street, self.house_no] if part)
        city = " ".join(part for part in [self.postal_code, self.city] if part)
        address_string = [address, street, city, "Norway"]
        return ", ".join(part for part in address_string if part)

    @classmethod
    def deserialise(cls, serialised: dict) -> NOAddress:
        serialised.pop("district")
        serialised.pop("state")
        serialised.pop("country_code")
        return cls(**serialised)

    @staticmethod
    def parse_from_string(address_string) -> NOAddress:
        address_split = address_string.split(", ")
        address_lines, house_no, street = BEAddress.parse_other_parts(
            address_split[:-2]
        )
        city, postal_code = BEAddress.parse_postal_code(address_split[-2])
        return NOAddress(
            address_lines=address_lines,
            house_no=house_no,
            street=street,
            postal_code=postal_code,
            city=city,
        )


class SEAddress(Address):
    def __init__(
        self,
        address_lines: List[str],
        house_no: str,
        street: str,
        postal_code: str,
        city: str,
    ):
        Address.__init__(
            self, address_lines, house_no, street, "", postal_code, city, "", "SE"
        )

    def stringify(self) -> str:
        address = ", ".join(line for line in self.address_lines if line)
        street = " ".join(part for part in [self.street, self.house_no] if part)
        city = " ".join(part for part in [self.postal_code, self.city] if part)
        address_string = [address, street, city, "Sweden"]
        return ", ".join(part for part in address_string if part)

    @classmethod
    def deserialise(cls, serialised: dict) -> SEAddress:
        serialised.pop("district")
        serialised.pop("state")
        serialised.pop("country_code")
        return cls(**serialised)

    @staticmethod
    def parse_from_string(address_string) -> SEAddress:
        address_split = address_string.split(", ")
        address_lines, house_no, street = BEAddress.parse_other_parts(
            address_split[:-2]
        )
        city, postal_code = BEAddress.parse_postal_code(address_split[-2])
        return SEAddress(
            address_lines=address_lines,
            house_no=house_no,
            street=street,
            postal_code=postal_code,
            city=city,
        )


COUNTRY_ADDRESSES = {
    "UK": UKAddress,
    "GB": UKAddress,
    "BE": BEAddress,
    "AT": ATAddress,
    "CH": CHAddress,
    "FR": FRAddress,
    "DE": DEAddress,
    "NO": NOAddress,
    "SE": SEAddress,
}
