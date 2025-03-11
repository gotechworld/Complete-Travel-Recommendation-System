from typing import Dict, List

class TravelRequest:
    def __init__(self, destination: str, dates: str, budget: float):
        self.destination = destination
        self.dates = dates
        self.budget = budget

class TravelRecommendation:
    def __init__(self, flights: List[Dict], hotels: List[Dict], activities: List[Dict]):
        self.flights = flights
        self.hotels = hotels
        self.activities = activities