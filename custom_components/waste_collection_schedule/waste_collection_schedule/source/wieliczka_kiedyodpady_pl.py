from datetime import date, datetime, timedelta

import requests
from waste_collection_schedule import Collection  # type: ignore[attr-defined]
from waste_collection_schedule.exceptions import SourceArgumentNotFoundWithSuggestions

TITLE = "Wieliczka Kiedy Odpady"
DESCRIPTION = "Source for Wieliczka Kiedy Odpady schedules."
URL = "https://wieliczka.kiedyodpady.pl"
COUNTRY = "pl"

TEST_CASES = {
    "Wieliczka, Asnyka, pozostale": {
        "locality_id": "0952232",
        "street_id": "15775",
        "number": "pozostałe",
    }
}

API_URL = "https://api.kiedyodpady.pl/public"
ORIGIN = "https://wieliczka.kiedyodpady.pl"
DEFAULT_DAYS = 35

ICON_MAP = {
    "bio": "mdi:leaf",
    "papier": "mdi:package-variant",
    "metale": "mdi:recycle",
    "tworzywa": "mdi:recycle",
    "szkło": "mdi:bottle-soda",
    "zmieszane": "mdi:trash-can",
    "gabaryt": "mdi:sofa",
    "choinka": "mdi:pine-tree",
    "odpady zielone": "mdi:leaf",
}

PARAM_TRANSLATIONS = {
    "en": {
        "locality": "Locality Name",
        "locality_id": "Locality ID",
        "street": "Street Name",
        "street_id": "Street ID",
        "number": "House Number",
        "property_type": "Property Type",
        "building_type": "Building Type",
        "days": "Days To Fetch",
    }
}

PARAM_DESCRIPTIONS = {
    "en": {
        "locality": "Locality name from the Kiedy Odpady locality list.",
        "locality_id": "Locality ID (use instead of locality name).",
        "street": "Street name from the selected locality.",
        "street_id": "Street ID (use instead of street name).",
        "number": "House number/address value from the selected street.",
        "property_type": "Optional property type as expected by API.",
        "building_type": "Optional building type as expected by API.",
        "days": "Number of days to request from today (default: 35).",
    }
}


def _normalize(value: str) -> str:
    return value.strip().lower().casefold()


def _pick_icon(name: str) -> str | None:
    lowered = name.lower()
    for key, icon in ICON_MAP.items():
        if key in lowered:
            return icon
    return None


class Source:
    def __init__(
        self,
        number: str,
        locality: str | None = None,
        locality_id: str | None = None,
        street: str | None = None,
        street_id: str | None = None,
        property_type: str = "",
        building_type: str = "",
        days: int = DEFAULT_DAYS,
    ):
        if not locality and not locality_id:
            raise ValueError("Either locality or locality_id must be provided.")
        if not street and not street_id:
            raise ValueError("Either street or street_id must be provided.")

        self._locality = locality
        self._locality_id = locality_id
        self._street = street
        self._street_id = street_id
        self._number = str(number).strip()
        self._property_type = property_type
        self._building_type = building_type
        self._days = days

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Origin": ORIGIN,
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
            }
        )

    def _get_localities(self) -> list[dict]:
        response = self._session.get(f"{API_URL}/territory/localities", timeout=30)
        response.raise_for_status()
        return response.json()

    def _resolve_locality_id(self) -> str:
        if self._locality_id:
            return self._locality_id

        localities = self._get_localities()
        assert self._locality is not None
        target = _normalize(self._locality)

        for locality in localities:
            candidates = [
                locality.get("name", ""),
                locality.get("extendedName", ""),
            ]
            if any(_normalize(candidate) == target for candidate in candidates if candidate):
                return locality["id"]

        suggestions = [
            locality.get("extendedName") or locality.get("name")
            for locality in localities
            if locality.get("name")
        ]
        raise SourceArgumentNotFoundWithSuggestions(
            "locality",
            self._locality,
            suggestions=suggestions,
        )

    def _get_streets(self, locality_id: str) -> list[dict]:
        response = self._session.get(
            f"{API_URL}/territory/localities/{locality_id}/streets",
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def _resolve_street_id(self, locality_id: str) -> str:
        if self._street_id:
            return self._street_id

        streets = self._get_streets(locality_id)
        assert self._street is not None
        target = _normalize(self._street)

        for street in streets:
            candidates = [street.get("name", ""), street.get("extendedName", "")]
            if any(_normalize(candidate) == target for candidate in candidates if candidate):
                return street["id"]

        suggestions = [
            street.get("extendedName") or street.get("name")
            for street in streets
            if street.get("name")
        ]
        raise SourceArgumentNotFoundWithSuggestions(
            "street",
            self._street,
            suggestions=suggestions,
        )

    def _validate_number(self, locality_id: str, street_id: str) -> None:
        response = self._session.get(
            f"{API_URL}/territory/localities/{locality_id}/addresses/{street_id}",
            timeout=30,
        )
        response.raise_for_status()
        numbers = response.json()
        if self._number not in numbers:
            raise SourceArgumentNotFoundWithSuggestions(
                "number",
                self._number,
                suggestions=numbers,
            )

    def _get_waste_types(self) -> dict[str, str]:
        response = self._session.get(f"{API_URL}/waste-types", timeout=30)
        response.raise_for_status()
        return {item["id"]: item["name"] for item in response.json() if "id" in item}

    def fetch(self) -> list[Collection]:
        locality_id = self._resolve_locality_id()
        street_id = self._resolve_street_id(locality_id)
        self._validate_number(locality_id, street_id)
        waste_type_map = self._get_waste_types()

        today = date.today()
        date_to = today + timedelta(days=self._days)
        payload = {
            "from": today.isoformat(),
            "to": date_to.isoformat(),
            "queries": [
                {
                    "localityId": locality_id,
                    "streetId": street_id,
                    "number": self._number,
                    "propertyType": self._property_type,
                    "buildingType": self._building_type,
                }
            ],
        }

        response = self._session.post(
            f"{API_URL}/schedules/find",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        entries: list[Collection] = []
        for occurrence in data.get("occurrences", []):
            waste_name = waste_type_map.get(occurrence["what"], occurrence["what"])
            entries.append(
                Collection(
                    date=datetime.fromisoformat(occurrence["when"]).date(),
                    t=waste_name,
                    icon=_pick_icon(waste_name),
                )
            )

        return entries
