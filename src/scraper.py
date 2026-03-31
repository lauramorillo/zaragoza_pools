import requests
from bs4 import BeautifulSoup
from datetime import datetime
from google.cloud import firestore
import functions_framework

# URL of the pools capacity page
URL = "https://piscinaszaragoza.provis.es/aforos/web"

# Initialize Firestore client
db = firestore.Client()

@functions_framework.http
def main(request):
    """
    Cloud Function that scrapes pool occupancy data and saves it to Firestore.
    """
    try:
        # User-Agent to avoid simple blocking mechanisms
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table with class 'users'
        table = soup.find('table', class_='users')
        if not table:
            error_msg = "Error: Users data table not found on the page."
            print(error_msg)
            return error_msg, 500

        rows = table.find('tbody').find_all('tr')
        
        timestamp = datetime.now()
        batch = db.batch()
        count = 0

        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 6:
                continue
                
            # Data extraction
            name = cells[0].get_text(strip=True)
            capacity_text = cells[3].get_text(strip=True)
            current_text = cells[4].get_text(strip=True)
            status_text = cells[5].get_text(strip=True) # Ex: "83 out of 120"
            
            # Try to convert to numbers if possible, otherwise save as text
            try:
                capacity = int(capacity_text) if capacity_text.isdigit() else None
                current = int(current_text) if current_text.isdigit() else None
            except ValueError:
                capacity = None
                current = None

            # Data payload
            doc_data = {
                'timestamp': timestamp,
                'name': name,
                'capacity': capacity,
                'current_occupation': current
            }

            # Create a new document in the 'pool_readings' collection
            doc_ref = db.collection('pool_readings').document()
            batch.set(doc_ref, doc_data)
            count += 1

        # Commit the batch
        batch.commit()
        
        return f"Scraped {count} pools successfully.", 200

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to website: {e}")
        return f"Request Error: {e}", 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"Unexpected Error: {e}", 500
