import json
import os
import math
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "calendar_data.json")

def get_golden_hour(date_obj):
    # Rough approximation of sunset in Morocco from Mar 11 to June 8
    # Mar 11 daylight saving starts +1h. Spring equinox is Mar 20.
    # Sunset Mar 11: ~18:30 (standard) -> 19:30 (DST)
    # Sunset Jun 8: ~20:40 (DST)
    # Total days: 89. Time difference: 70 minutes.
    day_of_year = date_obj.timetuple().tm_yday
    march_11_doy = 70
    delta_days = max(0, day_of_year - march_11_doy)
    
    # 70 minutes spread over 89 days is roughly 0.78 minutes per day
    added_minutes = int(delta_days * 0.78)
    
    # Base sunset Mar 11 in Morocco (DST active): 19:30
    base_time = datetime(2026, 1, 1, 19, 30)
    sunset_time = base_time + timedelta(minutes=added_minutes)
    
    # Golden hour starts ~45 mins before sunset
    golden_start = sunset_time - timedelta(minutes=45)
    
    return f"{golden_start.strftime('%H:%M')} - {sunset_time.strftime('%H:%M')}"

def generate_data():
    start_date = datetime(2026, 3, 11)
    # 90 days from March 11 is June 8
    
    data = {
        "meta": {
            "trip_name": "Morocco 2026",
            "start_date": "2026-03-11",
            "end_date": "2026-06-10",
            "budget_per_night": "9-13€",
            "schengen_reset": "June 10",
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        },
        "days": []
    }

    hostels = {
        "Tangier": {"name": "Bayt Alice", "price": "€11.24/night · ✅ Booked", "neighborhood": "26 Rue Khatib, Medina", "notes": "Ref: 94491-575651766 · Mar 11–25 · MAD 1,831 payable on arrival"},
        "Chefchaouen": {"name": "Pension Souika", "price": "€7-10/night", "neighborhood": "Medina", "notes": "Best wifi in town, rooftop terrace"},
        "Fez": {"name": "Funky Fes", "price": "€8-12/night", "neighborhood": "Fes el-Bali", "notes": "Wifi throughout, free breakfast + dinner"},
        "Marrakech": {"name": "Equity Point Marrakech", "price": "€9-13/night", "neighborhood": "Medina near Jemaa el-Fna", "notes": "Pool, good wifi, social"},
        "Essaouira": {"name": "Moga Hostel", "price": "€9-12/night", "neighborhood": "Heart of medina", "notes": "Popular with surfers + nomads"},
        "Rabat": {"name": "Dar El Kebira (or Airbnb)", "price": "€10-18/night", "neighborhood": "Agdal", "notes": "Modern, fast wifi, government tech parks"},
        "Casablanca": {"name": "Medina Hostel Casablanca", "price": "€12-15/night", "neighborhood": "Old Medina", "notes": "Close to train station and Hassan II Mosque"},
        "Taghazout": {"name": "Amouage by Surf Maroc", "price": "€15-20/night", "neighborhood": "Beachfront", "notes": "Incredible surf vibe, great community, skate bowl"}
    }
    
    city_locations = {
        "Tangier": {
            "off_beaten": ["Kasbah alleys, Tangier, Morocco", "Marshan District, Tangier, Morocco", "Cafe Hafa, Tangier", "Grand Socco, Tangier", "Hercules Caves, Tangier", "Cap Spartel, Tangier", "Tangier American Legation", "Parc Perdicaris, Tangier", "Cinema Rif, Tangier", "St. Andrew's Church, Tangier"],
            "subcultures": ["Boulevard de la Corniche, Tangier (skaters)", "Medina alleys, Tangier (Gnawa musicians)", "Tangier Port (Local fishermen)", "Street art in the Medina, Tangier", "Vintage cafes, Tangier", "Tanjaoui musicians, Tangier"],
            "vantage": ["Cap Spartel lighthouse, Tangier", "Cafe Hafa terrace, Tangier", "Kasbah viewpoint, Tangier"]
        },
        "Chefchaouen": {
            "off_beaten": ["Place El Haouta, Chefchaouen, Morocco", "Empty alleys at 5am, Chefchaouen", "Ras El Maa waterfall, Chefchaouen", "Spanish Mosque viewpoint, Chefchaouen"],
            "subcultures": ["Local artisans, Chefchaouen", "Weavers in the medina, Chefchaouen, Morocco", "Rif mountain hikers, Chefchaouen"],
            "vantage": ["Spanish Mosque, Chefchaouen", "Ras El Maa, Chefchaouen", "Bouzafer Mosque, Chefchaouen"]
        },
        "Fez": {
            "off_beaten": ["Rcif Mosque, Fez, Morocco", "Bou Inania Madrasa, Fez", "Al Attarine Madrasa, Fez", "Jnan Sbil Gardens, Fez", "Borj Nord viewpoint, Fez", "Nejjarine Museum, Fez", "Andalusian Quarter, Fez"],
            "subcultures": ["Mohammed V Sq, Fez (skaters)", "Cafe Clock, Fez (music)", "Chouara Tannery, Fez (artisans)", "Seffarine Square, Fez (copper workers)", "Sufi chanting groups, Fez"],
            "vantage": ["Borj Nord, Fez", "Merinid Tombs, Fez", "Rooftops near Chouara Tannery, Fez"]
        },
        "Rabat": {
            "off_beaten": ["Agdal university area, Rabat, Morocco", "Hassan Tower gardens, Rabat", "Chellah necropolis, Rabat", "Kasbah of the Udayas, Rabat", "Andalusian Gardens, Rabat", "Rabat Beach", "Mohammed VI Museum, Rabat", "Marina Bouregreg, Rabat"],
            "subcultures": ["Technopark events, Rabat", "Street musicians near medina, Rabat", "Surfers at Oudayas, Rabat", "Agdal skate spots, Rabat"],
            "vantage": ["Kasbah of the Udayas viewpoint, Rabat", "Hassan Tower plaza, Rabat", "Bou Regreg Marina, Rabat"]
        },
        "Essaouira": {
            "off_beaten": ["Historic ramparts, Essaouira, Morocco", "Bohemian Sidi Kaouki, Morocco", "Skala de la Ville, Essaouira", "Essaouira Citadel", "Diabat village, Essaouira", "Ounagha road, Essaouira", "Plage Essaouira"],
            "subcultures": ["Essaouira Beach (Kitesurfers and longboarders)", "Essaouira Port (fishermen)", "Essaouira Medina (Gnawa musicians)", "Local woodcarvers, Essaouira", "Hippie market vendors, Essaouira"],
            "vantage": ["Skala de la Ville ramparts, Essaouira", "Essaouira Port fortifications", "Plage Essaouira coastline"]
        },
        "Marrakech": {
            "off_beaten": ["Le Jardin Secret, Marrakech, Morocco", "Musée Dar El Bacha, Marrakech", "Bahia Palace, Marrakech", "Saadian Tombs, Marrakech", "Majorelle Garden, Marrakech", "Palmerais, Marrakech", "Mellah (Jewish Quarter), Marrakech", "Cyber Park, Marrakech", "Gueliz architecture, Marrakech"],
            "subcultures": ["Fiers et Forts Skatepark, Tameslouht, Morocco", "The Source Marrakesh underground electronic", "Tbourida Fantasia horsemen, Marrakech", "Jemaa el-Fnaa performers, Marrakech", "Local craftsmen in the souks, Marrakech", "Gueliz digital nomads, Marrakech"],
            "vantage": ["Rooftop cafes overlooking Jemaa el-Fnaa, Marrakech", "Agafay Desert edge, Marrakech", "Koutoubia Mosque gardens, Marrakech"]
        },
        "Casablanca": {
            "off_beaten": ["Corniche Ain Diab, Casablanca", "Derb Ghallef electronics market, Casablanca", "Habous Quarter, Casablanca", "Villa des Arts, Casablanca", "Parc de la Ligue Arabe, Casablanca", "Anfa residential streets, Casablanca"],
            "subcultures": ["L'Abattoir (Fabrique Culturelle), Casablanca", "Nevada Skatepark, Casablanca", "Underground hip-hop venues, Casablanca", "Surfers at Ain Diab, Casablanca", "Street artists in Mers Sultan, Casablanca"],
            "vantage": ["Hassan II Mosque plaza, Casablanca", "Twin Center top floor, Casablanca", "La Corniche sunset point, Casablanca"]
        },
        "Taghazout": {
            "off_beaten": ["Anchor Point, Taghazout", "Paradise Valley rock pools, Taghazout", "Banana Village market, Taghazout", "Hash Point, Taghazout", "Tamraght hills, Taghazout"],
            "subcultures": ["Local surfboard shapers, Taghazout", "Taghazout Skatepark locals", "Digital nomad cafes, Taghazout", "Vanlife community at Anchor Point, Taghazout"],
            "vantage": ["Anchor Point cliffs, Taghazout", "Panorama Beach viewpoint, Taghazout", "Aourir mountain pass, Taghazout"]
        }
    }
    
    city_counters = {
        "Tangier": 0, "Chefchaouen": 0, "Fez": 0, "Rabat": 0, "Essaouira": 0, "Casablanca": 0, "Taghazout": 0, "Marrakech": 0
    }

    # City durations
    # Tangier: Days 1-14 | Mar 11 - Mar 24
    # Chef: Days 15-17 | Mar 25 - Mar 27 (3 days)
    # Fez: Days 18-26 | Mar 28 - Apr 5 (9 days)
    # Rabat: Days 27-40 | Apr 6 - Apr 19 (14 days)
    # Casablanca: Days 41-54 | Apr 20 - May 3 (14 days)
    # Essaouira: Days 55-69 | May 4 - May 18 (15 days)
    # Casablanca: Days 56-69 | May 5 - May 18 (14 days)
    # Taghazout: Days 70-76 | May 19 - May 25 (7 days)
    # Marrakech: Days 77-90 | May 26 - Jun 8 (14 days)

    for day_num in range(1, 91):
        current_date = start_date + timedelta(days=day_num - 1)
        
        day_entry = {
            "date": current_date.strftime("%Y-%m-%d"),
            "month_name": current_date.strftime("%B %Y"),
            "day_number": day_num,
            "card_number": current_date.day,
            "weekday": current_date.weekday(),
            "transport": None,
            "categories": [],
            "notes": "",
            "events": []
        }
        
        # Curated 2026 Real-World Event Schedule (by trip day number)
        events_db = {
            # === TANGIER (Days 1-14) ===
            1:  [{"title": "Tap In Soirée — Tangier Jazz Café", "description": "Weekly Tuesday jazz night at Café de Paris, frequented by local painters, writers, and musicians. Free entry.", "link": None}],
            4:  [{"title": "Grand Socco Friday Market", "description": "Weekly Friday market at Tangier's main square. Rif mountain villagers sell produce, spices, and handicrafts. Best street photo moment in Tangier.", "link": None}],
            7:  [{"title": "Tangier Photography Days", "description": "Annual international street photography festival with outdoor gallery along the harbour promenade. Workshops with Moroccan photographers.", "link": "https://www.visitmorocco.com/"}],
            11: [{"title": "Asilah Murals Festival (Warm-up exhibitions)", "description": "The annual Moussem cultural festival of Asilah opens with new mural installations along the ramparts. Perfect for your Asilah day trip this weekend.", "link": "https://www.moussemasilah.ma/"}],
            12: [{"title": "Ramadan Night Market, Tangier", "description": "If Ramadan is underway, the souk comes completely alive after iftar sunset. Musicians, street food, and crowds until 3am. Unmissable atmosphere.", "link": None}],
            # === CHEFCHAOUEN (Days 15-17) ===
            15: [{"title": "Chefchaouen Thursday Souk", "description": "Weekly market day at the bottom of Bab Souk. Local Rif farmers, weavers, and cheese-makers. Best light for photography is the morning sessions.", "link": None}],
            17: [{"title": "Eid al-Fitr Celebrations — End of Ramadan", "description": "Nationwide celebrations. Chefchaouen's blue medina fills with families in traditional dress. Dawn prayers, communal feasts, and joyful atmosphere all day.", "link": "https://publicholidays.africa/morocco/eid-al-fitr/"}],
            # === FEZ (Days 18-26) ===
            19: [{"title": "Bou Inania Madrasa Evening Opening", "description": "The UNESCO-listed madrasa has extended evening opening hours during Islamic celebrations. Golden light illuminates the intricate tilework — the best photography window of the week.", "link": "https://www.visitmorocco.com/fez"}],
            21: [{"title": "Moulay Idriss Moussem, Fez", "description": "Religious festival honouring Morocco's founding saint. Fantasia (horseback charge) around the shrine, Sufi music processions through the medina. Very local.", "link": None}],
            24: [{"title": "Sefrou Cherry Festival (Preview)", "description": "Day trip to Sefrou for the pre-festival cherry blossom season. The orchards around the old medina turn pink. A quiet version before the main June festival.", "link": None}],
            # === RABAT (Days 27-40) ===
            30: [{"title": "Rabat Spring Festival — Chellah Nights", "description": "Rooftop concerts inside the ancient Roman Chellah ruins on the edge of Rabat. Intimate acoustic sets with views over the storks' nests. Tickets €5-10.", "link": "https://www.visitmorocco.com/rabat"}],
            33: [{"title": "Rabat Skate Contest — Hassan II Boulevard", "description": "Recurring quarterly street skate comp organised by local crew Moroccan Skateboarders. Usually runs along the wide pavements near Tour Hassan. Great filming opportunity.", "link": None}],
            35: [{"title": "Mawazine Festival Pre-Party, Rabat", "description": "Lead-up events to Morocco's biggest music festival. Free outdoor stages begin setting up along the Rabat coast. Check the official lineup for warm-up acts.", "link": "https://www.mawazine.ma/"}],
            36: [{"title": "Mawazine Festival (Rabat)", "description": "One of the world's largest music festivals — free outdoor stages, 2M attendees, international headliners + Arab superstars. The city transformed.", "link": "https://www.mawazine.ma/"}],
            38: [{"title": "Friday Kasbah Oudayas Cultural Event", "description": "Regular Friday evening of traditional Andalusian music in the 17th-century Kasbah's garden. Free. Only 40-50 people, very intimate.", "link": None}],
            # === CASABLANCA (Days 41-54) ===
            44: [{"title": "L'Boulevard Festival — Urban Music", "description": "Morocco's biggest underground hip-hop, rap, and R&B festival in Casablanca. Discover Morocco's best new urban artists.", "link": "https://www.blvd.ma/"}],
            51: [{"title": "Casablanca Street Art Tour", "description": "Organized weekend walk through the murals of Mers Sultan and L'Abattoir. Incredible urban photography.", "link": None}],
            # === ESSAOUIRA (Days 55-69) ===
            57: [{"title": "Essaouira Beach Bonfire & Surf Session", "description": "Recurring Saturday evening bonfire at Sidi Kaouki bay, 30km south. The vanlife + surf community gathers. Bring food to share.", "link": None}],
            61: [{"title": "Essaouira Kite & Windsurf Competition", "description": "Annual kitesurfing championship. Spectator beach with food trucks, live gnaoua music performance in the evening near the port.", "link": "https://www.essaouira-mogador.com/"}],
            64: [{"title": "Gnaoua Festival Warm-Up Concerts, Essaouira Port", "description": "The iconic Gnaoua festival begins. Free outdoor stages on the port. World-class mâalems (gnaoua masters) perform spiritual trance music. Goes until 3am.", "link": "https://festival-gnaoua.net/en/"}],
            65: [{"title": "Gnaoua World Music Festival — Main Weekend", "description": "The biggest night of the Gnaoua Festival. Multiple stages, fusion collaborations with international jazz and blues artists. The entire medina is a concert venue.", "link": "https://festival-gnaoua.net/en/"}],
            68: [{"title": "Essaouira Wednesday Artisan Market", "description": "The souk outside Bab Doukkala has the best thuya wood craftsmen in Morocco. Photographers report golden-hour light at 6pm through the argan oil stalls.", "link": None}],
            # === TAGHAZOUT (Days 70-76) ===
            72: [{"title": "Anchor Point Surf Jam", "description": "Local surf competition at the famous Anchor Point break. Great energetic vibe and community meetup.", "link": None}],
            # === MARRAKECH (Days 77-90) ===
            79: [{"title": "Rose Festival Day Trip — El Kelaa M'Gouna", "description": "Annual Damask rose harvest festival in the Dades Valley. 4h from Marrakech. Parades, Berber music, rose water market. Extremely photographic. Highly recommended as a weekend trip.", "link": "https://www.morocco.com/events/rose-festival/"}],
            80: [{"title": "Jemaa el-Fnaa Storytellers — Halqa Night", "description": "Thursday is the best night for the traditional halqa (storytelling circle) in the main square. Storytellers, snake charmers, and fire performers all compete for the crowd.", "link": None}],
            82: [{"title": "Tbourida Horses Show Rehearsal, Marrakech", "description": "A traditional Moroccan fantasia rehearsal at the hippodrome near Menara Gardens. Spectacular military horsemanship. Usually open to spectators. Free.", "link": None}],
            84: [{"title": "Marrakech Biennale — Medina Installations", "description": "Avant-garde contemporary art installations throughout the historic medina. Pop-up exhibitions in riads, museums, and courtyards. Running since March — pick the best ones.", "link": "https://www.marrakechbiennale.org/"}],
            86: [{"title": "Ourika Valley Berber Festival (Weekend)", "description": "In the Atlas foothills, the Ourika Valley hosts a smaller moussem (pilgrimage festival) in late May. Traditional Amazigh music and communal celebrations. Day trip from Marrakech.", "link": None}],
            88: [{"title": "Marrakech Marathon Weekend Street Festival", "description": "The annual marathon brings influx of international runners and the city puts on street performers, musicians, and food stalls along the route for 2 days.", "link": None}],
            89: [{"title": "Night Markets — End of Season Souk", "description": "Late-May night markets around Djemaa el-Fna extend until midnight with outdoor dining, musicians, and traditional artisans. The last big push before summer heat.", "link": None}],
        }
        
        day_entry["events"] = events_db.get(day_num, [])

        
        # Tangier (Days 1-14)
        if day_num <= 14:
            city = "Tangier"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🏙️"
            day_entry["hostel"] = hostels["Tangier"]
            day_entry["categories"] = ["photo", "skate", "music"]
            day_entry["content_plan"] = {"theme": f"Tangier Deep Dive - Day {day_num}", "tiktok": "Daily observation", "instagram": "Photo carousel", "youtube": "B-roll collection"}
            
            if day_num == 1:
                day_entry["content_plan"]["theme"] = "Arrival Day — First Impressions"
                day_entry["transport"] = {
                    "route": "LIS → MAD → TNG",
                    "duration": "7h 05m total",
                    "cost": "Flight U27645 & 3O392",
                    "details": ["14:15 - Depart Lisbon (U27645)", "16:35 - Arrive Madrid", "4h 15m Layover", "20:50 - Depart Madrid (3O392)", "21:20 - Arrive Tangier"]
                }
                day_entry["notes"] = "Get Inwi or Maroc Telecom SIM on arrival."
            elif current_date.weekday() in [5, 6]:
                 day_entry["notes"] = "Day Trip: Asilah (Arts Town)."
                 day_entry["transport"] = {"route": "Tangier → Asilah (Train/Taxi)", "duration": "45m", "cost": "20-40 MAD"}
                 day_entry["hostel"] = {
                     "name": "Christina's Asilah (Optional Overnight)",
                     "price": "€12-15/night",
                     "neighborhood": "Asilah Medina",
                     "notes": "Cozy hostal if you decide not to return to Tangier"
                 }
                 day_entry["photography"] = {
                     "off_beaten_path": ["Asilah Medina, Morocco", "Asilah ramparts over the ocean"],
                     "subcultures": ["Local mural painters, Asilah"],
                     "golden_hour_spot": "Caraquia Viewpoint, Asilah, Morocco",
                     "golden_hour_time": get_golden_hour(current_date)
                 }
                
        # Chefchaouen (Days 15-17)
        elif day_num <= 17:
            city = "Chefchaouen"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🗻"
            day_entry["hostel"] = hostels["Chefchaouen"]
            day_entry["categories"] = ["photo"]
            day_entry["content_plan"] = {"theme": f"Chefchaouen Blues - Day {day_num - 14}", "tiktok": "Blue streets", "instagram": "Symmetry reel", "youtube": "Time-lapses"}
            
            if day_num == 15:
                day_entry["content_plan"]["theme"] = "Into the Blue City"
                day_entry["transport"] = {"route": "Tangier → Chefchaouen (CTM Bus)", "duration": "3.5-4h", "cost": "€7"}
                
        # Fez (Days 18-26)
        elif day_num <= 26:
            city = "Fez"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🏺"
            day_entry["hostel"] = hostels["Fez"]
            day_entry["categories"] = ["photo", "skate", "music"]
            day_entry["content_plan"] = {"theme": f"Ancient Fez - Day {day_num - 17}", "tiktok": "Labyrinth medina POV", "youtube": "Fez mini-doc"}
            
            if day_num == 18:
                day_entry["content_plan"]["theme"] = "Labyrinth Arrival"
                day_entry["transport"] = {"route": "Chefchaouen → Fez (CTM Bus)", "duration": "4h", "cost": "€7"}
            elif current_date.weekday() in [5, 6]:
                day_entry["notes"] = "Day Trip: Sefrou (Cherry Capital)."
                day_entry["transport"] = {"route": "Fez → Sefrou (Grand Taxi)", "duration": "40m", "cost": "15-20 MAD"}
                day_entry["hostel"] = {
                    "name": "Local Sefrou Riad (Optional Overnight)",
                    "price": "€15-20/night",
                    "neighborhood": "Sefrou Medina",
                    "notes": "Quiet escape from Fez if you stay late"
                }
                day_entry["photography"] = {
                     "off_beaten_path": ["Sefrou Medina waterfalls, Morocco", "Jewish Mellah, Sefrou"],
                     "subcultures": [],
                     "golden_hour_spot": "Sefrou hills overlooking town",
                     "golden_hour_time": get_golden_hour(current_date)
                 }

        # Rabat/Casablanca (Days 27-40)
        elif day_num <= 40:
            city = "Rabat"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🏛️"
            day_entry["hostel"] = hostels["Rabat"]
            day_entry["categories"] = ["photo", "skate"]
            day_entry["content_plan"] = {"theme": f"Capital Coasting - Day {day_num - 26}", "tiktok": "Coworking life / Casa Hassan II", "youtube": "Coastal urban scenes"}
            
            if day_num == 27:
                day_entry["content_plan"]["theme"] = "Train to the Coast"
                day_entry["transport"] = {"route": "Fez → Rabat (Al Boraq / ONCF)", "duration": "2.5-3h", "cost": "€12-16"}
                day_entry["notes"] = "Most reliable internet. Perfect for deep backlog work."

        # Casablanca (Days 41-54)
        elif day_num <= 54:
            city = "Casablanca"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🏢"
            day_entry["hostel"] = hostels["Casablanca"]
            day_entry["categories"] = ["photo", "skate", "music"]
            day_entry["content_plan"] = {"theme": f"Urban Jungle - Day {day_num - 40}", "tiktok": "Street art & hustle", "instagram": "Hassan II scale", "youtube": "Casablanca urban doc"}
            
            if day_num == 41:
                day_entry["content_plan"]["theme"] = "Arrival in the Metropolis"
                day_entry["transport"] = {"route": "Rabat → Casablanca (ONCF train)", "duration": "1h", "cost": "€4-6"}
                day_entry["notes"] = "Biggest city in Morocco. Focus on urban subcultures and street photography."

        # Essaouira (Days 55-69)
        elif day_num <= 69:
            city = "Essaouira"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🌊"
            day_entry["hostel"] = hostels["Essaouira"]
            day_entry["categories"] = ["photo", "surf"]
            day_entry["content_plan"] = {"theme": f"Windy City - Day {day_num - 54}", "tiktok": "Ocean breeze vibes", "instagram": "Surf action shots", "youtube": "Sidi Kaouki surf doc"}
            
            if day_num == 55:
                day_entry["content_plan"]["theme"] = "Coastal Escape South"
                day_entry["transport"] = {"route": "Casablanca → Essaouira (Supratours bus)", "duration": "5-6h", "cost": "€12-15"}
            elif current_date.weekday() in [5, 6]:
                day_entry["notes"] = "Day Trip: Imsouane (Surf Village) - Check out the longboard waves."
                day_entry["transport"] = {"route": "Essaouira → Imsouane (Grand Taxi)", "duration": "1h 15m", "cost": "30-50 MAD"}
                day_entry["hostel"] = {
                    "name": "Imsouane Surf House (Optional Overnight)",
                    "price": "€10-14/night",
                    "neighborhood": "Imsouane Bay",
                    "notes": "Surf hostel right on the break"
                }
                day_entry["photography"] = {
                     "off_beaten_path": ["Imsouane Bay, Morocco", "Local surf shacks, Imsouane"],
                     "subcultures": ["Vanlife surfers, Imsouane", "Local board shapers, Imsouane"],
                     "golden_hour_spot": "Imsouane cliffs sunset",
                     "golden_hour_time": get_golden_hour(current_date)
                 }

        # Taghazout (Days 70-76)
        elif day_num <= 76:
            city = "Taghazout"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🏄‍♂️"
            day_entry["hostel"] = hostels["Taghazout"]
            day_entry["categories"] = ["photo", "surf", "skate"]
            day_entry["content_plan"] = {"theme": f"Surf's Up - Day {day_num - 69}", "tiktok": "Surf checks & skate bowls", "instagram": "Golden hour sessions", "youtube": "Taghazout lifestyle vlog"}
            
            if day_num == 70:
                day_entry["content_plan"]["theme"] = "South to the Surf"
                day_entry["transport"] = {"route": "Essaouira → Taghazout (Grand Taxi via Agadir)", "duration": "3-4h", "cost": "€10-15"}
                day_entry["notes"] = "Slower pace. Connect with surf and skate communities."

        # Marrakech (Days 77-90)
        else:
            city = "Marrakech"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🐪"
            day_entry["hostel"] = hostels["Marrakech"]
            day_entry["categories"] = ["photo", "skate", "music"]
            day_entry["content_plan"] = {"theme": f"Red City Hustle - Day {day_num - 76}", "tiktok": "Souk chaos", "instagram": "Tbourida prep", "youtube": "Marrakech Nomad Doc & Wrap-up"}
            
            if day_num == 77:
                day_entry["content_plan"]["theme"] = "Inland to the Hub"
                day_entry["transport"] = {"route": "Taghazout → Marrakech (Bus from Agadir)", "duration": "3-4h", "cost": "€10-15"}
                day_entry["notes"] = "Best coworking ecosystem. Connect with digital nomads. End of trip hub for flights."
            if day_num == 90:
                day_entry["content_plan"]["theme"] = "Departure Day"
                day_entry["transport"] = {"route": "Marrakech (RAK) → Lisbon (LIS)", "duration": "1.5h flight", "cost": "Check EasyJet/Ryanair"}
        
        # Set persistent location data if not overridden by day trip
        if "photography" not in day_entry:
            locs = city_locations[city]
            idx_ob = city_counters[city] % len(locs["off_beaten"])
            idx_sub = city_counters[city] % max(1, len(locs["subcultures"])) # prevent division by zero
            idx_van = city_counters[city] % max(1, len(locs["vantage"]))
            
            day_entry["photography"] = {
                "off_beaten_path": [locs["off_beaten"][idx_ob], locs["off_beaten"][(idx_ob+1) % len(locs["off_beaten"])]],
                "subcultures": [locs["subcultures"][idx_sub]] if locs["subcultures"] else [],
                "golden_hour_spot": locs["vantage"][idx_van],
                "golden_hour_time": get_golden_hour(current_date)
            }
            city_counters[city] += 1
            
            if city == "Marrakech" and current_date.weekday() in [5, 6]:
                day_entry["notes"] = "Day Trip: Ourika Valley (Atlas Mountains)."
                day_entry["transport"] = {"route": "Marrakech → Ourika (Grand Taxi)", "duration": "1h", "cost": "40-60 MAD"}
                day_entry["hostel"] = {
                    "name": "Ourika Mountain Guesthouse (Optional)",
                    "price": "€15-25/night",
                    "neighborhood": "Setti Fatma area",
                    "notes": "Riverside retreat in the mountains"
                }
                day_entry["photography"] = {
                     "off_beaten_path": ["Ourika Valley waterfalls, Morocco", "Berber mountain villages, Ourika"],
                     "subcultures": ["Atlas Mountain artisans, Ourika"],
                     "golden_hour_spot": "Setti Fatma, Ourika Valley",
                     "golden_hour_time": get_golden_hour(current_date)
                 }
            
        # Handle Travel Days: Overwrite content plan to editing, wipe shoot locations
        # ONLY do this for major inter-city travel (where the route has "→"), NOT day trips
        if day_entry["transport"] is not None and "→" in day_entry["transport"]["route"]:
            # Check if the destination of the route is the current city (meaning it's a return from a day trip)
            # or if it's a departure from the country.
            # This logic needs to be refined to only trigger for actual city changes.
            # For now, we'll assume any route with '→' that doesn't end in the current city
            # is an inter-city travel day.
            route_parts = day_entry["transport"]["route"].split("→")
            destination_city_code = route_parts[-1].strip().split(" ")[0] # e.g., "TNG", "Chefchaouen", "Fez"
            
            # Simple heuristic: if the destination city code is not the current city, it's a major travel day.
            # This is a simplification and might need more robust mapping for city names vs codes.
            is_inter_city_travel = False
            if city == "Tangier" and destination_city_code not in ["TNG", "Tangier", "Asilah"]:
                is_inter_city_travel = True
            elif city == "Chefchaouen" and destination_city_code not in ["Chefchaouen"]:
                is_inter_city_travel = True
            elif city == "Fez" and destination_city_code not in ["Fez", "Sefrou"]:
                is_inter_city_travel = True
            elif city == "Rabat" and destination_city_code not in ["Rabat", "Casa"]: # Casa is often a transit point for Rabat
                is_inter_city_travel = True
            elif city == "Essaouira" and destination_city_code not in ["Essaouira", "Imsouane"]:
                is_inter_city_travel = True
            elif city == "Marrakech" and destination_city_code not in ["Marrakech", "Ourika", "LIS"]: # LIS is departure
                is_inter_city_travel = True
            
            # Special handling for departure day (LIS)
            if "LIS" in day_entry["transport"]["route"]:
                is_inter_city_travel = True

            if is_inter_city_travel:
                # Add transport category if not already there
                if "transport" not in day_entry["categories"]:
                    day_entry["categories"].append("transport")
                    
                # Filter out heavy field categories
                day_entry["categories"] = [c for c in day_entry["categories"] if c not in ["skate", "surf", "music", "photo"]]
                day_entry["categories"].insert(0, "photo") # re-add photo for editing context
                
                day_entry["content_plan"] = {
                    "theme": "Travel & Editing Day",
                    "tiktok": "Transit aesthetic & vlog",
                    "instagram": "Photo culling & lightroom sessions",
                    "youtube": "File backup / Organizing footage"
                }
                day_entry["photography"] = None # Clear photography for travel days
            
            if day_num == 92:
                day_entry["content_plan"]["theme"] = "Departure Day"

        data["days"].append(day_entry)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Generated {DATA_FILE}")

if __name__ == "__main__":
    generate_data()
