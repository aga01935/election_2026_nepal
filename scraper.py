import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import os

class NepalElectionScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.party_colors = {
            "RSP": "#00BFFF", "CPN-UML": "#FF0000", "NC": "#008000",
            "NCP": "#8B0000", "RPP": "#FFD700", "Independent": "#808080",
            "Awaiting Count": "#334155" # Neutral dark color for zero-vote leads
        }
        self.constituencies = self.generate_constituency_list()

    def generate_constituency_list(self):
        """Generates all 165 parliamentary constituencies of Nepal."""
        mapping = {
            # Koshi (28)
            "Taplejung": 1, "Panchthar": 1, "Ilam": 2, "Jhapa": 5, "Sankhuwasabha": 1,
            "Tehrathum": 1, "Bhojpur": 1, "Dhankuta": 1, "Morang": 6, "Sunsari": 4,
            "Solukhumbu": 1, "Khotang": 1, "Okhaldhunga": 1, "Udayapur": 2,
            # Madhesh (32)
            "Saptari": 4, "Siraha": 4, "Dhanusha": 4, "Mahottari": 4, "Sarlahi": 4,
            "Rautahat": 4, "Bara": 4, "Parsa": 4,
            # Bagmati (33)
            "Dolakha": 1, "Ramechhap": 1, "Sindhuli": 2, "Rasuwa": 1, "Dhading": 2,
            "Nuwakot": 2, "Kathmandu": 10, "Bhaktapur": 2, "Lalitpur": 3, 
            "Kavrepalanchok": 2, "Sindhupalchok": 2, "Makwanpur": 2, "Chitwan": 3,
            # Gandaki (18)
            "Gorkha": 2, "Manang": 1, "Lamjung": 1, "Kaski": 3, "Tanahun": 2,
            "Syangja": 2, "Nawalparasi-East": 2, "Mustang": 1, "Myagdi": 1, "Baglung": 2, "Parbat": 1,
            # Lumbini (26)
            "Gulmi": 2, "Palpa": 2, "Arghakhanchi": 1, "Nawalparasi-West": 2, "Rupandehi": 5,
            "Kapilvastu": 3, "Dang": 3, "Pyuthan": 1, "Rolpa": 1, "Rukum-East": 1, "Bardiya": 2, "Banke": 3,
            # Karnali (12)
            "Dolpa": 1, "Mugu": 1, "Humla": 1, "Jumla": 1, "Kalikot": 1, "Dailekh": 2,
            "Jajarkot": 1, "Rukum-West": 1, "Salyan": 1, "Surkhet": 2,
            # Sudurpashchim (16)
            "Bajura": 1, "Bajhang": 1, "Achham": 2, "Doti": 1, "Kailali": 5,
            "Kanchanpur": 3, "Dadeldhura": 1, "Baitadi": 1, "Darchula": 1
        }
        return [f"{d}-{i+1}" for d, count in mapping.items() for i in range(count)]

    def scrape_data(self, constituency):
        """Fetches live data. Returns 0 if data is not available."""
        try:
            url = f"https://election.ekantipur.com/pratinidhi-sabha/district-{constituency.lower()}"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                candidates = []
                items = soup.select('.candidate-list-wrapper .candidate-card')
                
                for item in items[:3]:
                    name = item.select_one('.candidate-name').text.strip()
                    party = item.select_one('.party-name').text.strip()
                    votes = int(item.select_one('.vote-count').text.replace(',', '').strip())
                    candidates.append({"name": name, "party": party, "votes": votes})
                
                if candidates:
                    return candidates

            # If no data found on page (e.g., counting hasn't started/loaded)
            return self.get_default_values()

        except Exception:
            # On connection failure, return 0 to prevent breaking the dashboard
            return self.get_default_values()

    def get_default_values(self):
        """Ensures the vote value is strictly 0 for unpopulated seats."""
        return [
            {"name": "Awaiting Count", "party": "Awaiting Count", "votes": 0},
            {"name": "N/A", "party": "N/A", "votes": 0}
        ]

    def run(self):
        all_results = {}
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        
        for region in self.constituencies:
            data = self.scrape_data(region)
            for item in data:
                # Use default color if party is unknown
                item['color'] = self.party_colors.get(item['party'], "#808080")
            all_results[region] = data
            time.sleep(0.05) 

        # Atomic Save
        temp_file = 'election_data_temp.json'
        with open(temp_file, 'w') as f:
            json.dump({"last_updated": timestamp, "data": all_results}, f, indent=4)
        os.replace(temp_file, 'election_data.json')

        # Update History
        history = []
        if os.path.exists('election_history.json'):
            with open('election_history.json', 'r') as f:
                try: history = json.load(f)
                except: history = []
        
        history.append({"timestamp": timestamp, "snapshot": all_results})
        with open('election_history.json', 'w') as f:
            json.dump(history[-100:], f, indent=4)

if __name__ == "__main__":
    scraper = NepalElectionScraper()
    scraper.run()
