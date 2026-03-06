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
            "NCP": "#8B0000", "RPP": "#FFD700", "Janamat": "#FFA500",
            "Independent": "#808080", "Awaiting Count": "#334155"
        }
        self.province_mapping = {
            "1": {"taplejung": 1, "panchthar": 1, "ilam": 2, "jhapa": 5, "sankhuwasabha": 1, "tehrathum": 1, "bhojpur": 1, "dhankuta": 1, "morang": 6, "sunsari": 4, "solukhumbu": 1, "khotang": 1, "okhaldhunga": 1, "udayapur": 2},
            "2": {"saptari": 4, "siraha": 4, "dhanusha": 4, "mahottari": 4, "sarlahi": 4, "rautahat": 4, "bara": 4, "parsa": 4},
            "3": {"dolakha": 1, "ramechhap": 1, "sindhuli": 2, "rasuwa": 1, "dhading": 2, "nuwakot": 2, "kathmandu": 10, "bhaktapur": 2, "lalitpur": 3, "kavrepalanchok": 2, "sindhupalchok": 2, "makwanpur": 2, "chitwan": 3},
            "4": {"gorkha": 2, "manang": 1, "lamjung": 1, "kaski": 3, "tanahun": 2, "syangja": 2, "nawalparasi-east": 2, "mustang": 1, "myagdi": 1, "baglung": 2, "parbat": 1},
            "5": {"gulmi": 2, "palpa": 2, "arghakhanchi": 1, "nawalparasi-west": 2, "rupandehi": 5, "kapilvastu": 3, "dang": 3, "pyuthan": 1, "rolpa": 1, "rukum-east": 1, "bardiya": 2, "banke": 3},
            "6": {"dolpa": 1, "mugu": 1, "humla": 1, "jumla": 1, "kalikot": 1, "dailekh": 2, "jajarkot": 1, "rukum-west": 1, "salyan": 1, "surkhet": 2},
            "7": {"bajura": 1, "bajhang": 1, "achham": 2, "doti": 1, "kailali": 5, "kanchanpur": 3, "dadeldhura": 1, "baitadi": 1, "darchula": 1}
        }

    def scrape_constituency(self, p_id, dist, cons_no):
        url = f"https://election.ekantipur.com/pradesh-{p_id}/district-{dist}/constituency-{cons_no}?lng=eng"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code != 200:
                print(f"  [!] HTTP Error {res.status_code} for {dist}-{cons_no}")
                return self.get_default()

            soup = BeautifulSoup(res.content, 'html.parser')
            candidates = []
            
            # Robust Search - Try several possible containers
            items = soup.select('.candidate-card, .candidate-list-item, .item, .candidate-list-wrapper .col-md-4')
            
            if not items:
                print(f"  [?] No candidate elements found on page for {dist}-{cons_no}")

            for idx, item in enumerate(items[:3]):
                try:
                    name_tag = item.select_one('.candidate-name, .name, h3, .candidate-list-name')
                    party_tag = item.select_one('.party-name, .party, .candidate-list-party')
                    vote_tag = item.select_one('.vote-count, .votes, .count, .candidate-list-vote')

                    if name_tag and vote_tag:
                        name = name_tag.get_text(strip=True)
                        party = party_tag.get_text(strip=True) if party_tag else "Unknown"
                        v_raw = vote_tag.get_text(strip=True)
                        votes = int(v_raw.replace(',', '').split()[0]) # Split in case of "1,200 votes"
                        
                        print(f"  [✓] Found: {name} ({party}) - {votes} votes")
                        
                        candidates.append({
                            "name": name, 
                            "party": party, 
                            "votes": votes,
                            "color": self.party_colors.get(party, "#808080")
                        })
                except Exception as e:
                    print(f"  [x] Error parsing candidate {idx+1}: {e}")
                    continue
            
            return candidates if candidates else self.get_default()
        except Exception as e:
            print(f"  [!] Connection error for {dist}-{cons_no}: {e}")
            return self.get_default()

    def get_default(self):
        return [{"name": "Awaiting Count", "party": "Awaiting Count", "votes": 0, "color": "#334155"}]

    def run(self):
        results = {}
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        total_scraped = 0

        print(f"--- Starting Election Scrape: {timestamp} ---")
        for p_id, districts in self.province_mapping.items():
            for dist, count in districts.items():
                for i in range(1, count + 1):
                    key = f"{dist.capitalize()}-{i}"
                    print(f"[{total_scraped+1}/165] Accessing {key}...")
                    
                    data = self.scrape_constituency(p_id, dist, i)
                    results[key] = data
                    total_scraped += 1
                    
                    # Small delay to prevent being blocked
                    time.sleep(0.2) 

        # Final Save
        output = {"last_updated": timestamp, "data": results}
        with open('election_data.json', 'w') as f:
            json.dump(output, f, indent=4)
        print(f"\n--- Process Complete: 165 constituencies saved ---")

if __name__ == "__main__":
    NepalElectionScraper().run()
