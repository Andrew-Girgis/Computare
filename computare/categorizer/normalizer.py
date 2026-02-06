"""
Merchant name normalization for Computare.

Transforms raw POS strings into clean, human-readable merchant names.

Examples:
    "EasyPayShell1038489281*"           → "Shell"
    "FposStarbucks#16144#Mississaugaoncd" → "Starbucks"
    "LOBLAWS 10908* MISSISSAUGAONCA"    → "Loblaws"
    "AposMcdonald'S#291Mississaugaonca" → "McDonald's"
"""

import re
from typing import Optional


# Canonical display names for known merchants.
# Keys are lowercase keywords found in KNOWN_MERCHANT_HINTS.
# Values are the proper display name with correct capitalization.
CANONICAL_MERCHANT_NAMES = {
    # AI & Software
    "openai": "OpenAI",
    "chatgpt": "ChatGPT",
    "chatbase": "Chatbase",
    "openrouter": "OpenRouter",
    "cal.com": "Cal.com",
    "namecheap": "Namecheap",
    "github": "GitHub",
    "railway": "Railway",
    "anthropic": "Anthropic",
    "perplexity": "Perplexity",
    "cursor": "Cursor",
    "vercel": "Vercel",
    "supabase": "Supabase",

    # Entertainment - Gaming
    "steamgames": "Steam",
    "playstation": "PlayStation",
    "sonyinteractive": "PlayStation",
    "kingsisle": "KingsIsle",
    "wizard101": "Wizard101",
    "riotgames": "Riot Games",
    "chess.com": "Chess.com",

    # Entertainment - Movies
    "cineplex": "Cineplex",
    "famous player": "Famous Players",
    "famousplayers": "Famous Players",
    "princess cinema": "Princess Cinema",

    # Entertainment - Streaming
    "netflix": "Netflix",
    "spotify": "Spotify",
    "disney": "Disney+",
    "twitch": "Twitch",
    "apple.com": "Apple",
    "youtube": "YouTube",
    "primevideo": "Amazon Prime Video",

    # Entertainment - Activities
    "dave & buster": "Dave & Buster's",
    "wonderland": "Canada's Wonderland",
    "karaoke": "Karaoke",
    "ballroom bowl": "Ballroom Bowl",

    # Retail - Alcohol
    "lcbo": "LCBO",
    "beerstore": "The Beer Store",
    "beer store": "The Beer Store",

    # Retail - Groceries
    "highlandfarms": "Highland Farms",
    "highland farms": "Highland Farms",
    "loblaws": "Loblaws",
    "zehrs": "Zehrs",
    "seafoodcity": "Seafood City",
    "gianttiger": "Giant Tiger",
    "nofrills": "No Frills",
    "freshco": "FreshCo",
    "foodbasics": "Food Basics",
    "walmart": "Walmart",
    "wal-mart": "Walmart",
    "costco": "Costco",
    "t&t": "T&T Supermarket",
    "metro": "Metro",
    "sobeys": "Sobeys",
    "farm boy": "Farm Boy",
    "farmboy": "Farm Boy",
    "whole foods": "Whole Foods",
    "wholefoods": "Whole Foods",
    "fortinos": "Fortinos",
    "longos": "Longos",

    # Retail - Clothing
    "frank and oak": "Frank and Oak",
    "frankandoak": "Frank and Oak",
    "roots": "Roots",
    "under armour": "Under Armour",
    "underarmour": "Under Armour",
    "banana republic": "Banana Republic",
    "bananarepublic": "Banana Republic",
    "club monaco": "Club Monaco",
    "clubmonaco": "Club Monaco",
    "aritzia": "Aritzia",
    "uniqlo": "Uniqlo",
    "simons": "Simons",
    "winners": "Winners",
    "sephora": "Sephora",
    "h&m": "H&M",
    "old navy": "Old Navy",
    "oldnavy": "Old Navy",
    "gap": "Gap",

    # Retail - Electronics
    "best buy": "Best Buy",
    "bestbuy": "Best Buy",
    "apple store": "Apple Store",
    "memoryexpress": "Memory Express",
    "canadacomputers": "Canada Computers",
    "canada computers": "Canada Computers",

    # Retail - Online/General
    "amazon": "Amazon",
    "amzn": "Amazon",

    # Retail - Dollar/Discount
    "dollarama": "Dollarama",
    "dollar tree": "Dollar Tree",
    "dollartree": "Dollar Tree",

    # Retail - Home
    "ikea": "IKEA",
    "homesense": "HomeSense",
    "home depot": "Home Depot",
    "homedepot": "Home Depot",
    "canadian tire": "Canadian Tire",
    "canadiantire": "Canadian Tire",
    "lowes": "Lowe's",
    "structube": "Structube",
    "wayfair": "Wayfair",

    # Retail - Pet
    "petsmart": "PetSmart",
    "pet valu": "Pet Valu",
    "petvalu": "Pet Valu",

    # Food & Dining - Coffee
    "starbucks": "Starbucks",
    "tim horton": "Tim Hortons",
    "timhorton": "Tim Hortons",
    "second cup": "Second Cup",
    "secondcup": "Second Cup",
    "balzac": "Balzac's",

    # Food & Dining - Fast Food
    "mcdonald": "McDonald's",
    "subway": "Subway",
    "wendys": "Wendy's",
    "wendy's": "Wendy's",
    "burger king": "Burger King",
    "burgerking": "Burger King",
    "popeyes": "Popeyes",
    "kfc": "KFC",
    "taco bell": "Taco Bell",
    "tacobell": "Taco Bell",
    "harveys": "Harvey's",
    "harvey's": "Harvey's",
    "a&w": "A&W",
    "five guys": "Five Guys",
    "fiveguys": "Five Guys",
    "chipotle": "Chipotle",
    "pizza hut": "Pizza Hut",
    "pizzahut": "Pizza Hut",
    "little caesars": "Little Caesars",
    "littlecaesars": "Little Caesars",
    "domino": "Domino's",
    "panera": "Panera Bread",

    # Food & Dining - Delivery
    "ubereats": "Uber Eats",
    "uber eats": "Uber Eats",
    "doordash": "DoorDash",
    "skip the dishes": "SkipTheDishes",
    "skipthedishes": "SkipTheDishes",
    "instacart": "Instacart",

    # Food & Dining - Convenience
    "7-eleven": "7-Eleven",
    "7eleven": "7-Eleven",
    "circle k": "Circle K",
    "circlek": "Circle K",

    # Transportation - Gas
    "shell": "Shell",
    "esso": "Esso",
    "petro-canada": "Petro-Canada",
    "petrocanada": "Petro-Canada",
    "petro canada": "Petro-Canada",
    "canadian tire gas": "Canadian Tire Gas",
    "mobil": "Mobil",
    "pioneer": "Pioneer",
    "ultramar": "Ultramar",
    "chevron": "Chevron",

    # Transportation - Ride-hailing
    "uber": "Uber",
    "lyft": "Lyft",

    # Transportation - Parking
    "impark": "Impark",
    "indigo": "Indigo Parking",
    "green p": "Green P",
    "greenp": "Green P",

    # Transportation - Transit
    "presto": "PRESTO",
    "go transit": "GO Transit",
    "gotransit": "GO Transit",
    "ttc": "TTC",
    "metrolinx": "Metrolinx",

    # Bills & Utilities
    "rogers": "Rogers",
    "bell": "Bell",
    "telus": "Telus",
    "fido": "Fido",
    "koodo": "Koodo",
    "freedom mobile": "Freedom Mobile",
    "freedommobile": "Freedom Mobile",
    "virgin mobile": "Virgin Mobile",
    "virginmobile": "Virgin Mobile",
    "hydro one": "Hydro One",
    "hydroone": "Hydro One",
    "enbridge": "Enbridge",
    "alectra": "Alectra",

    # Healthcare
    "shoppers drug": "Shoppers Drug Mart",
    "shoppersdrugmart": "Shoppers Drug Mart",
    "rexall": "Rexall",
    "pharmasave": "Pharmasave",
    "london drugs": "London Drugs",
    "londondrugs": "London Drugs",
    "lifelabs": "LifeLabs",
    "dynacare": "Dynacare",

    # Financial
    "wealthsimple": "Wealthsimple",
    "questrade": "Questrade",
    "interac e-transfer": "Interac e-Transfer",
    "interace-transfer": "Interac e-Transfer",
    "etransfer": "Interac e-Transfer",
}


