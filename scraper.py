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

    def scrape_data(self):
        for province_id, districts in self.province_map.items():
            for district in districts:
                # Get the number of seats for this district (default to 1 if not in map)
                seat_count = self.district_seats.get(district, 1)
                
                for i in range(1, seat_count + 1):
                    # CONSTRUCT THE URL EXACTLY LIKE YOUR LINK:
                    url = f"https://election.ekantipur.com/pradesh-{province_id}/district-{district}/constituency-{i}?lng=eng"
                    
                    print(f"Scraping: {district.capitalize()}-{i} ({url})")
                    
                    try:
                        response = requests.get(url, headers=self.headers, timeout=10)
                        if response.status_code == 200:
                            # BeautifulSoup logic here...
                            pass 
                        time.sleep(0.1) # Avoid getting blocked
                    except Exception as e:
                        print(f"Failed {district}-{i}: {e}")

if __name__ == "__main__":
    scraper = NepalElectionScraper()
    scraper.scrape_data()
