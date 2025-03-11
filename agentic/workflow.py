from typing import List, Dict
from .interface import TravelRequest, TravelRecommendation

def get_flights(request: TravelRequest) -> List[Dict]:
    # Simulate retrieving flight information from an API
    flights = [
        {"airline": "Air France", "departure": "08:00", "arrival": "10:00", "price": 300.0},
        {"airline": "Tarom", "departure": "12:00", "arrival": "14:00", "price": 500.0},
    ]
    # Filter flights based on budget
    return [flight for flight in flights if flight["price"] <= request.budget]

def get_hotels(request: TravelRequest) -> List[Dict]:
    # Simulate retrieving hotel information from an API
    hotels = [
        {"name": "Zoku Paris", "rating": 8.9, "price": 250.0},
        {"name": "Villa M", "rating": 8.8, "price": 450.0},
    ]
    # Filter hotels based on budget
    return [hotel for hotel in hotels if hotel["price"] <= request.budget]

def get_activities(request: TravelRequest) -> List[Dict]:
    # Simulate retrieving activity information from an API
    activities = [
        {"name": "Admission to Disneyland Paris", "duration": "2 hours", "price": 100.0},
        {"name": "Sightseeing Cruise from the Eiffel Tower", "duration": "3 hours", "price": 75.0},
    ]
    # Filter activities based on budget
    return [activity for activity in activities if activity["price"] <= request.budget]

def travel_recommendation(request: TravelRequest) -> TravelRecommendation:
    flights = get_flights(request)
    hotels = get_hotels(request)
    activities = get_activities(request)
    return TravelRecommendation(flights, hotels, activities)