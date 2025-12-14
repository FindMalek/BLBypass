"""Fake data generation utilities"""

import random


def generate_fake_name() -> str:
    """
    Generate a random fake name
    
    Returns:
        Random name string
    """
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "James", "Emma",
        "Robert", "Olivia", "William", "Sophia", "Richard", "Isabella", "Joseph", "Mia",
        "Thomas", "Charlotte", "Charles", "Amelia", "Christopher", "Harper", "Daniel", "Evelyn",
        "Matthew", "Abigail", "Anthony", "Elizabeth", "Mark", "Sofia", "Donald", "Avery",
        "Steven", "Ella", "Paul", "Madison", "Andrew", "Scarlett", "Joshua", "Victoria",
        "Kenneth", "Aria", "Kevin", "Grace", "Brian", "Chloe", "George", "Camila",
        "Timothy", "Penelope", "Ronald", "Riley", "Jason", "Layla", "Edward", "Lillian"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor",
        "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Sanchez",
        "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
        "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
        "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
    ]
    
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_fake_email(name: str = None) -> str:
    """
    Generate a random fake email address
    
    Args:
        name: Optional name to use in email (if None, generates random)
        
    Returns:
        Random email string
    """
    if name:
        # Use name to create email-like address
        name_part = name.lower().replace(" ", ".").replace("'", "")
        domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]
        return f"{name_part}@{random.choice(domains)}"
    else:
        # Generate completely random email
        adjectives = ["cool", "awesome", "great", "super", "mega", "ultra", "pro", "max"]
        nouns = ["user", "person", "guy", "gal", "star", "hero", "legend", "champ"]
        numbers = random.randint(100, 9999)
        domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]
        return f"{random.choice(adjectives)}{random.choice(nouns)}{numbers}@{random.choice(domains)}"