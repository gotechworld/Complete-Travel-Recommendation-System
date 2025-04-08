import streamlit as st
import io
import os
import re
import datetime
from agentic.interface import TravelRequest
from agentic.workflow import get_flights, get_hotels, get_activities
from langchain_integration import generate_travel_plan
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT

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
        fontSize=10,
        alignment=TA_CENTER
    )

    footer_style = ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.darkblue,
        alignment=TA_CENTER
    )

    # Build document
    elements = []

    # Logo and header
    # Check if logo exists, if not, create a text-based header
    logo_path = 'smart-travel.png'  # Update with the actual path to your logo
    if os.path.exists(logo_path):
        # Add logo with proper sizing
        elements.append(Image(logo_path, width=2*inch, height=0.75*inch))
    else:
        # Text-based logo as fallback
        elements.append(Paragraph("<b>SMART TRAVEL</b>",
                                 ParagraphStyle(name='LogoText',
                                              parent=styles['Title'],
                                              fontSize=20,
                                              alignment=TA_CENTER,
                                              textColor=colors.darkblue)))

    elements.append(Spacer(1, 0.25*inch))

    # Title
    elements.append(Paragraph(f"Travel Itinerary", title_style))
    elements.append(Spacer(1, 0.25*inch))

    # Add current date and time
    current_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    datetime_style = ParagraphStyle(
    name='DateTime',
    parent=styles['Normal'],
    fontSize=9,
    textColor=colors.darkblue,
    alignment=TA_RIGHT
    )
    elements.append(Paragraph(f"Generated on: {current_datetime}", datetime_style))
    elements.append(Spacer(1, 0.1*inch))

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

    # Enhanced footer with contact information
    elements.append(Paragraph("Thank you for using our Smart Travel Planner!", italic_style))
    elements.append(Spacer(1, 0.1*inch))

    # Contact information in footer
    elements.append(Paragraph(
        f"Contact us: <b>Email:</b> office@smart-travel.com | <b>Phone:</b> +39 3121144778",
        footer_style
    ))

    # Build PDF with custom page template for header/footer
    class FooterCanvas:
        def __init__(self, canvas, doc):
            self.canvas = canvas
            self.doc = doc
            self.width = letter[0]
            self.height = letter[1]

        def __call__(self, canvas, doc):
            # Save state
            canvas.saveState()

            # Add a horizontal line above footer
            canvas.setStrokeColor(colors.lightgrey)
            canvas.setLineWidth(0.5)
            canvas.line(72, 60, self.width - 72, 60)

            # Add footer text
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.darkblue)

            # Company name and copyright
            canvas.drawCentredString(self.width/2, 45, "Smart Travel - Your Journey, Our Expertise")
            canvas.drawCentredString(self.width/2, 30, "Email: office@smart-travel.com | Phone: +39 3121144778")

            # Add page number
            page_num = canvas.getPageNumber()
            canvas.drawRightString(self.width - 72, 30, f"Page {page_num}")

            # Restore state
            canvas.restoreState()

    # Build PDF with custom footer
    doc.build(elements, onFirstPage=FooterCanvas(None, None), onLaterPages=FooterCanvas(None, None))
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
        budget = st.number_input("💰 Budget ($)", min_value=100, value=5000, step=100)
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
        travelers = st.number_input("👨‍👩‍👧‍👦 Number of Travelers", min_value=1, value=10)
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
            st.caption(f"Expected weather in {destination} during your stay ({dates})")

            # Create weather forecast data for the dates
            weather_data = []
            if "may" in dates.lower():
                # Paris in May weather data (historical averages)
                weather_icons = ["🌤️", "🌦️", "☀️", "🌤️", "☀️"]
                temperatures = ["19°C/10°C", "18°C/11°C", "21°C/12°C", "20°C/11°C", "22°C/13°C"]
                conditions = ["Partly Cloudy", "Light Showers", "Sunny", "Partly Cloudy", "Sunny"]
                precipitation = ["10%", "30%", "5%", "15%", "5%"]
            
                # Extract the date range from the input
                date_parts = dates.split("-")
                if len(date_parts) >= 2:
                    try:
                        start_day = int(date_parts[0].split(" ")[-1])
                        end_day = int(date_parts[1].split(" ")[0])
                        month = date_parts[0].split(" ")[0]
                        year = date_parts[1].split(" ")[-1]
            
                        # Create a row for each day in the range
                        for i, day in enumerate(range(start_day, end_day + 1)):
                            if i < len(weather_icons):
                                weather_data.append({
                                    "date": f"{month} {day}, {year}",
                                    "icon": weather_icons[i],
                                    "temp": temperatures[i],
                                    "condition": conditions[i],
                                    "precipitation": precipitation[i]
                                })
                    except (ValueError, IndexError):
                        # Fallback if date parsing fails
                        weather_data = [
                            {"date": "May 5, 2025", "icon": "🌤️", "temp": "19°C/10°C", "condition": "Partly Cloudy", "precipitation": "10%"},
                            {"date": "May 6, 2025", "icon": "🌦️", "temp": "18°C/11°C", "condition": "Light Showers", "precipitation": "30%"},
                            {"date": "May 7, 2025", "icon": "☀️", "temp": "21°C/12°C", "condition": "Sunny", "precipitation": "5%"},
                            {"date": "May 8, 2025", "icon": "🌤️", "temp": "20°C/11°C", "condition": "Partly Cloudy", "precipitation": "15%"},
                            {"date": "May 9, 2025", "icon": "☀️", "temp": "22°C/13°C", "condition": "Sunny", "precipitation": "5%"}
                        ]
            else:
                # Generic weather data if not May
                weather_data = [
                    {"date": "Day 1", "icon": "🌤️", "temp": "19°C/10°C", "condition": "Partly Cloudy", "precipitation": "10%"},
                    {"date": "Day 2", "icon": "🌦️", "temp": "18°C/11°C", "condition": "Light Showers", "precipitation": "30%"},
                    {"date": "Day 3", "icon": "☀️", "temp": "21°C/12°C", "condition": "Sunny", "precipitation": "5%"},
                    {"date": "Day 4", "icon": "🌤️", "temp": "20°C/11°C", "condition": "Partly Cloudy", "precipitation": "15%"},
                    {"date": "Day 5", "icon": "☀️", "temp": "22°C/13°C", "condition": "Sunny", "precipitation": "5%"}
                ]
            
            # Display weather data in a nice format
            cols = st.columns(len(weather_data))
            for i, day in enumerate(weather_data):
                with cols[i]:
                    st.markdown(f"**{day['date']}**")
                    st.markdown(f"<h1 style='text-align: center; font-size: 40px;'>{day['icon']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-weight: bold;'>{day['temp']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center;'>{day['condition']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center;'>Rain: {day['precipitation']}</p>", unsafe_allow_html=True)
            
            # Weather summary
            avg_high = sum([int(day['temp'].split('/')[0].replace('°C', '')) for day in weather_data]) / len(weather_data)
            avg_low = sum([int(day['temp'].split('/')[1].replace('°C', '')) for day in weather_data]) / len(weather_data)
            rainy_days = sum(1 for day in weather_data if int(day['precipitation'].replace('%', '')) > 20)
            
            st.markdown(f"""
            **Weather Summary:**
            - Average High: {avg_high:.1f}°C
            - Average Low: {avg_low:.1f}°C
            - Rainy Days: {rainy_days}
            - Overall: {'Mostly sunny with occasional showers' if rainy_days <= 2 else 'Mixed conditions with several rainy periods'}
            """)
            
            st.caption("Note: Weather forecast is based on historical averages and may vary. Check closer to your travel date for more accurate predictions.")
            
            # Local tips
            st.markdown("---")
            st.subheader("💡 Local Tips")
            st.caption("Insider advice to enhance your trip")
            
            # Create local tips based on destination
            if destination.lower() == "paris":
                # Create tabs for different categories of tips
                tip_tabs = st.tabs(["🍽️ Dining", "💰 Money-Saving", "🚇 Transportation", "🗣️ Language", "⚠️ Safety"])
            
                with tip_tabs[0]:  # Dining tips
                    st.markdown("### Dining Like a Local")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Best Times to Eat:**
                        - Cafés open early (7-8am)
                        - Lunch: 12-2pm
                        - Dinner: 7:30-10pm (restaurants may not open before 7pm)
            
                        **Ordering Water:**
                        - Ask for "une carafe d'eau" for free tap water
                        - Bottled water is charged extra
            
                        **Service & Tipping:**
                        - "Service compris" means tip is included
                        - Round up or leave €1-2 for good service
                        """)
                    with col2:
                        st.markdown("""
                        **Local Specialties to Try:**
                        - Croissants from award-winning bakeries like Du Pain et des Idées
                        - Steak frites at Le Relais de l'Entrecôte
                        - Falafel in Le Marais at L'As du Fallafel
                        - Macarons from Pierre Hermé or Ladurée
                        - Wine and cheese plate at any local wine bar
            
                        **Etiquette:**
                        - Always greet with "Bonjour" when entering shops
                        - Keep bread on the table, not on your plate
                        """)
            
                with tip_tabs[1]:  # Money-saving tips
                    st.markdown("### Budget-Friendly Paris")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Free Attractions:**
                        - Museums on first Sunday of each month
                        - Père Lachaise Cemetery
                        - Sacré-Cœur Basilica
                        - Notre-Dame Cathedral (exterior)
                        - Jardin du Luxembourg
            
                        **Affordable Dining:**
                        - Eat main meal at lunch with "formule" menu
                        - Shop at markets like Marché d'Aligre
                        - Picnic in parks with baguettes, cheese, and wine
                        """)
                    with col2:
                        st.markdown("""
                        **Transportation Savings:**
                        - Buy a carnet of 10 metro tickets (cheaper than singles)
                        - Consider Paris Museum Pass for multiple attractions
                        - Use Vélib' bike sharing for short trips
                        - Walk between nearby attractions
            
                        **Shopping Tips:**
                        - Tax refund available for purchases over €100
                        - Best sales (soldes) in January and July
                        """)
            
                with tip_tabs[2]:  # Transportation tips
                    st.markdown("### Getting Around Paris")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Metro Tips:**
                        - Download RATP app for navigation
                        - Metro runs 5:30am-1:15am (2:15am weekends)
                        - Keep ticket until you exit (inspections occur)
                        - Line 1 connects many major attractions
            
                        **Airport Transfers:**
                        - RER B train: CDG to central Paris (€11.40)
                        - Orlybus: Orly to Denfert-Rochereau (€9.50)
                        - Allow 60-90 minutes for airport transfers
                        """)
                    with col2:
                        st.markdown("""
                        **Walking Routes:**
                        - Seine riverside paths connect many attractions
                        - Covered passages (Passage des Panoramas, etc.)
                        - Canal Saint-Martin for trendy neighborhoods
            
                        **Avoiding Crowds:**
                        - Major attractions open early (8-9am)
                        - Visit Louvre on Wednesday/Friday evenings
                        - Eiffel Tower least crowded during dinner hours
                        - Book tickets online to skip lines
                        """)
            
                with tip_tabs[3]:  # Language tips
                    st.markdown("### Essential French Phrases")
                    phrases = {
                        "Hello": "Bonjour (bon-zhoor)",
                        "Good evening": "Bonsoir (bon-swahr)",
                        "Please": "S'il vous plaît (seel voo pleh)",
                        "Thank you": "Merci (mehr-see)",
                        "You're welcome": "De rien (duh ree-en)",
                        "Excuse me": "Excusez-moi (ex-koo-zay mwah)",
                        "Do you speak English?": "Parlez-vous anglais? (par-lay voo on-glay)",
                        "I don't understand": "Je ne comprends pas (zhuh nuh kom-pron pah)",
                        "Where is...?": "Où est...? (oo eh)",
                        "How much is it?": "C'est combien? (say kom-bee-en)",
                        "The bill, please": "L'addition, s'il vous plaît (lah-dee-see-ohn seel voo pleh)"
                    }
            
                    # Display phrases in a nice format
                    for phrase, translation in phrases.items():
                        st.markdown(f"**{phrase}:** {translation}")
            
                    st.info("💡 Tip: Even a simple 'Bonjour' before speaking English is greatly appreciated by locals!")
            
                with tip_tabs[4]:  # Safety tips
                    st.markdown("### Safety & Etiquette")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Common Scams to Avoid:**
                        - Petition signers (distraction technique)
                        - Friendship bracelet offers (especially near Sacré-Cœur)
                        - "Gold ring" found on the ground
                        - Forced help with ticket machines
            
                        **Pickpocket Awareness:**
                        - Be vigilant on metro line 1 and at tourist spots
                        - Front pockets or money belts recommended
                        - Keep bags zipped and in front of you
                        """)
                    with col2:
                        st.markdown("""
                        **Emergency Numbers:**
                        - General Emergency: 112
                        - Police: 17
                        - Ambulance: 15
                        - Fire: 18
            
                        **Health & Comfort:**
                        - Pharmacies marked with green cross signs
                        - Public toilets (sanisettes) are free
                        - Drinking water from Wallace fountains is safe
                        - Dress in layers for changing weather
                        """)
            
                    st.warning("⚠️ Be especially vigilant around the Eiffel Tower, Louvre, and Montmartre areas where pickpockets target tourists.")
            
            else:
                # Generic tips for other destinations
                st.info(f"Local tips for {destination} would appear here. Our travel experts are constantly updating our database with insider knowledge for destinations worldwide.")
            
                # Placeholder for generic tips
                st.markdown("""
                ### General Travel Tips:
            
                - Research local customs and etiquette before your trip
                - Learn a few basic phrases in the local language
                - Keep digital and physical copies of important documents
                - Notify your bank of travel plans to avoid card blocks
                - Consider purchasing travel insurance
                - Stay hydrated and be mindful of jet lag
                - Use apps like Google Maps to download offline maps
                """)
            
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