def normalize_merchant(raw_store: str) -> str:
    """
    Normalize a raw store/merchant string to a clean, human-readable name.

    Performs two-phase normalization:
    1. Clean the string by removing POS prefixes, location codes, etc.
    2. Match against known merchant names for proper capitalization.

    Args:
        raw_store: Raw merchant string from statement (e.g., "EasyPayShell1038489281*")

    Returns:
        Normalized merchant name (e.g., "Shell")

    Examples:
        >>> normalize_merchant("EasyPayShell1038489281*")
        "Shell"
        >>> normalize_merchant("FposStarbucks#16144#Mississaugaoncd")
        "Starbucks"
        >>> normalize_merchant("LOBLAWS 10908* MISSISSAUGAONCA")
        "Loblaws"
        >>> normalize_merchant("AposMcdonald'S#291Mississaugaonca")
        "McDonald's"
    """
    if not raw_store:
        return ""

    # Phase 1: Clean the string
    cleaned = _clean_raw_string(raw_store)

    # Phase 2: Match against known merchants for canonical name
    canonical = _match_canonical_name(cleaned)
    if canonical:
        return canonical

    # Fallback: Title-case the cleaned string
    return _title_case_fallback(cleaned)


def _clean_raw_string(s: str) -> str:
    """
    Remove noise from raw merchant strings.

    Strips POS prefixes, account numbers, phone numbers, store numbers,
    location codes, and normalizes whitespace.
    """
    original = s
    s = s.strip()

    # Remove "Pre-authorized Debit to " prefix
    s = re.sub(r"(?i)^pre-?authorized\s+debit\s+to\s+", "", s)

    # Remove POS prefixes (Fpos, Opos, Apos, Aips, CS*)
    s = re.sub(r"(?i)^[FOAI]pos\s*", "", s)
    s = re.sub(r"(?i)^CS\*\s*", "", s)
    s = re.sub(r"(?i)^[OA]pos", "", s)  # Handle OposMcdonald's without space

    # Remove EasyPay prefix (but preserve Shell, Esso after)
    s = re.sub(r"(?i)^easypay\s*", "", s)

    # Remove /BILL suffix (APPLE.COM/BILL)
    s = re.sub(r"/BILL$", "", s, flags=re.IGNORECASE)

    # Remove masked account numbers (******2820, ****5080, *51001)
    s = re.sub(r"\*{1,}\d+\*?", "", s)

    # Remove phone numbers (888-764-3771, 800-3457669, 877-850-197)
    s = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "", s)
    s = re.sub(r"\b\d{10,}\b", "", s)

    # Remove store/location numbers (#16144, #291, C21842)
    s = re.sub(r"#\d+#?", "", s)
    s = re.sub(r"\bC\d{4,}\b", "", s)
    s = re.sub(r"\s+\d{4,}\s*", " ", s)  # Standalone numbers like "10908"

    # Remove reference numbers at start (e.g. "14272353FreeInterac...")
    s = re.sub(r"^\d{6,}", "", s)

    # Remove Canadian city names (commonly appended to merchant)
    cities = (
        r"Mississaug|Toronto|Oakville|Waterloo|Hamilton|Cambridge|"
        r"Brantford|Orillia|Milton|Calgary|Vancouver|London|Ottawa|"
        r"StCatharin|Kitchener|Brampton|Markham|Vaughan|Richmond|"
        r"Scarborough|Etobicoke|NorthYork|EastYork"
    )
    s = re.sub(rf"\s*({cities})\w*$", "", s, flags=re.IGNORECASE)
    s = re.sub(rf"({cities})\w*$", "", s, flags=re.IGNORECASE)  # No space

    # Remove Canadian province/country suffixes
    s = re.sub(
        r"\s*(ON|BC|AB|QC|MB|SK|NS|NB|PE|NL|NT|YT|NU)(\s*CA)?\s*$",
        "", s, flags=re.IGNORECASE
    )
    s = re.sub(r"\s*(onca|oncd|caus|bcca|abca|abcd)\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+(CA|US)\s*$", "", s, flags=re.IGNORECASE)

    # Remove "GC" suffix (gift card identifiers like "StarbucksGc")
    s = re.sub(r"Gc\s*$", "", s, flags=re.IGNORECASE)

    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()

    # If empty after cleanup, return cleaned original (just whitespace normalized)
    if not s:
        return re.sub(r"\s+", " ", original).strip()

    return s


