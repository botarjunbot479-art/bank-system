"""Core banking domain — accounts, ledger, transfers."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BankError(Exception):
    pass


@dataclass
class Txn:
    id: str
    kind: str
    amount: float
    balance_after: float
    note: str
    at: str
    counterparty: Optional[str] = None


@dataclass
class Account:
    number: str
    name: str
    pin: str
    balance: float = 0.0
    history: list = field(default_factory=list)

    def _check_pin(self, pin: str) -> None:
        if pin != self.pin:
            raise BankError("invalid PIN")

    def deposit(self, amount: float, note: str = "deposit") -> Txn:
        if amount <= 0:
            raise BankError("amount must be positive")
        self.balance = round(self.balance + amount, 2)
        txn = Txn(str(uuid.uuid4())[:8], "deposit", amount, self.balance, note, utc_now())
        self.history.append(asdict(txn))
        return txn

    def withdraw(self, amount: float, pin: str, note: str = "withdraw") -> Txn:
        self._check_pin(pin)
        if amount <= 0:
            raise BankError("amount must be positive")
        if amount > self.balance:
            raise BankError("insufficient funds")
        self.balance = round(self.balance - amount, 2)
        txn = Txn(str(uuid.uuid4())[:8], "withdraw", amount, self.balance, note, utc_now())
        self.history.append(asdict(txn))
        return txn


class Bank:
    def __init__(self, name: str = "Arjun Mini Bank") -> None:
        self.name = name
        self.accounts: dict[str, Account] = {}

    def open_account(self, name: str, pin: str, opening: float = 0.0) -> Account:
        if not name or len(pin) < 4:
            raise BankError("name required and PIN must be 4+ digits")
        number = f"ARJ-{1000 + len(self.accounts) + 1}"
        acc = Account(number=number, name=name, pin=pin, balance=0.0)
        if opening:
            acc.deposit(opening, note="opening balance")
        self.accounts[number] = acc
        return acc

    def get(self, number: str) -> Account:
        if number not in self.accounts:
            raise BankError("account not found")
        return self.accounts[number]

    def transfer(self, src: str, dst: str, amount: float, pin: str) -> tuple[Txn, Txn]:
        a = self.get(src)
        b = self.get(dst)
        a._check_pin(pin)
        if amount <= 0:
            raise BankError("amount must be positive")
        if amount > a.balance:
            raise BankError("insufficient funds")
        a.balance = round(a.balance - amount, 2)
        b.balance = round(b.balance + amount, 2)
        out = Txn(str(uuid.uuid4())[:8], "transfer_out", amount, a.balance, f"to {dst}", utc_now(), dst)
        inn = Txn(str(uuid.uuid4())[:8], "transfer_in", amount, b.balance, f"from {src}", utc_now(), src)
        a.history.append(asdict(out))
        b.history.append(asdict(inn))
        return out, inn

    def statement(self, number: str, pin: str) -> list[dict]:
        acc = self.get(number)
        acc._check_pin(pin)
        return list(acc.history)

    def save(self, path: str | Path) -> None:
        data = {
            "name": self.name,
            "accounts": {
                n: {
                    "number": a.number,
                    "name": a.name,
                    "pin": a.pin,
                    "balance": a.balance,
                    "history": a.history,
                }
                for n, a in self.accounts.items()
            },
        }
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Bank":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        bank = cls(data.get("name") or "Arjun Mini Bank")
        for n, raw in (data.get("accounts") or {}).items():
            bank.accounts[n] = Account(
                number=raw["number"],
                name=raw["name"],
                pin=raw["pin"],
                balance=float(raw.get("balance") or 0),
                history=list(raw.get("history") or []),
            )
        return bank
