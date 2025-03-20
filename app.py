import streamlit as st
import io
from agentic.interface import TravelRequest
from agentic.workflow import get_flights, get_hotels, get_activities
from langchain_integration import generate_travel_plan
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch

def create_pdf(content, destination, dates, budget, hotels, flights, activities):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title',
                             fontName='Helvetica-Bold',
                             fontSize=20,
                             alignment=1,
                             spaceAfter=12))
    styles.add(ParagraphStyle(name='Heading2',
                             fontName='Helvetica-Bold',
                             fontSize=14,
                             spaceBefore=12,
                             spaceAfter=6))
    styles.add(ParagraphStyle(name='Normal',
                             fontName='Helvetica',
                             fontSize=10,
                             spaceBefore=6,
                             spaceAfter=6))
    styles.add(ParagraphStyle(name='Italic',
                             fontName='Helvetica-Oblique',
                             fontSize=10))

    # Build document
    elements = []

    # Logo and header
    # elements.append(Image('logo.png', width=1.5*inch, height=0.5*inch))  # Uncomment if you have a logo
    elements.append(Paragraph(f"Travel Itinerary", styles['Title']))
    elements.append(Spacer(1, 0.25*inch))

    # Trip summary
    trip_info = [
        ['Destination:', destination],
        ['Travel Dates:', dates],
        ['Budget:', f"${budget}"]
    ]

    trip_table = Table(trip_info, colWidths=[1.5*inch, 4*inch])
    trip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(trip_table)
    elements.append(Spacer(1, 0.25*inch))

    # Itinerary
    elements.append(Paragraph("Your Personalized Travel Plan", styles['Heading2']))
    elements.append(Paragraph(content, styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))

    # Flight information
    elements.append(Paragraph("Flight Options", styles['Heading2']))
    flight_data = [['Airline', 'Price', 'Departure', 'Arrival']]
    for flight in flights[:3]:  # Show top 3 flights
        flight_data.append([
            flight['airline'],
            f"${flight['price']}",
            flight['departure'],
            flight['arrival']
        ])

    flight_table = Table(flight_data, colWidths=[1.25*inch, 1*inch, 1.5*inch, 1.5*inch])
    flight_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(flight_table)
    elements.append(Spacer(1, 0.25*inch))

    # Hotel information
    elements.append(Paragraph("Accommodation Options", styles['Heading2']))
    hotel_data = [['Hotel', 'Price per Night', 'Rating']]
    for hotel in hotels[:3]:  # Show top 3 hotels
        hotel_data.append([
            hotel['name'],
            f"${hotel['price']}",
            f"{hotel['rating']}⭐"
        ])

    hotel_table = Table(hotel_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
    hotel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(hotel_table)
    elements.append(Spacer(1, 0.25*inch))

    # Activities
    elements.append(Paragraph("Recommended Activities", styles['Heading2']))
    activity_data = [['Activity', 'Price', 'Duration']]
    for activity in activities[:5]:  # Show top 5 activities
        activity_data.append([
            activity['name'],
            f"${activity['price']}",
            activity['duration']
        ])

    activity_table = Table(activity_data, colWidths=[3*inch, 1*inch, 1*inch])
    activity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(activity_table)
    elements.append(Spacer(1, 0.5*inch))

    # Footer
    elements.append(Paragraph("Thank you for using our Smart Travel Planner!", styles['Italic']))
    elements.append(Paragraph("Contact us at travel@example.com for any questions.", styles['Italic']))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

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
            pdf_buffer = create_pdf(
                travel_plan,
                destination,
                dates,
                budget,
                hotels,
                flights,
                activities
            )
            st.download_button(
                label="📥 Download Travel Plan as PDF",
                data=pdf_buffer,
                file_name=f"{destination}_travel_plan.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
