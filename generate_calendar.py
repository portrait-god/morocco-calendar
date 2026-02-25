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
            "end_date": "2026-06-08",
            "budget_per_night": "9-13€",
            "schengen_reset": "June 10",
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        },
        "days": []
    }

    hostels = {
        "Tangier": {"name": "The Medina Hostel Tangier", "price": "€8-11/night", "neighborhood": "Kasbah / Petit Socco", "notes": "Rooftop ocean views, good wifi"},
        "Chefchaouen": {"name": "Pension Souika", "price": "€7-10/night", "neighborhood": "Medina", "notes": "Best wifi in town, rooftop terrace"},
        "Fez": {"name": "Funky Fes", "price": "€8-12/night", "neighborhood": "Fes el-Bali", "notes": "Wifi throughout, free breakfast + dinner"},
        "Marrakech": {"name": "Equity Point Marrakech", "price": "€9-13/night", "neighborhood": "Medina near Jemaa el-Fna", "notes": "Pool, good wifi, social"},
        "Essaouira": {"name": "Moga Hostel", "price": "€9-12/night", "neighborhood": "Heart of medina", "notes": "Popular with surfers + nomads"},
        "Rabat": {"name": "Dar El Kebira (or Airbnb)", "price": "€10-18/night", "neighborhood": "Agdal", "notes": "Modern, fast wifi, government tech parks"}
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
        }
    }
    
    city_counters = {
        "Tangier": 0, "Chefchaouen": 0, "Fez": 0, "Rabat": 0, "Essaouira": 0, "Marrakech": 0
    }

    # City durations
    # Tangier: Days 1-14 | Mar 11 - Mar 24
    # Chef: Days 15-17 | Mar 25 - Mar 27 (3 days)
    # Fez: Days 18-26 | Mar 28 - Apr 5 (9 days)
    # Rabat/Casa: Days 27-40 | Apr 6 - Apr 19 (14 days)
    # Essaouira: Days 41-55 | Apr 20 - May 4 (15 days)
    # Marrakech: Days 56-90 | May 5 - Jun 8 (35 days)

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
            "notes": ""
        }
        
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
                 day_entry["notes"] = "Day Trip: Asilah (Arts Town). 45 min train from Tangier."
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
                day_entry["notes"] = "Day Trip: Sefrou (Cherry Capital). Easy 40 min grand taxi."
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

        # Essaouira (Days 41-55)
        elif day_num <= 55:
            city = "Essaouira"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🌊"
            day_entry["hostel"] = hostels["Essaouira"]
            day_entry["categories"] = ["photo", "surf"]
            day_entry["content_plan"] = {"theme": f"Windy City - Day {day_num - 40}", "tiktok": "Ocean breeze vibes", "instagram": "Surf action shots", "youtube": "Sidi Kaouki surf doc"}
            
            if day_num == 41:
                day_entry["content_plan"]["theme"] = "Coastal Escape South"
                day_entry["transport"] = {"route": "Rabat → Essaouira (Train to Casa/Marrakech then Supratours)", "duration": "7-8h", "cost": "€18-25"}
            elif current_date.weekday() in [5, 6]:
                day_entry["notes"] = "Day Trip: Imsouane (Surf Village) - Check out the longboard waves. 1h taxi."
                day_entry["photography"] = {
                     "off_beaten_path": ["Imsouane Bay, Morocco", "Local surf shacks, Imsouane"],
                     "subcultures": ["Vanlife surfers, Imsouane", "Local board shapers, Imsouane"],
                     "golden_hour_spot": "Imsouane cliffs sunset",
                     "golden_hour_time": get_golden_hour(current_date)
                 }

        # Marrakech (Days 56-90)
        else:
            city = "Marrakech"
            day_entry["city"] = city
            day_entry["city_emoji"] = "🐪"
            day_entry["hostel"] = hostels["Marrakech"]
            day_entry["categories"] = ["photo", "skate", "music"]
            day_entry["content_plan"] = {"theme": f"Red City Hustle - Day {day_num - 55}", "tiktok": "Souk chaos", "instagram": "Tbourida prep", "youtube": "Marrakech Nomad Doc & Wrap-up"}
            
            if day_num == 56:
                day_entry["content_plan"]["theme"] = "Inland to the Hub"
                day_entry["transport"] = {"route": "Essaouira → Marrakech (Supratours bus)", "duration": "2.5-3h", "cost": "€8-9"}
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
            
            # Additional day trip for Marrakech
            if city == "Marrakech" and current_date.weekday() in [5, 6]:
                day_entry["notes"] = "Day Trip: Ourika Valley (Atlas Mountains). 1h Grand Taxi."
                day_entry["photography"] = {
                     "off_beaten_path": ["Ourika Valley waterfalls, Morocco", "Berber mountain villages, Ourika"],
                     "subcultures": ["Atlas Mountain artisans, Ourika"],
                     "golden_hour_spot": "Setti Fatma, Ourika Valley",
                     "golden_hour_time": get_golden_hour(current_date)
                 }
            
        # Handle Travel Days: Overwrite content plan to editing, wipe shoot locations
        if day_entry["transport"] is not None:
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
            day_entry["photography"] = None

            if day_num == 90:
                day_entry["content_plan"]["theme"] = "Departure Day"

        data["days"].append(day_entry)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Generated {DATA_FILE}")

if __name__ == "__main__":
    generate_data()
