from functools import lru_cache
from typing import List, Dict, Tuple, Optional
import heapq

from data_loader import Listing


def expand_vehicles(specs: List[Dict[str, int]]) -> List[int]:
    items: List[int] = []
    for s in specs:
        items += [int(s["length"])] * int(s["quantity"])
    # sort descending to prune deep earlier
    items.sort(reverse=True)
    return items


# lanes is a list of remaining capacities per lane (e.g., [40,40,40])
def can_fit(vehicles: Tuple[int, ...], lanes: Tuple[int, ...]) -> bool:
    # total length cannot exceed sum of lanes
    if sum(vehicles) > sum(lanes):
        return False
    return _can_fit_cached(vehicles, tuple(sorted(lanes, reverse=True)))

@lru_cache(maxsize=None)
def _can_fit_cached(vehicles: Tuple[int, ...], lanes_sorted_desc: Tuple[int, ...]) -> bool:
    if not vehicles:
        return True
    v = vehicles[0]

    lanes = list(lanes_sorted_desc)
    used_tried = set()  # avoid trying same capacity multiple times at this level

    for i, cap in enumerate(lanes):
        if cap < v or cap in used_tried:
            continue
        used_tried.add(cap)

        lanes[i] = cap - v
        # keep lanes sorted descesding to maximize cache hits
        nxt_lanes = tuple(sorted(lanes, reverse=True))
        if _can_fit_cached(tuple(vehicles[1:]), nxt_lanes):
            return True
        lanes[i] = cap

    return False

# per-location cheapest combo via best-first (uniform-cost) search ---
def cheapest_for_location(vehicles: List[int], listings: List[Listing]) -> Optional[Tuple[List[str], int]]:
    """
    Explore subsets in ascending total cost order. Each listing can be used in either orientation.
    State:
      (total_cost, last_idx, listing_ids[], lanes_tuple)
    Pop the cheapest; if lanes can fit all vehicles → that’s the optimal combo for this location.
    """
    if not vehicles:
        return ([], 0)

    v_tuple = tuple(sorted(vehicles, reverse=True))

    # min-heap priority queue
    pq: List[Tuple[int, int, Tuple[str, ...], Tuple[int, ...]]] = []

    # seed with empty state
    heapq.heappush(pq, (0, -1, tuple(), tuple()))  # (cost, last_idx, listing_ids, lanes)

    # visited pruning: (last_idx, listing_ids, lanes_sorted) -> best cost seen
    # but listing_ids grows; use a cheaper key: (last_idx, len(listing_ids), lanes)
    # combined with cost-order expansion
    seen = set()

    while pq:
        cost, last_idx, chosen_ids, lanes = heapq.heappop(pq)

        # check feasibility only if we actually have lanes
        if lanes and can_fit(v_tuple, lanes):
            return (list(chosen_ids), cost)

        key = (last_idx, len(chosen_ids), lanes)
        if key in seen:
            continue
        seen.add(key)

        # expand by adding one next listing (index strictly increasing to avoid permutations)
        for i in range(last_idx + 1, len(listings)):
            L = listings[i]
            # orientation 1: along length
            lanes_L = L.lanes_along_length()
            if lanes_L:
                new_lanes = tuple(sorted(tuple(lanes) + tuple(lanes_L), reverse=True))
                heapq.heappush(pq, (cost + L.price_in_cents, i, chosen_ids + (L.id,), new_lanes))
            # orientation 2: along width
            lanes_W = L.lanes_along_width()
            if lanes_W:
                new_lanes = tuple(sorted(tuple(lanes) + tuple(lanes_W), reverse=True))
                heapq.heappush(pq, (cost + L.price_in_cents, i, chosen_ids + (L.id,), new_lanes))

    return None

def find_results(vehicles: List[int], by_location: Dict[str, List[Listing]]):
    out = []
    for loc, lst in by_location.items():
        best = cheapest_for_location(vehicles, lst)
        if best:
            ids, total = best
            out.append({
                "location_id": loc,
                "listing_ids": ids,
                "total_price_in_cents": total
            })
    out.sort(key=lambda x: x["total_price_in_cents"])
    return out
