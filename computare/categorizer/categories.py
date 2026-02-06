"""
Transaction category definitions for Computare.

Defines the 13 top-level categories and known merchant-to-category mappings
used for deterministic categorization before falling back to LLM.

Subcategories (stored in transactions.sub_category):
  Food & Dining      -> Coffee & Cafes, Fast Food, Restaurants, Delivery, Convenience
  Retail & Shopping  -> Groceries, Alcohol, Clothing, Electronics, Online/General,
                        Dollar/Discount, Home, Pet
  Entertainment      -> Gaming, Movies, Streaming, Activities/Venues, Events
  Transportation     -> Gas & Fuel, Parking, Ride-hailing, Auto Maintenance
  Housing            -> Home Maintenance
  Bills & Utilities  -> Bank Fees, Phone Bill, Utilities, Insurance, Loan Payments
  Healthcare         -> Pharmacy, Physio & Rehab, Medical, Optometry, Other
"""

from enum import Enum
from typing import Dict


class TransactionCategory(str, Enum):
    """The 13 top-level transaction categories."""
    FOOD_AND_DINING = "Food & Dining"
    TRANSPORTATION = "Transportation"
    RETAIL_AND_SHOPPING = "Retail & Shopping"
    BILLS_AND_UTILITIES = "Bills & Utilities"
    HEALTHCARE = "Healthcare"
    ENTERTAINMENT = "Entertainment"
    HOUSING = "Housing"
    INCOME = "Income"
    TRANSFERS = "Transfers"
    INVESTMENT = "Investment"
    EDUCATION = "Education"
    PERSONAL_CARE = "Personal Care"
    AI_AND_SOFTWARE = "AI & Software Services"


class TransactionSubCategory(str, Enum):
    """Subcategories for finer-grained classification."""
    # Food & Dining
    COFFEE_AND_CAFES = "Coffee & Cafes"
    FAST_FOOD = "Fast Food"
    RESTAURANTS = "Restaurants"
    DELIVERY = "Delivery"
    CONVENIENCE = "Convenience"
    # Retail & Shopping
    GROCERIES = "Groceries"
    ALCOHOL = "Alcohol"
    CLOTHING = "Clothing"
    ELECTRONICS = "Electronics"
    ONLINE_GENERAL = "Online/General"
    DOLLAR_DISCOUNT = "Dollar/Discount"
    HOME = "Home"
    PET = "Pet"
    # Entertainment
    GAMING = "Gaming"
    MOVIES = "Movies"
    STREAMING = "Streaming"
    ACTIVITIES_AND_VENUES = "Activities/Venues"
    EVENTS = "Events"
    # Transportation
    GAS_AND_FUEL = "Gas & Fuel"
    PARKING = "Parking"
    RIDE_HAILING = "Ride-hailing"
    AUTO_MAINTENANCE = "Auto Maintenance"
    # Housing
    HOME_MAINTENANCE = "Home Maintenance"
    # Bills & Utilities
    BANK_FEES = "Bank Fees"
    PHONE_BILL = "Phone Bill"
    UTILITIES = "Utilities"
    INSURANCE = "Insurance"
    LOAN_PAYMENTS = "Loan Payments"
    # Healthcare
    PHARMACY = "Pharmacy"
    PHYSIO_AND_REHAB = "Physio & Rehab"
    MEDICAL = "Medical"
    OPTOMETRY = "Optometry"
    OTHER = "Other"


