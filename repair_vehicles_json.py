import json
import os
from pathlib import Path
import logging
from datetime import datetime
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Configuration: Always resolve data/vehicles.json relative to the current working directory (project root)
DATA_DIR = Path.cwd() / "data"
VEHICLES_FILE = DATA_DIR / "vehicles.json"
BACKUP_FILE = DATA_DIR / f"vehicles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Valid US state codes (from your cogs)
VALID_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
}

def validate_vehicle(vehicle):
    """Validate a vehicle entry against cog requirements."""
    required_fields = {"userId", "make", "model", "color", "state", "plate", "registeredAt"}
    if not all(field in vehicle for field in required_fields):
        logger.warning(f"Missing fields in vehicle: {vehicle}")
        return False
    
    # Validate userId (basic check for numeric string)
    if not isinstance(vehicle["userId"], str) or not vehicle["userId"].isdigit():
        logger.warning(f"Invalid userId in vehicle: {vehicle['userId']}")
        return False
    
    # Validate make, model, color (non-empty, max 20 chars)
    for field in ["make", "model", "color"]:
        if not isinstance(vehicle[field], str) or not vehicle[field] or len(vehicle[field]) > 20:
            logger.warning(f"Invalid {field} in vehicle: {vehicle[field]}")
            return False
    
    # No state validation: accept any state code
    
    # Validate plate (2–8 chars, alphanumeric or hyphen)
    plate = vehicle["plate"]
    if not (2 <= len(plate) <= 8 and all(c.isalnum() or c == "-" for c in plate)):
        logger.warning(f"Invalid plate in vehicle: {plate}")
        return False
    
    # Validate registeredAt (basic ISO format check)
    try:
        datetime.fromisoformat(vehicle["registeredAt"].replace("Z", "+00:00"))
    except ValueError:
        logger.warning(f"Invalid registeredAt in vehicle: {vehicle['registeredAt']}")
        return False
    
    return True

def fix_json_file():
    """Diagnose and fix the vehicles.json file."""
    # Create backup
    if VEHICLES_FILE.exists():
        logger.info(f"Creating backup at {BACKUP_FILE}")
        shutil.copy(VEHICLES_FILE, BACKUP_FILE)
    
    # Try to load JSON
    try:
        with VEHICLES_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"JSON syntax error: {e}")
        logger.info("Attempting to create a new valid JSON file")
        data = {"vehicles": []}
    except Exception as e:
        logger.error(f"Unexpected error reading file: {e}")
        data = {"vehicles": []}
    
    # Validate structure
    if not isinstance(data, dict) or "vehicles" not in data or not isinstance(data["vehicles"], list):
        logger.warning("Invalid JSON structure. Resetting to empty vehicles array.")
        data = {"vehicles": []}
    
    # Clean and validate vehicles
    cleaned_vehicles = []
    seen_plates = set()  # Track plate-state combos to remove duplicates
    for vehicle in data["vehicles"]:
        if not validate_vehicle(vehicle):
            logger.warning(f"Skipping invalid vehicle: {vehicle}")
            continue
        plate_state = (vehicle["plate"].upper(), vehicle["state"].upper())
        if plate_state in seen_plates:
            logger.warning(f"Duplicate plate {vehicle['plate']} in state {vehicle['state']}")
            continue
        seen_plates.add(plate_state)
        # Normalize fields
        vehicle["make"] = vehicle["make"].strip()[:20]
        vehicle["model"] = vehicle["model"].strip()[:20]
        vehicle["color"] = vehicle["color"].strip()[:20]
        vehicle["state"] = vehicle["state"].upper()
        vehicle["plate"] = vehicle["plate"].upper()
        cleaned_vehicles.append(vehicle)
    
    # Update data
    data["vehicles"] = cleaned_vehicles
    logger.info(f"Found {len(cleaned_vehicles)} valid vehicles after cleaning")
    
    # Save fixed JSON
    try:
        with VEHICLES_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully saved fixed JSON to {VEHICLES_FILE}")
    except Exception as e:
        logger.error(f"Failed to save fixed JSON: {e}")
        return False
    
    return True

def main():
    """Run the JSON fixer."""
    DATA_DIR.mkdir(exist_ok=True)
    if not VEHICLES_FILE.exists():
        logger.info(f"No vehicles.json found. Creating empty file.")
        with VEHICLES_FILE.open("w", encoding="utf-8") as f:
            json.dump({"vehicles": []}, f, indent=2)
        return
    
    if fix_json_file():
        logger.info("JSON file fixed successfully!")
    else:
        logger.error("Failed to fix JSON file. Check logs for details.")

if __name__ == "__main__":
    main()
