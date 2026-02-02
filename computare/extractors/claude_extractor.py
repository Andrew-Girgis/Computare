"""
Claude AI-based PDF extraction - fallback for complex cases.
Uses Claude's native PDF support for high accuracy extraction.
"""

import base64
import json
import re
from pathlib import Path
from typing import List, Optional
from datetime import date, datetime

import anthropic

from .base import BaseExtractor
from ..models import (
    Transaction, TransactionType, ExtractionResult,
    StatementMetadata, ExtractionMethod
)
from ..config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, DEFAULT_YEAR


class ClaudeExtractor(BaseExtractor):
    """
    Extracts transactions using Claude's PDF vision capabilities.
    More expensive but handles complex layouts and edge cases.
    """

    EXTRACTION_PROMPT = """Extract ALL transactions from this bank statement PDF.

Return a JSON object with this exact structure:
{
  "bank": "bank name",
  "account_type": "account type if visible",
  "opening_balance": 1234.56 or null,
  "closing_balance": 1234.56 or null,
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "description": "transaction description/type",
      "amount": -123.45,
      "balance": 1234.56,
      "store": "merchant name if visible",
      "location": "location code if visible (e.g., ONCA)"
    }
  ]
}

CRITICAL RULES:
1. Include EVERY transaction - do not skip any
2. amount is NEGATIVE for withdrawals/purchases/debits
3. amount is POSITIVE for deposits/credits
4. Parse dates as YYYY-MM-DD (infer year from statement date if needed)
5. Remove $ and commas from amounts before converting to numbers
6. The balance should be the running balance AFTER the transaction
7. Return ONLY valid JSON, no markdown code blocks or explanation text

Statement year hint: {year}"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Anthropic API key."""
        self.api_key = api_key or ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def can_handle(self, pdf_path: str | Path) -> bool:
        """Claude can handle any PDF within size limits."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return False

        # Check file size (Claude limit is 32MB)
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        return size_mb <= 32

    def extract(self, pdf_path: str | Path, year: Optional[int] = None) -> ExtractionResult:
        """Extract transactions using Claude API."""
        pdf_path = Path(pdf_path)
        year = year or self._detect_year_from_filename(pdf_path.name) or DEFAULT_YEAR

        # Read and encode PDF
        with open(pdf_path, "rb") as f:
            pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Call Claude API
        prompt = self.EXTRACTION_PROMPT.format(year=year)

        try:
            message = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_data
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            # Parse response
            response_text = message.content[0].text
            data = self._parse_json_response(response_text)

            # Convert to Transaction objects
            transactions = self._convert_to_transactions(data.get("transactions", []))

            # Build metadata
            metadata = StatementMetadata(
                bank=data.get("bank", "unknown"),
                account_type=data.get("account_type", ""),
                opening_balance=data.get("opening_balance"),
                closing_balance=data.get("closing_balance")
            )

            return ExtractionResult(
                transactions=transactions,
                metadata=metadata,
                extraction_method=ExtractionMethod.CLAUDE_AI,
                confidence_score=0.95,  # Claude is generally high accuracy
                source_file=str(pdf_path)
            )

        except anthropic.APIError as e:
            return ExtractionResult(
                transactions=[],
                metadata=StatementMetadata(bank="unknown"),
                extraction_method=ExtractionMethod.CLAUDE_AI,
                confidence_score=0.0,
                validation_errors=[f"API Error: {str(e)}"],
                source_file=str(pdf_path)
            )

    def _detect_year_from_filename(self, filename: str) -> Optional[int]:
        """Try to detect year from filename."""
        match = re.search(r'20\d{2}', filename)
        if match:
            return int(match.group())
        return None

    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from Claude's response, handling markdown code blocks."""
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```"):
            # Find the first newline after ``` to skip language identifier
            first_newline = response.find('\n')
            if first_newline != -1:
                response = response[first_newline + 1:]

            # Remove closing ```
            if response.endswith("```"):
                response = response[:-3]

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Try to find JSON object in response
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                try:
                    return json.loads(response[start:end + 1])
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"Failed to parse JSON response: {e}")

    def _convert_to_transactions(self, raw_transactions: List[dict]) -> List[Transaction]:
        """Convert raw JSON transactions to Transaction objects."""
        transactions = []

        for raw in raw_transactions:
            try:
                # Parse date
                date_str = raw.get("date", "")
                if isinstance(date_str, str):
                    trans_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    continue

                # Parse amount
                amount = raw.get("amount", 0)
                if isinstance(amount, str):
                    amount = float(amount.replace(',', '').replace('$', ''))

                # Parse balance
                balance = raw.get("balance", 0)
                if isinstance(balance, str):
                    balance = float(balance.replace(',', '').replace('$', ''))

                # Determine transaction type
                if amount < 0:
                    trans_type = TransactionType.DEBIT
                elif amount > 0:
                    trans_type = TransactionType.CREDIT
                else:
                    trans_type = TransactionType.UNKNOWN

                transaction = Transaction(
                    date=trans_date,
                    description=raw.get("description", ""),
                    amount=float(amount),
                    balance=float(balance),
                    transaction_type=trans_type,
                    store=raw.get("store", ""),
                    location=raw.get("location", ""),
                    raw_text=json.dumps(raw)
                )
                transactions.append(transaction)

            except (ValueError, KeyError) as e:
                # Skip malformed transactions but log the error
                print(f"Warning: Could not parse transaction: {raw}, error: {e}")
                continue

        return transactions
