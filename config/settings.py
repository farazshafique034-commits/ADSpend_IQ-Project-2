from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"

APP_NAME = "AdSpend IQ"
APP_SUBTITLE = "Digital Advertising Intelligence Platform"

DEFAULT_BUDGET = 1_000_000
DEFAULT_RECORDS = 10_000
RANDOM_SEED = 42

PLATFORMS = [
    "Facebook",
    "Instagram",
    "Google",
    "TikTok",
    "YouTube"
]

CITIES = [
    "Lahore",
    "Karachi",
    "Islamabad",
    "Rawalpindi",
    "Faisalabad",
    "Multan",
    "Peshawar",
    "Sialkot"
]

CAMPAIGNS = [
    "Winter Sale",
    "Summer Collection",
    "Black Friday",
    "Brand Awareness",
    "Product Launch",
    "Eid Campaign",
    "Retargeting",
    "New Customer Acquisition"
]

DEVICES = ["Android", "iOS", "Desktop", "Tablet"]
GENDERS = ["Male", "Female", "Other"]

PLATFORM_COLORS = {
    "Facebook": "#1877F2",
    "Instagram": "#E1306C",
    "Google": "#34A853",
    "TikTok": "#8B5CF6",
    "YouTube": "#FF0033"
}

REQUIRED_COLUMNS = [
    "date", "campaign", "platform",
    "impressions", "clicks", "spend",
    "conversions", "revenue",
    "age", "gender", "city", "device"
]

for folder in [
    DATA_DIR, RAW_DIR, PROCESSED_DIR, REPORTS_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)
