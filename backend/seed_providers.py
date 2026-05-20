"""Seed fake providers into the database for testing."""
import uuid
from db.supabase_client import supabase
from datetime import datetime

FAKE_PROVIDERS = [
    # Electricians in different sectors of Islamabad
    {"name": "Ahmed Electrician", "phone": "03001110001", "service_type": "electrician", "area": "G-10", "rate_per_hour": 500, "bio": "Expert electrician in G-10, 5 years experience"},
    {"name": "Bilal Electrician", "phone": "03001110002", "service_type": "electrician", "area": "F-11", "rate_per_hour": 650, "bio": "Specialist in home wiring and repairs, F-11 area"},
    {"name": "Danish Electrician", "phone": "03001110003", "service_type": "electrician", "area": "I-8", "rate_per_hour": 450, "bio": "Affordable electrician in I-8, all types of electrical work"},

    # Plumbers
    {"name": "Umer Plumber", "phone": "03001110004", "service_type": "plumber", "area": "G-11", "rate_per_hour": 600, "bio": "Expert plumber in G-11, water line and drainage specialist"},
    {"name": "Farhan Plumber", "phone": "03001110005", "service_type": "plumber", "area": "F-10", "rate_per_hour": 550, "bio": "Plumber in F-10, 7 years experience in pipe fixing"},
    {"name": "Hassan Plumber", "phone": "03001110006", "service_type": "plumber", "area": "E-11", "rate_per_hour": 500, "bio": "Plumber in E-11, water tank and bathroom installation"},

    # AC Technicians
    {"name": "Kamran AC", "phone": "03001110007", "service_type": "ac_technician", "area": "F-11", "rate_per_hour": 800, "bio": "AC technician in F-11, all brands repair and gas filling"},
    {"name": "Naveed AC", "phone": "03001110008", "service_type": "ac_technician", "area": "G-10", "rate_per_hour": 750, "bio": "AC specialist in G-10, split AC installation and maintenance"},
    {"name": "Rashid AC", "phone": "03001110009", "service_type": "ac_technician", "area": "I-8", "rate_per_hour": 700, "bio": "AC technician in I-8, window and split AC expert"},

    # Tutors
    {"name": "Sara Tutor", "phone": "03001110010", "service_type": "tutor", "area": "F-10", "rate_per_hour": 1000, "bio": "Mathematics and Science tutor in F-10, 5 years experience"},
    {"name": "Ayesha Tutor", "phone": "03001110011", "service_type": "tutor", "area": "G-11", "rate_per_hour": 1200, "bio": "English and Urdu tutor in G-11, expert for all grades"},
    {"name": "Zain Tutor", "phone": "03001110012", "service_type": "tutor", "area": "E-11", "rate_per_hour": 900, "bio": "Physics and Chemistry tutor in E-11, O/A Level specialist"},

    # Cleaners
    {"name": "Javed Cleaner", "phone": "03001110013", "service_type": "cleaner", "area": "I-8", "rate_per_hour": 350, "bio": "Home and office cleaner in I-8, thorough cleaning service"},
    {"name": "Tariq Cleaner", "phone": "03001110014", "service_type": "cleaner", "area": "G-10", "rate_per_hour": 300, "bio": "Deep cleaning specialist in G-10, kitchen and bathroom focus"},
    {"name": "Shahid Cleaner", "phone": "03001110015", "service_type": "cleaner", "area": "F-11", "rate_per_hour": 400, "bio": "Commercial and residential cleaner in F-11"},

    # Carpenters
    {"name": "Rafiq Carpenter", "phone": "03001110016", "service_type": "carpenter", "area": "F-10", "rate_per_hour": 700, "bio": "Furniture maker and repair carpenter in F-10"},
    {"name": "Mushtaq Carpenter", "phone": "03001110017", "service_type": "carpenter", "area": "G-11", "rate_per_hour": 650, "bio": "Carpenter in G-11, kitchen cabinets and wardrobe expert"},
    {"name": "Aslam Carpenter", "phone": "03001110018", "service_type": "carpenter", "area": "I-8", "rate_per_hour": 600, "bio": "Door and window frame carpenter in I-8"},

    # Painters
    {"name": "Nasir Painter", "phone": "03001110019", "service_type": "painter", "area": "G-10", "rate_per_hour": 500, "bio": "Home painter in G-10, interior and exterior painting"},
    {"name": "Irfan Painter", "phone": "03001110020", "service_type": "painter", "area": "F-11", "rate_per_hour": 550, "bio": "Painter in F-11, wall texture and design specialist"},
    {"name": "Saleem Painter", "phone": "03001110021", "service_type": "painter", "area": "E-11", "rate_per_hour": 480, "bio": "Affordable painter in E-11, 8 years experience"},

    # Mechanics
    {"name": "Waseem Mechanic", "phone": "03001110022", "service_type": "mechanic", "area": "I-10", "rate_per_hour": 800, "bio": "Car mechanic in I-10, engine and transmission expert"},
    {"name": "Faisal Mechanic", "phone": "03001110023", "service_type": "mechanic", "area": "G-11", "rate_per_hour": 750, "bio": "Bike and car mechanic in G-11, roadside assistance available"},
    {"name": "Khalid Mechanic", "phone": "03001110024", "service_type": "mechanic", "area": "H-8", "rate_per_hour": 900, "bio": "Heavy vehicle mechanic in H-8, 12 years experience"},

    # Cooks
    {"name": "Rizwan Cook", "phone": "03001110025", "service_type": "cook", "area": "F-10", "rate_per_hour": 600, "bio": "Home cook in F-10, Pakistani and Chinese cuisine expert"},
    {"name": "Imran Cook", "phone": "03001110026", "service_type": "cook", "area": "G-11", "rate_per_hour": 700, "bio": "Cook in G-11, BBQ and party catering specialist"},
    {"name": "Tahir Cook", "phone": "03001110027", "service_type": "cook", "area": "I-8", "rate_per_hour": 550, "bio": "Desi food specialist cook in I-8, daily meals available"},

    # Security Guards
    {"name": "Hamza Guard", "phone": "03001110028", "service_type": "security_guard", "area": "F-11", "rate_per_hour": 400, "bio": "Security guard in F-11, night shift specialist"},
    {"name": "Rizwan Guard", "phone": "03001110029", "service_type": "security_guard", "area": "G-10", "rate_per_hour": 350, "bio": "Building security guard in G-10, 24/7 available"},
    {"name": "Asif Guard", "phone": "03001110030", "service_type": "security_guard", "area": "E-11", "rate_per_hour": 380, "bio": "Watchman and security guard in E-11, reliable and punctual"},
]

