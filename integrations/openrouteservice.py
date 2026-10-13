# Owner: Jesca Amondi
# Feature: Route Information

import httpx

from config import ORS_API_KEY, ORS_BASE_URL


class OpenRouteServiceError(RuntimeError):
    pass


def get_hgv_route(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
) -> dict:
    if not ORS_API_KEY:
        raise OpenRouteServiceError("ORS_API_KEY is not configured")

    url = f"{ORS_BASE_URL.rstrip('/')}/driving-hgv"
    payload = {
        "coordinates": [
            [origin_longitude, origin_latitude],
            [destination_longitude, destination_latitude],
        ]
    }

    try:
        response = httpx.post(
            url,
            headers={
                "Authorization": ORS_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        body = response.json()
        summary = body["routes"][0]["summary"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
        raise OpenRouteServiceError(
            "Route information could not be retrieved"
        ) from error

    return {
        "distance_km": round(float(summary["distance"]) / 1000, 2),
        "duration_minutes": max(1, round(float(summary["duration"]) / 60)),
    }
