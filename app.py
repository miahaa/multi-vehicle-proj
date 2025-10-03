from fastapi import FastAPI, HTTPException
from typing import List
from pathlib import Path

from models import VehicleReq
from data_loader import load_locations
from search import find_results

DATA_PATH = Path(__file__).resolve().parent / "data" / "listings.json"

app = FastAPI(title="Neighbor Multi-Vehicle Search", version="1.0.0")

@app.on_event("startup")
def _load_data() -> None:
    if not DATA_PATH.exists():
        raise RuntimeError(f"Missing listings.json at: {DATA_PATH}")
    # dict[str, list[Listing]]
    app.state.by_location = load_locations(str(DATA_PATH))

@app.get("/health", summary="Health check")
def health():
    return {"ok": True}

@app.post("/", summary="Find cheapest listing combinations per location")
def search(body: List[VehicleReq]):
    if not body:
        raise HTTPException(status_code=400, detail="Body must be a non-empty array of { length, quantity }")

    # Expand request into a (very small) list of vehicle lengths (≤ 5 total)
    vehicles: List[int] = []
    for v in body:
        vehicles.extend([v.length] * v.quantity)
    vehicles.sort(reverse=True)

    return find_results(vehicles, app.state.by_location)
