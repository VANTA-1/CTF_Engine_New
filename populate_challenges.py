# populate_challenges.py
import models, schemas, crud, database
from database import SessionLocal, engine

# Create all tables (in case they don't exist)
models.Base.metadata.create_all(bind=engine)
print("Ensuring database tables exist.")

db = SessionLocal()

# Define a list of sample challenges
challenge_data = [
    {
        "name": "Welcome to the Matrix",
        "description": "This is the first challenge. The flag is the answer to everything.",
        "flag": "flag{the_answer_is_42}",
        "points": 10
    },
    {
        "name": "Basic Web Exploitation",
        "description": "Inspect the source code of the main page to find the hidden flag.",
        "flag": "flag{source_code_is_not_secure}",
        "points": 50
    },
    {
        "name": "Crypto 101: Caesar Cipher",
        "description": "Decrypt this message: 'Uifsf jt b tfdsfu dpef!'",
        "flag": "flag{this_is_a_secret_code}",
        "points": 100
    },
    {
        "name": "Forensic File Analysis",
        "description": "A hidden image is embedded in this challenge description. Find it. (Hint: This is just a placeholder, the real challenge would have a file).",
        "flag": "flag{steganography_is_fun}",
        "points": 250
    }
]

print("Populating challenges...")
for challenge in challenge_data:
    # Check if challenge already exists by name
    db_challenge = crud.get_challenge_by_name(db, name=challenge["name"])
    if not db_challenge:
        print(f"Creating challenge: {challenge['name']}")
        db_challenge = models.Challenge(**challenge)
        db.add(db_challenge)
    else:
        print(f"Challenge already exists: {challenge['name']}")

db.commit()
print("Challenge population complete.")
db.close()