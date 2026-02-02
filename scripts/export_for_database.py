#!/usr/bin/env python3
"""
Export transaction data for database import.
Generates files for both Supabase (SQL/CSV) and Convex (JSON).
Supports multiple banks with bank_id foreign keys.
"""

import json
import csv
import uuid
from pathlib import Path
from datetime import datetime


def load_data(input_file: str = "output/all_statements_analysis.json") -> list:
    """Load the extracted statement data."""
    with open(input_file) as f:
        return json.load(f)


def generate_records(data: list, bank_name: str = "Scotiabank") -> tuple[dict, list, list]:
    """Generate bank, statement, and transaction records with UUIDs."""

    # Create bank record
    bank_id = str(uuid.uuid4())
    bank = {
        "id": bank_id,
        "name": bank_name,
        "account_type": "Chequing",  # Default, can be updated
        "account_number_masked": None,
        "currency": "CAD",
        "is_active": True,
    }

    statements = []
    transactions = []

    for r in data:
        if "error" in r:
            continue

        statement_id = str(uuid.uuid4())

        # Statement record
        statements.append({
            "id": statement_id,
            "bank_id": bank_id,
            "file_name": r["file"],
            "year": r["year"],
            "month": r["month"],
            "opening_balance": r["opening_balance"],
            "closing_balance": r["closing_balance"],
            "total_debits": r["total_debits"],
            "total_credits": r["total_credits"],
            "transaction_count": r["transaction_count"],
            "confidence": r["confidence"],
        })

        # Transaction records
        for t in r.get("transactions", []):
            transactions.append({
                "id": str(uuid.uuid4()),
                "bank_id": bank_id,
                "statement_id": statement_id,
                "date": t["date"],
                "description": t["description"],
                "amount": t["amount"],
                "balance": t["balance"],
                "transaction_type": t["transaction_type"],
                "store": t.get("store") or None,
                "location": t.get("location") or None,
                "category": t.get("category"),
                "raw_text": t.get("raw_text"),
            })

    return bank, statements, transactions


def export_supabase_sql(bank: dict, statements: list, transactions: list, output_dir: Path):
    """Generate SQL INSERT statements for Supabase."""
    sql_file = output_dir / "seed_data.sql"

    with open(sql_file, "w") as f:
        f.write("-- Supabase Seed Data\n")
        f.write("-- Generated: {}\n\n".format(datetime.now().isoformat()))

        # Insert bank
        f.write("-- Bank\n")
        account_type = f"'{bank['account_type']}'" if bank['account_type'] else "NULL"
        account_num = f"'{bank['account_number_masked']}'" if bank['account_number_masked'] else "NULL"
        f.write(f"""INSERT INTO banks (id, name, account_type, account_number_masked, currency, is_active)
VALUES ('{bank["id"]}', '{bank["name"]}', {account_type}, {account_num}, '{bank["currency"]}', {str(bank["is_active"]).lower()});\n\n""")

        # Insert statements
        f.write("-- Statements\n")
        for s in statements:
            f.write(f"""INSERT INTO statements (id, bank_id, file_name, year, month, opening_balance, closing_balance, total_debits, total_credits, transaction_count, confidence)
VALUES ('{s["id"]}', '{s["bank_id"]}', '{s["file_name"].replace("'", "''")}', {s["year"]}, {s["month"]}, {s["opening_balance"]}, {s["closing_balance"]}, {s["total_debits"]}, {s["total_credits"]}, {s["transaction_count"]}, {s["confidence"]});\n""")

        f.write("\n-- Transactions\n")
        for t in transactions:
            store = f"'{t['store'].replace(chr(39), chr(39)+chr(39))}'" if t["store"] else "NULL"
            location = f"'{t['location']}'" if t["location"] else "NULL"
            category = f"'{t['category']}'" if t["category"] else "NULL"
            raw_text = f"'{t['raw_text'].replace(chr(39), chr(39)+chr(39))}'" if t["raw_text"] else "NULL"

            f.write(f"""INSERT INTO transactions (id, bank_id, statement_id, date, description, amount, balance, transaction_type, store, location, category, raw_text)
VALUES ('{t["id"]}', '{t["bank_id"]}', '{t["statement_id"]}', '{t["date"]}', '{t["description"].replace("'", "''")}', {t["amount"]}, {t["balance"]}, '{t["transaction_type"]}', {store}, {location}, {category}, {raw_text});\n""")

    print(f"  Created: {sql_file}")


