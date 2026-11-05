from dataclasses import dataclass

@dataclass
class DateOfBirth:
    day: str
    month: str
    year: str


@dataclass
class Address:
    first_name: str
    last_name: str
    company: str
    address: str
    address_2: str
    country: str
    state: str
    city: str
    zipcode: str
    mobile_number: str


@dataclass
class AccountInformation:
    title: str
    password: str
    date_of_birth: DateOfBirth
    address: Address
    subscribe_newsletter: bool = False
    receive_special_offers: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "AccountInformation":
        dob = data["date_of_birth"]
        addr = data["address"]
        return cls(
            title=data["title"],
            password=data["password"],
            date_of_birth=DateOfBirth(day=dob["day"], month=dob["month"], year=dob["year"]),
            address=Address(
                first_name=addr["first_name"],
                last_name=addr["last_name"],
                company=addr["company"],
                address=addr["address"],
                address_2=addr["address_2"],
                country=addr["country"],
                state=addr["state"],
                city=addr["city"],
                zipcode=addr["zipcode"],
                mobile_number=addr["mobile_number"],
            ),
            subscribe_newsletter=data.get("subscribe_newsletter", False),
            receive_special_offers=data.get("receive_special_offers", False),
        )