# Maps subcategory -> parent category
SUBCATEGORY_PARENT: Dict[TransactionSubCategory, TransactionCategory] = {
    # Food & Dining
    TransactionSubCategory.COFFEE_AND_CAFES: TransactionCategory.FOOD_AND_DINING,
    TransactionSubCategory.FAST_FOOD: TransactionCategory.FOOD_AND_DINING,
    TransactionSubCategory.RESTAURANTS: TransactionCategory.FOOD_AND_DINING,
    TransactionSubCategory.DELIVERY: TransactionCategory.FOOD_AND_DINING,
    TransactionSubCategory.CONVENIENCE: TransactionCategory.FOOD_AND_DINING,
    # Retail & Shopping
    TransactionSubCategory.GROCERIES: TransactionCategory.RETAIL_AND_SHOPPING,
    TransactionSubCategory.ALCOHOL: TransactionCategory.RETAIL_AND_SHOPPING,
    TransactionSubCategory.CLOTHING: TransactionCategory.RETAIL_AND_SHOPPING,
    TransactionSubCategory.ELECTRONICS: TransactionCategory.RETAIL_AND_SHOPPING,
    TransactionSubCategory.ONLINE_GENERAL: TransactionCategory.RETAIL_AND_SHOPPING,
    TransactionSubCategory.DOLLAR_DISCOUNT: TransactionCategory.RETAIL_AND_SHOPPING,
    TransactionSubCategory.HOME: TransactionCategory.RETAIL_AND_SHOPPING,
    TransactionSubCategory.PET: TransactionCategory.RETAIL_AND_SHOPPING,
    # Entertainment
    TransactionSubCategory.GAMING: TransactionCategory.ENTERTAINMENT,
    TransactionSubCategory.MOVIES: TransactionCategory.ENTERTAINMENT,
    TransactionSubCategory.STREAMING: TransactionCategory.ENTERTAINMENT,
    TransactionSubCategory.ACTIVITIES_AND_VENUES: TransactionCategory.ENTERTAINMENT,
    TransactionSubCategory.EVENTS: TransactionCategory.ENTERTAINMENT,
    # Transportation
    TransactionSubCategory.GAS_AND_FUEL: TransactionCategory.TRANSPORTATION,
    TransactionSubCategory.PARKING: TransactionCategory.TRANSPORTATION,
    TransactionSubCategory.RIDE_HAILING: TransactionCategory.TRANSPORTATION,
    TransactionSubCategory.AUTO_MAINTENANCE: TransactionCategory.TRANSPORTATION,
    # Housing
    TransactionSubCategory.HOME_MAINTENANCE: TransactionCategory.HOUSING,
    # Bills & Utilities
    TransactionSubCategory.BANK_FEES: TransactionCategory.BILLS_AND_UTILITIES,
    TransactionSubCategory.PHONE_BILL: TransactionCategory.BILLS_AND_UTILITIES,
    TransactionSubCategory.UTILITIES: TransactionCategory.BILLS_AND_UTILITIES,
    TransactionSubCategory.INSURANCE: TransactionCategory.BILLS_AND_UTILITIES,
    TransactionSubCategory.LOAN_PAYMENTS: TransactionCategory.BILLS_AND_UTILITIES,
    # Healthcare
    TransactionSubCategory.PHARMACY: TransactionCategory.HEALTHCARE,
    TransactionSubCategory.PHYSIO_AND_REHAB: TransactionCategory.HEALTHCARE,
    TransactionSubCategory.MEDICAL: TransactionCategory.HEALTHCARE,
    TransactionSubCategory.OPTOMETRY: TransactionCategory.HEALTHCARE,
    TransactionSubCategory.OTHER: TransactionCategory.HEALTHCARE,
}


# Category colors for UI display
CATEGORY_COLORS: Dict[TransactionCategory, str] = {
    TransactionCategory.FOOD_AND_DINING: "#FF6B6B",
    TransactionCategory.TRANSPORTATION: "#4ECDC4",
    TransactionCategory.RETAIL_AND_SHOPPING: "#45B7D1",
    TransactionCategory.BILLS_AND_UTILITIES: "#FFEAA7",
    TransactionCategory.HEALTHCARE: "#E84393",
    TransactionCategory.ENTERTAINMENT: "#96CEB4",
    TransactionCategory.HOUSING: "#FFD93D",
    TransactionCategory.INCOME: "#6BCB77",
    TransactionCategory.TRANSFERS: "#B07CC6",
    TransactionCategory.INVESTMENT: "#9B59B6",
    TransactionCategory.EDUCATION: "#3498DB",
    TransactionCategory.PERSONAL_CARE: "#E91E63",
    TransactionCategory.AI_AND_SOFTWARE: "#00BCD4",
}


