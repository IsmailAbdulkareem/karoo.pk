from mcp.tools.travel_time import get_travel_time

async def rank_providers(providers: list, user_lat: float = None,
                         user_lng: float = None, user_budget: str = None) -> list:
    """
    Rank providers using 6-factor scoring formula.
    Fetches real travel time from Google Routes API for each provider.
    Returns top 3 providers sorted by score.
    """
    for p in providers:
        # Get real travel time if user location available
        eta = 30  # default fallback
        if user_lat and user_lng and p.get("lat") and p.get("lng"):
            travel = await get_travel_time(p["lat"], p["lng"], user_lat, user_lng)
            eta = travel["eta_minutes"]
        p["eta_minutes"] = eta

        # Price fit
        price_fit = 1.0
        if user_budget == "low" and p.get("rate_per_hour", 0) > 1000:
            price_fit = 0.3
        elif user_budget == "high" and p.get("rate_per_hour", 0) < 500:
            price_fit = 0.5

        # 6-factor scoring
        rating = p.get("rating", 0) / 5.0
        eta_score = 1 / (eta + 1)
        available = 1.0 if p.get("is_available") else 0.0
        on_time = p.get("on_time_score", 5.0) / 5.0
        recency = p.get("review_recency", 1.0)

        p["match_score"] = round(
            (rating    * 0.30) +
            (eta_score * 0.25) +
            (available * 0.15) +
            (on_time   * 0.15) +
            (price_fit * 0.10) +
            (recency   * 0.05), 3
        )

        print(f"[RANKING] {p.get('name', p['id'])} -> score: {p['match_score']} | ETA: {eta}min | Rating: {p.get('rating',0)}")

    sorted_providers = sorted(providers, key=lambda x: x["match_score"], reverse=True)
    return sorted_providers[:3]