def _match_canonical_name(cleaned: str) -> Optional[str]:
    """
    Match cleaned string against known merchant names.

    Returns the canonical display name if found, None otherwise.
    """
    cleaned_lower = cleaned.lower()

    # Direct match first
    if cleaned_lower in CANONICAL_MERCHANT_NAMES:
        return CANONICAL_MERCHANT_NAMES[cleaned_lower]

    # Substring match (longer keywords first for specificity)
    for keyword in sorted(CANONICAL_MERCHANT_NAMES.keys(), key=len, reverse=True):
        if keyword in cleaned_lower:
            return CANONICAL_MERCHANT_NAMES[keyword]

    return None


def _title_case_fallback(s: str) -> str:
    """
    Convert string to title case with special handling for common patterns.
    """
    # Handle camelCase by inserting spaces
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)

    # Handle all-caps words
    words = s.split()
    result = []
    for word in words:
        if word.isupper() and len(word) > 2:
            # Convert LOBLAWS to Loblaws
            result.append(word.capitalize())
        elif word.islower():
            result.append(word.capitalize())
        else:
            result.append(word)

    return " ".join(result)


def extract_merchant_key(raw_store: str) -> str:
    """
    Extract a stable key for grouping/caching purposes.

    Returns lowercase version of normalized merchant for use as cache key.
    This ensures "Shell", "SHELL", and "shell" all map to the same key.
    """
    normalized = normalize_merchant(raw_store)
    return normalized.lower()
