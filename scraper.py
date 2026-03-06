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
            "RSP": "#00BFFF",      # Rastriya Swatantra Party (Blue)
            "CPN-UML": "#FF0000",  # UML (Red)
            "NC": "#008000",       # Nepali Congress (Green)
            "NCP": "#8B0000",      # Nepali Communist Party (Dark Red)
            "RPP": "#FFD700",      # Rastriya Prajatantra Party (Gold)
            "Janamat": "#FFA500",  # Janamat Party (Orange)
            "Independent": "#808080",
            "Awaiting Count": "#334155"
        }
        # The official 165 mapping by Province (Pradesh)
        self.province_mapping = {
            "1": { # Koshi (28)
                "taplejung": 1, "panchthar": 1, "ilam": 2, "jhapa": 5, "sankhuwasabha": 1,
                "tehrathum": 1, "bhojpur": 1, "dhankuta": 1, "morang": 6, "sunsari": 4,
                "solukhumbu": 1, "khotang": 1, "okhaldhunga": 1, "udayapur": 2
            },
            "2": { # Madhesh (32)
                "saptari": 4, "siraha": 4, "dhanusha": 4, "mahottari": 4, "sarlahi": 4,
                "rautahat": 4, "bara": 4, "parsa": 4
            },
            "3": { # Bagmati (33)
                "dolakha": 1, "ramechhap": 1, "sindhuli": 2, "rasuwa": 1, "dhading": 2,
                "nuwakot": 2, "kathmandu": 10, "bhaktapur": 2, "lalitpur": 3,
                "kavrepalanchok": 2, "sindhupalchok": 2, "makwanpur": 2, "chitwan": 3
            },
            "4": { # Gandaki (18)
                "gorkha": 2, "manang": 1, "lamjung": 1, "kaski": 3, "tanahun": 2,
                "syangja": 2, "nawalparasi-east": 2, "mustang": 1, "myagdi": 1, "baglung": 2, "parbat": 1
            },
            "5": { # Lumbini (26)
                "gulmi": 2, "palpa": 2, "arghakhanchi": 1, "nawalparasi-west": 2, "rupandehi": 5,
                "kapilvastu": 3, "dang": 3, "pyuthan": 1, "rolpa": 1, "rukum-east": 1, "bardiya": 2, "banke": 3
            },
            "6": { # Karnali (12)
                "dolpa": 1, "mugu": 1, "humla": 1, "jumla": 1, "kalikot": 1, "dailekh": 2,
                "jajarkot": 1, "rukum-west": 1, "salyan": 1, "surkhet": 2
            },
            "7": { # Sudurpashchim (16)
                "bajura": 1, "bajhang": 1, "achham": 2, "doti": 1, "kailali": 5,
                "kanchanpur": 3, "dadeldhura": 1, "baitadi": 1, "darchula": 1
            }
        }

    def scrape_constituency(self, p_id, dist, cons_no):
        url = f"https://election.ekantipur.com/pradesh-{p_id}/district-{dist}/constituency-{cons_no}?lng=eng"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code != 200: return self.get_default()

            soup = BeautifulSoup(res.content, 'html.parser')
            candidates = []
            
            # Robust 2026 Selectors
            items = soup.select('.candidate-card, .candidate-list-item, .item')
            for item in items[:3]:
                try:
                    name = item.select_one('.candidate-name, .name, h3').get_text(strip=True)
                    party = item.select_one('.party-name, .party').get_text(strip=True)
                    v_raw = item.select_one('.vote-count, .votes, .count').get_text(strip=True)
                    votes = int(v_raw.replace(',', ''))
                    
                    candidates.append({
                        "name": name, 
                        "party": party, 
                        "votes": votes,
                        "color": self.party_colors.get(party, "#808080")
                    })
                except: continue
            
            return candidates if candidates else self.get_default()
        except:
            return self.get_default()

    def get_default(self):
        return [{"name": "Awaiting Count", "party": "Awaiting Count", "votes": 0, "color": "#334155"}]

    def run(self):
        results = {}
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        total_scraped = 0

        for p_id, districts in self.province_mapping.items():
            for dist, count in districts.items():
                for i in range(1, count + 1):
                    key = f"{dist.capitalize()}-{i}"
                    data = self.scrape_constituency(p_id, dist, i)
                    results[key] = data
                    total_scraped += 1
                    print(f"[{total_scraped}/165] Scraped {key}")
                    time.sleep(0.1) # Respect server limits

        # Final Save
        output = {"last_updated": timestamp, "data": results}
        with open('election_data.json', 'w') as f:
            json.dump(output, f, indent=4)
        print(f"Success: 165 constituencies saved at {timestamp}")

if __name__ == "__main__":
    NepalElectionScraper().run()