# Known merchant keywords -> (category, sub_category) mappings for deterministic
# classification.  Checked via substring match (case-insensitive) before the LLM.
# Values are (TransactionCategory, optional TransactionSubCategory).
#
# ORDERING: More specific keywords MUST come before less specific ones.
# e.g. "ubereats" before "uber", "animalclinic" before "clinic".
# The first match wins (early return in _match_known_merchant).
KNOWN_MERCHANT_HINTS: Dict[str, tuple] = {
    # ── AI & Software Services ──────────────────────────────────────────
    "openai": (TransactionCategory.AI_AND_SOFTWARE, None),
    "chatgpt": (TransactionCategory.AI_AND_SOFTWARE, None),
    "chatbase": (TransactionCategory.AI_AND_SOFTWARE, None),
    "openrouter": (TransactionCategory.AI_AND_SOFTWARE, None),
    "cal.com": (TransactionCategory.AI_AND_SOFTWARE, None),
    "namecheap": (TransactionCategory.AI_AND_SOFTWARE, None),
    "github": (TransactionCategory.AI_AND_SOFTWARE, None),
    "railway": (TransactionCategory.AI_AND_SOFTWARE, None),
    "anthropic": (TransactionCategory.AI_AND_SOFTWARE, None),
    "perplexity": (TransactionCategory.AI_AND_SOFTWARE, None),

    # ── Entertainment — Gaming ──────────────────────────────────────────
    "steamgames": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.GAMING),
    "playstation": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.GAMING),
    "sonyinteractive": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.GAMING),
    "kingsisle": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.GAMING),
    "wizard101": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.GAMING),
    "riotgames": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.GAMING),
    "chess.com": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.GAMING),

    # ── Entertainment — Movies ──────────────────────────────────────────
    "cineplex": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.MOVIES),
    "famous player": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.MOVIES),
    "famousplayers": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.MOVIES),
    "princess cinema": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.MOVIES),

    # ── Entertainment — Streaming ───────────────────────────────────────
    "netflix": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.STREAMING),
    "spotify": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.STREAMING),
    "disney": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.STREAMING),
    "twitch": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.STREAMING),

    # ── Entertainment — Activities/Venues ───────────────────────────────
    "dave & buster": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "wonderland": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "karaoke": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "ballroom bowl": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "swing zone": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "waveline": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "golf course": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "conservation": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "yuk yuk": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "looking glass adven": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),
    "niagara speedway": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.ACTIVITIES_AND_VENUES),

    # ── Entertainment — Events ──────────────────────────────────────────
    "ticketmaster": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.EVENTS),
    "see tickets": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.EVENTS),
    "axs.com": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.EVENTS),
    "saddledome": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.EVENTS),
    "scotiabank arena": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.EVENTS),
    "auto show": (TransactionCategory.ENTERTAINMENT, TransactionSubCategory.EVENTS),

    # ── Retail & Shopping — Alcohol ─────────────────────────────────────
    "lcbo": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ALCOHOL),
    "beerstore": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ALCOHOL),
    "beer store": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ALCOHOL),
    "wineshop": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ALCOHOL),
    "winerack": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ALCOHOL),

    # ── Retail & Shopping — Groceries ───────────────────────────────────
    "highlandfarms": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "highland farms": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "loblaws": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "zehrs": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "seafoodcity": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "gianttiger": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "nofrills": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "freshco": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "foodbasics": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "metro": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "sobeys": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "walmart": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "wal-mart": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "costco": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "longos": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "farm boy": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "farmboy": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "fortinos": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "whole foods": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "wholefoods": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),
    "t&t": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.GROCERIES),

    # ── Retail & Shopping — Clothing ────────────────────────────────────
    "frank and oak": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "frankandoak": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "roots": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "under armour": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "underarmour": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "banana republic": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "bananarepublic": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "club monaco": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "clubmonaco": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "aritzia": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "uniqlo": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "simons": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "winners": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),
    "sephora": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.CLOTHING),

    # ── Retail & Shopping — Electronics ─────────────────────────────────
    "bestbuy": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ELECTRONICS),
    "best buy": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ELECTRONICS),
    "canada computers": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ELECTRONICS),
    "canadacomputers": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ELECTRONICS),

    # ── Retail & Shopping — Online/General ──────────────────────────────
    "amazon": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.ONLINE_GENERAL),

    # ── Retail & Shopping — Dollar/Discount ─────────────────────────────
    "dollarama": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.DOLLAR_DISCOUNT),
    "value village": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.DOLLAR_DISCOUNT),
    "valuevillage": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.DOLLAR_DISCOUNT),

    # ── Retail & Shopping — Home ────────────────────────────────────────
    "ikea": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.HOME),
    "home depot": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.HOME),
    "homedepot": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.HOME),
    "michaels": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.HOME),

    # ── Retail & Shopping — Pet ─────────────────────────────────────────
    "petsmart": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.PET),
    "essential cat": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.PET),
    "essentialcat": (TransactionCategory.RETAIL_AND_SHOPPING, TransactionSubCategory.PET),

    # ── Retail & Shopping — no subcategory ──────────────────────────────
    "walmart": (TransactionCategory.RETAIL_AND_SHOPPING, None),
    "costco": (TransactionCategory.RETAIL_AND_SHOPPING, None),
    "indigo": (TransactionCategory.RETAIL_AND_SHOPPING, None),
    "canadian tire": (TransactionCategory.RETAIL_AND_SHOPPING, None),
    "canadiantire": (TransactionCategory.RETAIL_AND_SHOPPING, None),

    # ── Food & Dining — Coffee & Cafes ──────────────────────────────────
    "timhortons": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "tim hortons": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "starbucks": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "mathcoffee": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "danishpast": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "h3cafe": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "nespresso": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "kungfutea": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "cocofresh": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "propellercoffee": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "neocoffeebar": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "blackcanary": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),
    "mountainbrew": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.COFFEE_AND_CAFES),

    # ── Food & Dining — Fast Food ───────────────────────────────────────
    "mcdonald": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "pizzapizza": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "pizza pizza": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "pizza nova": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "subway": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "wendys": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "wendy's": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "burgerking": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "burger king": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "popeyes": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "kfc": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "harveys": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "marybrown": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "mary brown": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "dominos": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "a&w": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "little caesars": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "littlecaesars": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "jollibee": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "dairy queen": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "dairyqueen": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "chipotle": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "lazeez": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "osmow": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "shawerma": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "chungchun": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "jimmy the greek": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "jimmythegreek": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),
    "fast eddie": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.FAST_FOOD),

    # ── Food & Dining — Delivery (MUST come before generic "uber") ──────
    "doordash": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.DELIVERY),
    "ubereats": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.DELIVERY),
    "uber eats": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.DELIVERY),
    "skipthedishes": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.DELIVERY),
    "skip the dishes": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.DELIVERY),

    # ── Food & Dining — Convenience ─────────────────────────────────────
    "mac's": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.CONVENIENCE),
    "becker's": (TransactionCategory.FOOD_AND_DINING, TransactionSubCategory.CONVENIENCE),

    # ── Transportation — Gas & Fuel ─────────────────────────────────────
    "shell": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.GAS_AND_FUEL),
    "petro-canada": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.GAS_AND_FUEL),
    "petrocanada": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.GAS_AND_FUEL),
    "esso": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.GAS_AND_FUEL),
    "husky": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.GAS_AND_FUEL),

    # ── Transportation — Parking ────────────────────────────────────────
    "parking authority": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "parkingauthority": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "uw parking": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "honk parking": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "hangtag": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "park indigo": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "canada wide parking": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "target park": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "parking ticket": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "parking enforcement": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "world auto parking": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),
    "world car park": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.PARKING),

    # ── Transportation — Ride-hailing (after "ubereats" above) ──────────
    "uber": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.RIDE_HAILING),

    # ── Transportation — Auto Maintenance ───────────────────────────────
    "car wash": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.AUTO_MAINTENANCE),
    "carwash": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.AUTO_MAINTENANCE),
    "spot free": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.AUTO_MAINTENANCE),
    "muffler": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.AUTO_MAINTENANCE),
    "subaru": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.AUTO_MAINTENANCE),
    "motorama": (TransactionCategory.TRANSPORTATION, TransactionSubCategory.AUTO_MAINTENANCE),

    # ── Transportation — no subcategory ─────────────────────────────────
    "presto": (TransactionCategory.TRANSPORTATION, None),
    "compass": (TransactionCategory.TRANSPORTATION, None),
    "burlington go": (TransactionCategory.TRANSPORTATION, None),

    # ── Housing — Home Maintenance ──────────────────────────────────────
    "dependable mechanical": (TransactionCategory.HOUSING, TransactionSubCategory.HOME_MAINTENANCE),

    # ── Housing — no subcategory ────────────────────────────────────────
    "rent": (TransactionCategory.HOUSING, None),

    # ── Healthcare — Pharmacy (before generic "clinic") ─────────────────
    "shoppersdrug": (TransactionCategory.HEALTHCARE, TransactionSubCategory.PHARMACY),
    "shoppers drug": (TransactionCategory.HEALTHCARE, TransactionSubCategory.PHARMACY),
    "rexall": (TransactionCategory.HEALTHCARE, TransactionSubCategory.PHARMACY),
    "campus pharmacy": (TransactionCategory.HEALTHCARE, TransactionSubCategory.PHARMACY),

    # ── Healthcare — Physio & Rehab ─────────────────────────────────────
    "elevaterehab": (TransactionCategory.HEALTHCARE, TransactionSubCategory.PHYSIO_AND_REHAB),
    "elevate rehab": (TransactionCategory.HEALTHCARE, TransactionSubCategory.PHYSIO_AND_REHAB),
    "chiropractic": (TransactionCategory.HEALTHCARE, TransactionSubCategory.PHYSIO_AND_REHAB),

    # ── Healthcare — Optometry ──────────────────────────────────────────
    "optometric": (TransactionCategory.HEALTHCARE, TransactionSubCategory.OPTOMETRY),
    "eye star": (TransactionCategory.HEALTHCARE, TransactionSubCategory.OPTOMETRY),

    # ── Healthcare — Other (specific before generic "clinic") ───────────
    "animalclinic": (TransactionCategory.HEALTHCARE, TransactionSubCategory.OTHER),
    "animal clinic": (TransactionCategory.HEALTHCARE, TransactionSubCategory.OTHER),
    "veterinar": (TransactionCategory.HEALTHCARE, TransactionSubCategory.OTHER),
    "medavie": (TransactionCategory.HEALTHCARE, TransactionSubCategory.OTHER),
    "popeye's supplements": (TransactionCategory.HEALTHCARE, TransactionSubCategory.OTHER),

    # ── Healthcare — Medical (generic "clinic"/"hospital" last) ─────────
    "hospital": (TransactionCategory.HEALTHCARE, TransactionSubCategory.MEDICAL),
    "clinic": (TransactionCategory.HEALTHCARE, TransactionSubCategory.MEDICAL),
    "dental": (TransactionCategory.HEALTHCARE, TransactionSubCategory.MEDICAL),
    "pharmacy": (TransactionCategory.HEALTHCARE, TransactionSubCategory.PHARMACY),

    # ── Bills & Utilities — Phone Bill ──────────────────────────────────
    "rogers": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.PHONE_BILL),
    "bell canada": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.PHONE_BILL),
    "bellcanada": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.PHONE_BILL),
    "fido": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.PHONE_BILL),
    "koodo": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.PHONE_BILL),
    "telus": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.PHONE_BILL),

    # ── Bills & Utilities — Utilities ───────────────────────────────────
    "enbridge": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.UTILITIES),
    "hydro": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.UTILITIES),
    "wyse meter": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.UTILITIES),
    "wysemeter": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.UTILITIES),

    # ── Bills & Utilities — Insurance ───────────────────────────────────
    "scotia credit card protection": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.INSURANCE),
    "scotia sccp": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.INSURANCE),

    # ── Bills & Utilities — Loan Payments ───────────────────────────────
    "nslsc": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.LOAN_PAYMENTS),

    # ── Transfers ───────────────────────────────────────────────────────
    "interace-transfer": (TransactionCategory.TRANSFERS, None),
    "emailmoneytrf": (TransactionCategory.TRANSFERS, None),
    "freeinterace-transfer": (TransactionCategory.TRANSFERS, None),

    # ── Education ───────────────────────────────────────────────────────
    "universityofwaterloo": (TransactionCategory.EDUCATION, None),
    "brockuniversit": (TransactionCategory.EDUCATION, None),

    # ── Investment ──────────────────────────────────────────────────────
    "wealthsimpleinvestment": (TransactionCategory.INVESTMENT, None),
    "edwardjones": (TransactionCategory.INVESTMENT, None),

    # ── Personal Care ───────────────────────────────────────────────────
    "lifestylehair": (TransactionCategory.PERSONAL_CARE, None),
    "tiptoptailor": (TransactionCategory.PERSONAL_CARE, None),
    "barbershop": (TransactionCategory.PERSONAL_CARE, None),
    "barber": (TransactionCategory.PERSONAL_CARE, None),
}