# Sector coordinates (approximate center of each sector in Islamabad)
SECTOR_COORDS = {
    "G-10": (33.668, 73.022),
    "F-10": (33.676, 73.023),
    "I-8": (33.656, 73.023),
    "G-11": (33.668, 73.010),
    "F-11": (33.676, 73.011),
    "E-11": (33.684, 73.011),
    "I-10": (33.656, 73.010),
    "H-8": (33.666, 73.023),
}

def seed():
    """Insert fake providers into the database."""
    print("Starting provider seeding...")
    count = 0
    errors = 0

    for provider in FAKE_PROVIDERS:
        area = provider["area"]
        coords = SECTOR_COORDS.get(area, (33.68, 73.06))

        # Create or find the user account for this provider
        user_data = {
            "name": provider["name"],
            "phone": provider["phone"],
            "password_hash": "$2b$12$LJ3m4ys3Lk0TSwHn6lGWOu5FM1okQlW0KOqRf5OyXK5Ozpn5qoHji",  # hashed "password123"
            "role": "provider",
            "avatar_url": f"https://ui-avatars.com/api/?name={provider['name'].replace(' ', '+')}&background=10b981&color=fff"
        }

        # Check if user already exists
        existing_user = supabase.table("users").select("id").eq("phone", provider["phone"]).execute()
        if existing_user.data:
            user_id = existing_user.data[0]["id"]
            print(f"  User {provider['name']} already exists, reusing.")
        else:
            user_res = supabase.table("users").insert(user_data).execute()
            if not user_res.data:
                print(f"  ERROR: Failed to create user for {provider['name']}")
                errors += 1
                continue
            user_id = user_res.data[0]["id"]
            print(f"  Created user {provider['name']} with ID {user_id}")

        # Check if provider profile already exists
        existing_provider = supabase.table("providers").select("id").eq("user_id", user_id).execute()
        if existing_provider.data:
            print(f"  Provider profile for {provider['name']} already exists, skipping.")
            count += 1
            continue

        # Create provider profile
        lat, lng = coords
        provider_data = {
            "user_id": user_id,
            "service_type": provider["service_type"],
            "area": area,
            "rate_per_hour": provider["rate_per_hour"],
            "bio": provider["bio"],
            "base_rate": provider["rate_per_hour"],
            "is_available": True,
            "is_online": True,
            "rating": round(4.0 + (hash(provider["name"]) % 10) / 10, 1),
            "total_ratings": hash(provider["name"]) % 20 + 1,
            "lat": lat,
            "lng": lng,
            "on_time_score": 5.0,
            "review_recency": 1.0,
            "created_at": datetime.utcnow().isoformat()
        }

        prov_res = supabase.table("providers").insert(provider_data).execute()
        if prov_res.data:
            count += 1
            print(f"  [OK] Created {provider['service_type']}: {provider['name']} ({area})")
        else:
            print(f"  ❌ Failed to create provider {provider['name']}")
            errors += 1

    print(f"\n=== Seeding Complete ===")
    print(f"  Total: {len(FAKE_PROVIDERS)}")
    print(f"  Success: {count}")
    print(f"  Errors: {errors}")

if __name__ == "__main__":
    seed()