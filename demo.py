#!/usr/bin/env python3
"""Quick demo of the bank system."""

from bank import Bank

b = Bank("Arjun Mini Bank")
me = b.open_account("Arjun Singh", "1234", opening=1000)
you = b.open_account("Peer Dev", "5678", opening=200)
b.transfer(me.number, you.number, 150, "1234")
print("me", me.number, me.balance)
print("you", you.number, you.balance)
print("statement:")
for row in b.statement(me.number, "1234"):
    print(" ", row)
