import streamlit as st
import io
import re
from agentic.interface import TravelRequest
from agentic.workflow import get_flights, get_hotels, get_activities
from langchain_integration import generate_travel_plan
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

def create_pdf(content, destination, dates, budget, hotels, flights, activities):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)

    # Create styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=24
    )

    heading1_style = ParagraphStyle(
        name='Heading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceBefore=16,
        spaceAfter=10,
        textColor=colors.darkblue
    )

    heading2_style = ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.navy
    )

    heading3_style = ParagraphStyle(
        name='Heading3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.darkblue
    )

    normal_style = ParagraphStyle(
        name='CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=4,
        spaceAfter=4,
        alignment=TA_JUSTIFY
    )

    bullet_style = ParagraphStyle(
        name='CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=2,
        spaceAfter=2,
        leftIndent=20,
        bulletIndent=10
    )

    italic_style = ParagraphStyle(
        name='CustomItalic',
        parent=styles['Italic'],
        fontSize=10
    )

    # Build document
    elements = []

    # Cover page
    elements.append(Paragraph(f"Travel Itinerary", title_style))
    elements.append(Spacer(1, 0.25*inch))

    # Trip summary table with better styling
    trip_info = [
        ['Destination:', destination],
        ['Travel Dates:', dates],
        ['Budget:', f"${budget}"]
    ]

    trip_table = Table(trip_info, colWidths=[1.5*inch, 4*inch])
    trip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightsteelblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    elements.append(trip_table)
    elements.append(Spacer(1, 0.5*inch))

    # Process the travel plan content to properly format sections
    # This is the key improvement - parsing the content to create proper sections

    # First, let's clean up the content by ensuring proper line breaks
    content = content.replace('# ', '\n# ').replace('## ', '\n## ').replace('* ', '\n* ')

    # Split the content by sections
    sections = re.split(r'(# [^\n]+)', content)

    if len(sections) > 1:  # If we have proper sections
        # The first element might be empty or introductory text
        if sections[0].strip():
            elements.append(Paragraph(sections[0].strip(), normal_style))
            elements.append(Spacer(1, 0.2*inch))

        # Process each section
        for i in range(1, len(sections), 2):
            if i < len(sections):
                # Section title
                section_title = sections[i].replace('# ', '').strip()
                elements.append(Paragraph(section_title, heading1_style))

                # Section content
                if i+1 < len(sections):
                    section_content = sections[i+1]

                    # Process subsections
                    subsections = re.split(r'(## [^\n]+)', section_content)

                    if len(subsections) > 1:  # If we have subsections
                        # The first element might be content before any subsection
                        if subsections[0].strip():
                            # Process bullet points
                            bullets = subsections[0].split('\n* ')
                            if len(bullets) > 1:
                                elements.append(Paragraph(bullets[0].strip(), normal_style))
                                for bullet in bullets[1:]:
                                    if bullet.strip():
                                        elements.append(Paragraph(f"• {bullet.strip()}", bullet_style))
                            else:
                                elements.append(Paragraph(subsections[0].strip(), normal_style))

                        # Process each subsection
                        for j in range(1, len(subsections), 2):
                            if j < len(subsections):
                                # Subsection title
                                subsection_title = subsections[j].replace('## ', '').strip()
                                elements.append(Paragraph(subsection_title, heading2_style))

                                # Subsection content
                                if j+1 < len(subsections):
                                    # Process bullet points
                                    bullets = subsections[j+1].split('\n* ')
                                    if len(bullets) > 1:
                                        elements.append(Paragraph(bullets[0].strip(), normal_style))
                                        for bullet in bullets[1:]:
                                            if bullet.strip():
                                                elements.append(Paragraph(f"• {bullet.strip()}", bullet_style))
                                    else:
                                        elements.append(Paragraph(subsections[j+1].strip(), normal_style))
                    else:
                        # No subsections, just process the content
                        # Process bullet points
                        bullets = section_content.split('\n* ')
                        if len(bullets) > 1:
                            elements.append(Paragraph(bullets[0].strip(), normal_style))
                            for bullet in bullets[1:]:
                                if bullet.strip():
                                    elements.append(Paragraph(f"• {bullet.strip()}", bullet_style))
                        else:
                            elements.append(Paragraph(section_content.strip(), normal_style))
    else:
        # No sections found, just add the content as is
        elements.append(Paragraph(content, normal_style))

    # Add a page break before recommendations
    elements.append(PageBreak())

    # Flight information with improved styling
    elements.append(Paragraph("Flight Options", heading1_style))
    elements.append(Spacer(1, 0.1*inch))

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
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(flight_table)
    elements.append(Spacer(1, 0.3*inch))

    # Hotel information with improved styling
    elements.append(Paragraph("Accommodation Options", heading1_style))
    elements.append(Spacer(1, 0.1*inch))

    hotel_data = [['Hotel', 'Price per Night', 'Rating']]
    for hotel in hotels[:3]:  # Show top 3 hotels
        hotel_data.append([
            hotel['name'],
            f"${hotel['price']}",
            f"{hotel['rating']}⭐"
        ])

    hotel_table = Table(hotel_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
    hotel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(hotel_table)
    elements.append(Spacer(1, 0.3*inch))

    # Activities with improved styling
    elements.append(Paragraph("Recommended Activities", heading1_style))
    elements.append(Spacer(1, 0.1*inch))

    activity_data = [['Activity', 'Price', 'Duration']]
    for activity in activities[:5]:  # Show top 5 activities
        activity_data.append([
            activity['name'],
            f"${activity['price']}",
            activity['duration']
        ])

    activity_table = Table(activity_data, colWidths=[3*inch, 1*inch, 1*inch])
    activity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(activity_table)
    elements.append(Spacer(1, 0.5*inch))

    # Footer with improved styling
    elements.append(Paragraph("Thank you for using our Smart Travel Planner!", italic_style))
    elements.append(Paragraph("Contact us at travel@example.com for any questions.", italic_style))

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
        budget = st.number_input("💰 Budget ($)", min_value=100, value=3000, step=100)
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
        travelers = st.number_input("👨‍👩‍👧‍👦 Number of Travelers", min_value=1, value=5)
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
