import os
import urllib.request
from pathlib import Path

# Target directory for local document store
DOC_DIR = Path(__file__).resolve().parent / 'app' / 'data' / 'rag_docs'
os.makedirs(DOC_DIR, exist_ok=True)

# Key car concepts to download
DOC_LINKS = {
    "ev_charging.txt": "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles=Electric_vehicle_charging_network&format=json",
    "drivetrain_comparison.txt": "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles=Drivetrain&format=json",
    "horsepower_torque.txt": "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles=Horsepower&format=json"
}

# Fallback content if internet connection is offline
FALLBACKS = {
    "ev_charging.txt": (
        "Electric Vehicle (EV) Charging and Battery Capacity:\n"
        "Battery capacity is measured in kilowatt-hours (kWh). A larger capacity means a longer driving range "
        "but also longer charging times. Charging rate is measured in kilowatts (kW). High-power DC fast charging "
        "can charge an EV battery from 10% to 80% in under 30 minutes, utilizing 800V architectures. Range is impacted "
        "by cabin heating, speeds, weight, and drag."
    ),
    "drivetrain_comparison.txt": (
        "Drivetrain Configurations: AWD vs RWD vs FWD:\n"
        "All-Wheel Drive (AWD) delivers power to all four wheels, offering superior traction and acceleration grip "
        "on slippery surfaces, rain, and snow. Rear-Wheel Drive (RWD) routes power to the rear wheels, providing "
        "balanced weight distribution, precise steering feedback, and sporty handling dynamics. Front-Wheel Drive "
        "(FWD) is efficient and offers good traction in standard driving but lacks performance handling."
    ),
    "horsepower_torque.txt": (
        "Understanding Horsepower and Torque in Car Performance:\n"
        "Horsepower (HP) is the rate at which an engine can perform work, dictating the vehicle's top speed and "
        "its ability to sustain acceleration at higher speeds (e.g. highway overtaking). Torque is the rotational force "
        "produced by the engine, dictating off-the-line acceleration ('shove' in the seat) and pulling power. Electric "
        "motors deliver maximum torque instantly at 0 RPM, resulting in rapid launch times."
    )
}

def fetch_documents():
    print("Fetching concepts reference documents from public sources...")
    
    for filename, url in DOC_LINKS.items():
        filepath = DOC_DIR / filename
        try:
            # Fetch Wikipedia introductory text via JSON API
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                import json
                data = json.loads(response.read().decode('utf-8'))
                pages = data.get("query", {}).get("pages", {})
                extract = ""
                for page_id, page_val in pages.items():
                    extract = page_val.get("extract", "")
                    break
                
                if extract:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(extract)
                    print(f"  [Success] Fetched online text for {filename} ({len(extract)} chars)")
                else:
                    raise ValueError("No extract found in API response")
        except Exception as e:
            # Fallback to predefined high-fidelity local concept sheet
            print(f"  [Offline/Error] Falling back to pre-defined content for {filename}: {str(e)}")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(FALLBACKS[filename])

if __name__ == "__main__":
    fetch_documents()
