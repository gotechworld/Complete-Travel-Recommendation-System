import streamlit as st
from agentic.interface import TravelRequest
from agentic.workflow import get_flights, get_hotels, get_activities
from langchain_integration import generate_travel_plan

def main():
    st.set_page_config(page_title="Travel Recommendation System", layout="wide")

    st.title("🌍 Travel Recommendation System")
    st.write("Plan your next trip with AI-powered recommendations")

    # User input
    col1, col2, col3 = st.columns(3)
    with col1:
        destination = st.text_input("Destination", "Paris")
    with col2:
        dates = st.text_input("Dates", "May 5-9, 2025")
    with col3:
        budget = st.number_input("Budget ($)", min_value=100, value=1000, step=100)

    if st.button("Get Recommendations"):
        with st.spinner("Generating recommendations..."):
            # Create a travel request
            request = TravelRequest(destination, dates, budget)

            # Get recommendations using the agentic workflow
            flights = get_flights(request)
            hotels = get_hotels(request)
            activities = get_activities(request)

            # Generate a travel plan using LangChain
            travel_plan = generate_travel_plan(destination, dates, budget)

            # Display recommendations
            st.subheader("✈️ Flight Options")
            for flight in flights:
                st.write(f"**{flight['airline']}**: ${flight['price']} (Departure: {flight['departure']}, Arrival: {flight['arrival']})")

            st.subheader("🏨 Hotel Options")
            for hotel in hotels:
                st.write(f"**{hotel['name']}**: ${hotel['price']} per night (Rating: {hotel['rating']}⭐)")

            st.subheader("🎭 Activity Options")
            for activity in activities:
                st.write(f"**{activity['name']}**: ${activity['price']} ({activity['duration']})")

            st.subheader("🗺️ AI-Generated Travel Plan")
            st.write(travel_plan)

if __name__ == "__main__":
    main()