def export_supabase_csv(bank: dict, statements: list, transactions: list, output_dir: Path):
    """Generate CSV files for Supabase import."""
    # Banks CSV
    banks_csv = output_dir / "banks.csv"
    with open(banks_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=bank.keys())
        writer.writeheader()
        writer.writerow(bank)
    print(f"  Created: {banks_csv}")

    # Statements CSV
    statements_csv = output_dir / "statements.csv"
    with open(statements_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=statements[0].keys())
        writer.writeheader()
        writer.writerows(statements)
    print(f"  Created: {statements_csv}")

    # Transactions CSV
    transactions_csv = output_dir / "transactions.csv"
    with open(transactions_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
        writer.writeheader()
        writer.writerows(transactions)
    print(f"  Created: {transactions_csv}")


def export_convex_json(bank: dict, statements: list, transactions: list, output_dir: Path):
    """Generate JSON files formatted for Convex import."""
    # Bank (Convex uses camelCase)
    convex_bank = {
        "_id": bank["id"],
        "name": bank["name"],
        "accountType": bank["account_type"],
        "accountNumberMasked": bank["account_number_masked"],
        "currency": bank["currency"],
        "isActive": bank["is_active"],
    }

    bank_json = output_dir / "banks.json"
    with open(bank_json, "w") as f:
        json.dump([convex_bank], f, indent=2)
    print(f"  Created: {bank_json}")

    # Statements
    convex_statements = []
    for s in statements:
        convex_statements.append({
            "_id": s["id"],
            "_bankId": s["bank_id"],
            "fileName": s["file_name"],
            "year": s["year"],
            "month": s["month"],
            "openingBalance": s["opening_balance"],
            "closingBalance": s["closing_balance"],
            "totalDebits": s["total_debits"],
            "totalCredits": s["total_credits"],
            "transactionCount": s["transaction_count"],
            "confidence": s["confidence"],
        })

    statements_json = output_dir / "statements.json"
    with open(statements_json, "w") as f:
        json.dump(convex_statements, f, indent=2)
    print(f"  Created: {statements_json}")

    # Transactions
    convex_transactions = []
    for t in transactions:
        convex_transactions.append({
            "_id": t["id"],
            "_bankId": t["bank_id"],
            "_statementId": t["statement_id"],
            "date": t["date"],
            "description": t["description"],
            "amount": t["amount"],
            "balance": t["balance"],
            "transactionType": t["transaction_type"],
            "store": t["store"],
            "location": t["location"],
            "category": t["category"],
            "rawText": t["raw_text"],
        })

    transactions_json = output_dir / "transactions.json"
    with open(transactions_json, "w") as f:
        json.dump(convex_transactions, f, indent=2)
    print(f"  Created: {transactions_json}")


def export_convex_seed_script(output_dir: Path):
    """Generate a Convex seed mutation for importing data."""
    seed_file = output_dir / "seed.ts"

    content = '''/**
 * Convex Seed Script
 * Supports multiple banks with bank_id references
 */

import { mutation } from "./_generated/server";

import banksData from "./banks.json";
import statementsData from "./statements.json";
import transactionsData from "./transactions.json";

export const importData = mutation({
  args: {},
  handler: async (ctx) => {
    // Map old UUIDs to new Convex IDs
    const bankIdMap = new Map<string, string>();
    const statementIdMap = new Map<string, string>();

    // Import banks
    for (const b of banksData) {
      const id = await ctx.db.insert("banks", {
        name: b.name,
        accountType: b.accountType || undefined,
        accountNumberMasked: b.accountNumberMasked || undefined,
        currency: b.currency,
        isActive: b.isActive,
      });
      bankIdMap.set(b._id, id);
    }

    // Import statements
    for (const s of statementsData) {
      const bankId = bankIdMap.get(s._bankId);
      if (!bankId) {
        console.error(`Bank not found for statement: ${s._id}`);
        continue;
      }

      const id = await ctx.db.insert("statements", {
        bankId,
        fileName: s.fileName,
        year: s.year,
        month: s.month,
        openingBalance: s.openingBalance,
        closingBalance: s.closingBalance,
        totalDebits: s.totalDebits,
        totalCredits: s.totalCredits,
        transactionCount: s.transactionCount,
        confidence: s.confidence,
      });
      statementIdMap.set(s._id, id);
    }

    // Import transactions
    for (const t of transactionsData) {
      const bankId = bankIdMap.get(t._bankId);
      const statementId = statementIdMap.get(t._statementId);

      if (!bankId || !statementId) {
        console.error(`Missing reference for transaction: ${t._id}`);
        continue;
      }

      await ctx.db.insert("transactions", {
        bankId,
        statementId,
        date: t.date,
        description: t.description,
        amount: t.amount,
        balance: t.balance,
        transactionType: t.transactionType,
        store: t.store || undefined,
        location: t.location || undefined,
        category: t.category || undefined,
        rawText: t.rawText || undefined,
      });
    }

    return {
      banks: banksData.length,
      statements: statementsData.length,
      transactions: transactionsData.length,
    };
  },
});
'''

    with open(seed_file, "w") as f:
        f.write(content)
    print(f"  Created: {seed_file}")


def main():
    print("=" * 60)
    print("DATABASE EXPORT")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    data = load_data()
    print(f"  Loaded {len(data)} statements")

    # Generate normalized records with UUIDs
    print("\nGenerating records...")
    bank, statements, transactions = generate_records(data, bank_name="Scotiabank")
    print(f"  1 bank: {bank['name']}")
    print(f"  {len(statements)} statements")
    print(f"  {len(transactions)} transactions")

    # Create output directories
    supabase_dir = Path("database/supabase")
    convex_dir = Path("database/convex")
    supabase_dir.mkdir(parents=True, exist_ok=True)
    convex_dir.mkdir(parents=True, exist_ok=True)

    # Export for Supabase
    print("\nExporting for Supabase...")
    export_supabase_sql(bank, statements, transactions, supabase_dir)
    export_supabase_csv(bank, statements, transactions, supabase_dir)

    # Export for Convex
    print("\nExporting for Convex...")
    export_convex_json(bank, statements, transactions, convex_dir)
    export_convex_seed_script(convex_dir)

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print("\nSupabase files:")
    print("  database/supabase/schema.sql    - Run first to create tables")
    print("  database/supabase/seed_data.sql - Run to insert data")
    print("  database/supabase/banks.csv     - Import via UI (order: banks first)")
    print("  database/supabase/statements.csv")
    print("  database/supabase/transactions.csv")
    print("\nConvex files (for future migration):")
    print("  database/convex/schema.ts       - Copy to convex/schema.ts")
    print("  database/convex/banks.json      - Data to import")
    print("  database/convex/statements.json")
    print("  database/convex/transactions.json")
    print("  database/convex/seed.ts         - Copy to convex/seed.ts")


if __name__ == "__main__":
    main()
