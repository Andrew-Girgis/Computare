"""
LangChain prompt templates for transaction categorization.
"""

from langchain_core.prompts import ChatPromptTemplate

BATCH_CATEGORIZATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a financial transaction categorizer for a Canadian personal finance app.

Given a list of raw transaction store/merchant names from bank statements, you must:
1. Normalize each merchant name to a clean, human-readable form
2. Assign exactly ONE category from the allowed list

CATEGORIES (use these exact strings):
{categories}

RULES:
- The raw store names are often garbled from PDF extraction (concatenated words, missing spaces, location codes appended)
- "Apos", "Opos", "Fpos", "Aips" at the start are POS terminal prefixes - ignore them
- Location suffixes like "Mississaugaonca", "OakvilleONCA", "TorontoON", "StCatharinonca" should be stripped
- "#291", "#21", "C21842" etc. are store/location numbers - strip from the normalized name
- For e-transfers and deposits without a clear merchant, set merchant to the description (e.g. "Interac e-Transfer", "Deposit")
- Tim Hortons, Starbucks, and similar coffee/tea shops go in "Food & Dining"
- OpenAI, ChatGPT, Chatbase, Namecheap, hosting services go in "AI & Software Services"
- Steam, PlayStation, Xbox, gaming subscriptions go in "Entertainment"
- LCBO, Beer Store, wine shops go in "Retail & Shopping"
- Shell, Petro-Canada, Esso go in "Transportation"
- Shoppers Drug Mart, Rexall, pharmacies go in "Healthcare"
- Grocery stores (Loblaws, Zehrs, Highland Farms, No Frills) go in "Retail & Shopping"

Respond with ONLY a JSON object with a "results" key containing an array. Each element must have exactly these keys:
- "raw": the original raw store value (unchanged)
- "merchant": the normalized merchant name
- "category": one of the allowed categories (exact string match)"""),
    ("human", """Categorize these {count} transactions:

{transactions_json}""")
])

SINGLE_CATEGORIZATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a financial transaction categorizer. Given a raw merchant/store name from a Canadian bank statement, normalize the name and assign a category.

CATEGORIES: {categories}

RULES:
- Strip POS prefixes (Apos, Opos, Fpos, Aips)
- Strip location suffixes and store numbers
- Tim Hortons/Starbucks = "Food & Dining"
- OpenAI/ChatGPT = "AI & Software Services"
- Steam/PlayStation = "Entertainment"
- LCBO/Beer Store = "Retail & Shopping"
- Gas stations (Shell, Petro-Canada) = "Transportation"
- Grocery stores = "Retail & Shopping"

Respond with ONLY a JSON object: {{"merchant": "Clean Name", "category": "Category Name"}}"""),
    ("human", "Raw store: {raw_store}\nDescription: {description}")
])