# Description-based rules for Scotiabank chequing.
# The "description" field is the transaction type, not the merchant name.
# Values are (TransactionCategory, optional TransactionSubCategory).
DESCRIPTION_CATEGORY_RULES: Dict[str, tuple] = {
    "Payrolldep.": (TransactionCategory.INCOME, None),
    "Payrolldep": (TransactionCategory.INCOME, None),
    "Taxrefund": (TransactionCategory.INCOME, None),
    "GST": (TransactionCategory.INCOME, None),
    "ClimateActionIncentive": (TransactionCategory.INCOME, None),
    "CanadaCarbonRebate": (TransactionCategory.INCOME, None),
    "FederalPayment": (TransactionCategory.INCOME, None),
    "ProvincialPayment": (TransactionCategory.INCOME, None),
    "Health/dentalclaimins": (TransactionCategory.INCOME, None),
    "PSSuperannuation": (TransactionCategory.INCOME, None),
    "Investment": (TransactionCategory.INVESTMENT, None),
    # Wealthsimple activity types
    "Trade_BUY": (TransactionCategory.INVESTMENT, None),
    "Trade_SELL": (TransactionCategory.INVESTMENT, None),
    "BUY": (TransactionCategory.INVESTMENT, None),
    "SELL": (TransactionCategory.INVESTMENT, None),
    "DIV": (TransactionCategory.INVESTMENT, None),
    "DIVIDEND": (TransactionCategory.INVESTMENT, None),
    "CONT": (TransactionCategory.INVESTMENT, None),
    "CONTRIBUTION": (TransactionCategory.INVESTMENT, None),
    "WITHDRAW": (TransactionCategory.INVESTMENT, None),
    "WITHDRAWAL": (TransactionCategory.INVESTMENT, None),
    "FEE": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.BANK_FEES),
    "ABMwithdrawal": (TransactionCategory.TRANSFERS, None),
    "SharedABMwithdrawal": (TransactionCategory.TRANSFERS, None),
    "MB-Transferto": (TransactionCategory.TRANSFERS, None),
    "MB-Transferfrom": (TransactionCategory.TRANSFERS, None),
    "PCTransferto": (TransactionCategory.TRANSFERS, None),
    "PCTransferfrom": (TransactionCategory.TRANSFERS, None),
    "IOTransferto": (TransactionCategory.TRANSFERS, None),
    "IOTransferfrom": (TransactionCategory.TRANSFERS, None),
    "BRTransferfrom": (TransactionCategory.TRANSFERS, None),
    "CSTransferto": (TransactionCategory.TRANSFERS, None),
    "ABMtransferto": (TransactionCategory.TRANSFERS, None),
    "CreditCard/LOCpayment": (TransactionCategory.TRANSFERS, None),
    "Servicecharge": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.BANK_FEES),
    "INTERACABMfee": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.BANK_FEES),
    "Overdrawnhandling": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.BANK_FEES),
    "Overdraftinterest": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.BANK_FEES),
    "NSFchequecharge": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.BANK_FEES),
    "Customcheques": (TransactionCategory.BILLS_AND_UTILITIES, TransactionSubCategory.BANK_FEES),
}
