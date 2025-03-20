import streamlit as st
from agentic.interface import TravelRequest
from agentic.workflow import get_flights, get_hotels, get_activities
from langchain_integration import generate_travel_plan

def main():
    st.set_page_config(page_title="Travel Recommendation System", layout="wide")

    st.title("✈️ 🌍 🧳 Smart Travel Planner")
    st.write("Let our AI-powered system create your perfect vacation itinerary!")

    st.markdown("---")
    st.subheader("📝 Tell us about your dream trip")

    # User input with more context
    col1, col2, col3 = st.columns(3)
    with col1:
        destination = st.text_input("🏙️ Destination", "Paris")
        st.caption("Enter city, country, or region")
    with col2:
        dates = st.text_input("📅 Travel Dates", "May 5-9, 2025")
        st.caption("Format: Month Day-Day, Year")
    with col3:
        budget = st.number_input("💰 Budget ($)", min_value=100, value=1000, step=100)
        st.caption("Total budget for your trip")

    # Additional preferences
    st.subheader("🔍 Refine your preferences (optional)")
    col1, col2 = st.columns(2)
    with col1:
        travel_style = st.selectbox("🧭 Travel Style",
                                   ["Balanced", "Luxury", "Budget", "Adventure", "Cultural", "Relaxation"])
        accommodation_type = st.selectbox("🏠 Accommodation Preference",
                                        ["Hotel", "Resort", "Apartment", "Hostel", "Boutique"])
    with col2:
        travelers = st.number_input("👨‍👩‍👧‍👦 Number of Travelers", min_value=1, value=2)
        interests = st.multiselect("🎯 Interests",
                                  ["History", "Food", "Nature", "Shopping", "Art", "Nightlife", "Sports"])

    if st.button("🚀 Generate My Travel Plan"):
        with st.spinner("✨ Creating your personalized travel experience..."):
            # Create a travel request
            request = TravelRequest(destination, dates, budget)

            # Get recommendations using the agentic workflow
            flights = get_flights(request)
            hotels = get_hotels(request)
            activities = get_activities(request)

            # Generate a travel plan using LangChain
            travel_plan = generate_travel_plan(destination, dates, budget)

            st.success("🎉 Your travel plan is ready!")
            st.markdown("---")

            # Display recommendations with enhanced visuals
            st.subheader("✈️ Flight Options")
            st.caption("Best flight options based on price and convenience")
            for flight in flights:
                st.write(f"**{flight['airline']}**: ${flight['price']} "
                         f"(🛫 Departure: {flight['departure']}, 🛬 Arrival: {flight['arrival']})")

            st.markdown("---")
            st.subheader("🏨 Accommodation Options")
            st.caption("Places to stay that match your preferences")
            for hotel in hotels:
                st.write(f"**{hotel['name']}**: 💵 ${hotel['price']} per night (⭐ Rating: {hotel['rating']}/5)")

            st.markdown("---")
            st.subheader("🎭 Recommended Activities")
            st.caption("Exciting things to do at your destination")
            for activity in activities:
                st.write(f"**{activity['name']}**: 💵 ${activity['price']} (⏱️ {activity['duration']})")

            st.markdown("---")
            st.subheader("📋 Your Personalized Itinerary")
            st.info("🤖 AI-Generated Travel Plan")
            st.write(travel_plan)

            # Weather forecast
            st.markdown("---")
            st.subheader("☀️ Weather Forecast")
            st.caption(f"Expected weather in {destination} during your stay")
            st.write("Weather data would appear here")

            # Local tips
            st.markdown("---")
            st.subheader("💡 Local Tips")
            st.caption("Insider advice to enhance your trip")
            st.write("Local tips would appear here")

            # Download option
            st.download_button(
                label="📥 Download Travel Plan",
                data=travel_plan,
                file_name=f"{destination}_travel_plan.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
