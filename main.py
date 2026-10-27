#!/usr/bin/env python3
"""CLI for Arjun Mini Bank."""

from __future__ import annotations

import argparse
from pathlib import Path

from bank import Bank, BankError

DB = Path(__file__).resolve().parent / "bank_data.json"


def load() -> Bank:
    return Bank.load(DB) if DB.exists() else Bank()


def save(bank: Bank) -> None:
    bank.save(DB)


def main() -> int:
    p = argparse.ArgumentParser(description="Arjun Mini Bank")
    sub = p.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("open", help="Open account")
    o.add_argument("--name", required=True)
    o.add_argument("--pin", required=True)
    o.add_argument("--opening", type=float, default=0)

    d = sub.add_parser("deposit")
    d.add_argument("--account", required=True)
    d.add_argument("--amount", type=float, required=True)

    w = sub.add_parser("withdraw")
    w.add_argument("--account", required=True)
    w.add_argument("--amount", type=float, required=True)
    w.add_argument("--pin", required=True)

    t = sub.add_parser("transfer")
    t.add_argument("--from", dest="src", required=True)
    t.add_argument("--to", dest="dst", required=True)
    t.add_argument("--amount", type=float, required=True)
    t.add_argument("--pin", required=True)

    s = sub.add_parser("statement")
    s.add_argument("--account", required=True)
    s.add_argument("--pin", required=True)

    b = sub.add_parser("balance")
    b.add_argument("--account", required=True)
    b.add_argument("--pin", required=True)

    args = p.parse_args()
    bank = load()
    try:
        if args.cmd == "open":
            acc = bank.open_account(args.name, args.pin, args.opening)
            save(bank)
            print(f"opened {acc.number} for {acc.name} bal={acc.balance}")
        elif args.cmd == "deposit":
            txn = bank.get(args.account).deposit(args.amount)
            save(bank)
            print(txn)
        elif args.cmd == "withdraw":
            txn = bank.get(args.account).withdraw(args.amount, args.pin)
            save(bank)
            print(txn)
        elif args.cmd == "transfer":
            out, inn = bank.transfer(args.src, args.dst, args.amount, args.pin)
            save(bank)
            print(out)
            print(inn)
        elif args.cmd == "statement":
            for row in bank.statement(args.account, args.pin):
                print(row)
        elif args.cmd == "balance":
            acc = bank.get(args.account)
            acc._check_pin(args.pin)
            print(f"{acc.number} {acc.name} bal={acc.balance}")
    except BankError as e:
        print(f"error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
