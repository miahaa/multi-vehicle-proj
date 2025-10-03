import json
from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class Listing:
    id: str
    location_id: str
    length: int
    width: int
    price_in_cents: int

    # lane profiles for both orientations
    # profile_L: vehicles run along length → lanes = width//10, each lane capacity = length
    # profile_W: vehicles run along width  → lanes = length//10, each lane capacity = width
    def lanes_along_length(self) -> List[int]:
        return [self.length] * (self.width // 10)

    def lanes_along_width(self) -> List[int]:
        return [self.width] * (self.length // 10)

def load_locations(path: str) -> Dict[str, List[Listing]]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    listings = []
    for r in raw:
        listings.append(
            Listing(
                id=str(r["id"]),
                location_id=str(r["location_id"]),
                length=int(r["length"]),
                width=int(r["width"]),
                price_in_cents=int(r["price_in_cents"]),
            )
        )

    by_loc: Dict[str, List[Listing]] = {}
    for l in listings:
        by_loc.setdefault(l.location_id, []).append(l)
    # sort each location’s listings by price asc for friendlier, stable expansion
    for k in by_loc:
        by_loc[k].sort(key=lambda x: x.price_in_cents)
    return by_loc
