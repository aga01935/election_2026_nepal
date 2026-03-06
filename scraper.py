import requests
from bs4 import BeautifulSoup
import time

class NepalElectionScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        # Province mapping is required for the URL structure you shared
        self.province_map = {
            "1": ["taplejung", "panchthar", "ilam", "jhapa", "morang", "sunsari", "dhankuta", "tehrathum", "bhojpur", "sankhuwasabha", "solukhumbu", "khotang", "okhaldhunga", "udayapur"],
            "2": ["saptari", "siraha", "dhanusha", "mahottari", "sarlahi", "rautahat", "bara", "parsa"],
            "3": ["dolakha", "ramechhap", "sindhuli", "kavrepalanchok", "sindhupalchok", "kathmandu", "bhaktapur", "lalitpur", "nuwakot", "rasuwa", "dhading", "makwanpur", "chitwan"],
            "4": ["gorkha", "lamjung", "tanahun", "kaski", "manang", "mustang", "myagdi", "parbat", "baglung", "syangja", "nawalparasi-east"],
            "5": ["nawalparasi-west", "rupandehi", "kapilvastu", "palpa", "arghakhanchi", "gulmi", "dang", "pyuthan", "rolpa", "rukum-east", "banke", "bardiya"],
            "6": ["rukum-west", "salyan", "dolpa", "jajarkot", "jumla", "kalikot", "mugu", "humla", "dailekh", "surkhet"],
            "7": ["bajura", "bajhang", "doti", "achham", "kailali", "kanchanpur", "dadeldhura", "baitadi", "darchula"]
        }
        # Correct seat counts for each district
        self.district_seats = {
            "kaski": 3, "tanahun": 2, "gorkha": 2, "kathmandu": 10, "jhapa": 5, "morang": 6, # ... add others here
        }

    def scrape_data(self, province_id, district, constituency_no):
    url = f"https://election.ekantipur.com/pradesh-{province_id}/district-{district}/constituency-{constituency_no}?lng=eng"
    try:
        response = requests.get(url, headers=self.headers, timeout=10)
        if response.status_code != 200:
            return self.get_default_values()

        soup = BeautifulSoup(response.content, 'html.parser')
        candidates = []

        # STRATEGY 1: Card-based layout (The visual cards)
        # Try different classes often used by Ekantipur
        items = soup.select('.candidate-card, .candidate-list-wrapper .item, .candidate-grid .card')
        
        for item in items[:3]:
            try:
                # Flexible name hunting
                name_el = item.select_one('.candidate-name, .name, h3')
                party_el = item.select_one('.party-name, .party, .candidate-party')
                vote_el = item.select_one('.vote-count, .votes, .count')
                
                if name_el and vote_el:
                    name = name_el.get_text(strip=True)
                    party = party_el.get_text(strip=True) if party_el else "Independent"
                    votes = int(vote_el.get_text(strip=True).replace(',', ''))
                    candidates.append({"name": name, "party": party, "votes": votes})
            except:
                continue

        # STRATEGY 2: Table-based layout (Fallback if cards aren't found)
        if not candidates:
            table = soup.find('table', {'class': ['table', 'custom-table']})
            if table:
                rows = table.find_all('tr')[1:] # Skip header
                for row in rows[:3]:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        # Common order: S.N, Candidate, Party, Votes
                        candidates.append({
                            "name": cols[1].get_text(strip=True),
                            "party": cols[2].get_text(strip=True),
                            "votes": int(cols[3].get_text(strip=True).replace(',', ''))
                        })

        return candidates if candidates else self.get_default_values()

    except Exception as e:
        print(f"Scrape Error for {district}-{constituency_no}: {e}")
        return self.get_default_values()

if __name__ == "__main__":
    scraper = NepalElectionScraper()
    scraper.scrape_data()
