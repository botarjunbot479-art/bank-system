"""Tests for Arjun Mini Bank."""

from bank import Bank, BankError


def test_open_deposit_withdraw_transfer():
    b = Bank()
    a = b.open_account("Arjun", "1234", opening=100)
    c = b.open_account("Friend", "9999")
    a.deposit(50)
    a.withdraw(20, "1234")
    b.transfer(a.number, c.number, 30, "1234")
    assert a.balance == 100
    assert c.balance == 30
    assert len(a.history) >= 3


def test_bad_pin_and_overdraft():
    b = Bank()
    a = b.open_account("Arjun", "1234", opening=10)
    try:
        a.withdraw(5, "0000")
        assert False, "should fail pin"
    except BankError:
        pass
    try:
        a.withdraw(999, "1234")
        assert False, "should fail funds"
    except BankError:
        pass
