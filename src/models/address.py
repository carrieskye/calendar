import re
from typing import List

UK_STREET_ABBR = ['Ave', 'Blvd', 'Bdwy', 'Cir', 'Cl', 'Ct', 'Cr', 'Dr', 'Gdn', 'Gdns', 'Gn', 'Gr', 'J', 'Ln', 'Mt',
                  'Pl', 'Pk', 'Rdg', 'Rd', 'St.', 'Sq', 'Square', 'St', 'Ter', 'Val', 'Way']


class Address:

    def __init__(self, address_lines: List[str], house_no: str, street: str, district: str, postal_code: str, city: str,
                 state: str, country_code: str):
        self.address_lines = address_lines
        self.house_no = house_no
        self.street = street
        self.district = district
        self.postal_code = postal_code
        self.city = city
        self.state = state
        self.country_code = country_code

    def serialise(self):
        return self.__dict__

    @staticmethod
    def deserialise(serialised: dict):
        return Address(**serialised)


class UKAddress(Address):

    def __init__(self, address_lines: List[str], house_no: str, street: str, district: str, postal_code: str,
                 city: str):
        Address.__init__(self, address_lines, house_no, street, district, postal_code, city, '', 'UK')

    def stringify(self):
        address = ', '.join(line for line in self.address_lines if line)
        street = ' '.join(part for part in [self.house_no, self.street] if part)
        city = ' '.join(part for part in [self.city, self.postal_code] if part)
        address_string = [address, street, self.district, city, self.country_code]
        return ', '.join(part for part in address_string if part)

    def serialise(self):
        return self.__dict__

    @staticmethod
    def deserialise(serialised: dict):
        return UKAddress(**serialised)

    @staticmethod
    def parse_from_string(address_string):
        address_split = address_string.split(', ')
        address_lines, house_no, street, district = UKAddress.parse_other_parts(address_split[:-2])
        city, postal_code = UKAddress.parse_postal_code(address_split[-2])
        return UKAddress(
            address_lines=address_lines,
            house_no=house_no,
            street=street,
            district=district,
            postal_code=postal_code,
            city=city
        )

    @staticmethod
    def parse_postal_code(city_and_postal_code):
        postal_code, city = ['', '']
        postal_codes = re.findall(r'[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}', city_and_postal_code)
        if not postal_codes:
            postal_codes = re.findall(r'[A-Z]{1,2}[0-9][0-9A-Z]?', city_and_postal_code)
        if postal_codes:
            postal_code = postal_codes[0] if postal_codes else ''
            city = re.sub(f' {postal_code}', '', city_and_postal_code)
        else:
            city = city_and_postal_code
        return city, postal_code

    @staticmethod
    def parse_other_parts(other_parts):
        address_lines, street, house_no, district = [[], '', '', ['']]
        for index, part in enumerate(other_parts):
            if any([part.endswith(' ' + street_abbr) for street_abbr in UK_STREET_ABBR]):
                street = part
                address_lines = other_parts[:index]
                if len(other_parts) > index + 1:
                    district = other_parts[index + 1:]
                break

        if not street:
            district[0] = other_parts[-1]
            address_lines = other_parts[:-1]

        if street and str.isdigit(street[0]):
            house_no = street.split(' ')[0]
            street = ' '.join(street.split(' ')[1:])

        if not house_no and address_lines:
            house_no_index = -1
            for index, address_line in enumerate(address_lines):
                if str.isdigit(address_line[0]) and len(address_line.split(' ')) == 1:
                    house_no_index = index
            if house_no_index > 0:
                house_no = address_lines.pop(house_no_index)

        if len(district) > 1:
            raise Exception(f'Can only add one district: {district}')
        return address_lines, house_no, street, district[0]
