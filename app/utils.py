# Various utility functions used in the app

import requests
import hashlib

def fetch_bootswatch_themes():
    try:
        # Make a request to the Bootswatch API
        response = requests.get("https://bootswatch.com/api/5.json")
        if response.status_code == 200:
            data = response.json()
            themes = data.get('themes', [])
            if themes:
                return themes
            else:
                print("No themes found in the response.")
                return []
        else:
            print(f"Failed to fetch themes: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching Bootswatch themes: {e}")
        return []

def get_gravatar_url(email, size=200, default='identicon'):
    # Create an MD5 hash of the email address
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    # Construct the Gravatar URL
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"