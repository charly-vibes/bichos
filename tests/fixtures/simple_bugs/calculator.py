"""Simple calculator module.

BUG #1: Division by zero not handled — divide() raises ZeroDivisionError
when denominator is 0 instead of returning a meaningful value or raising
a custom exception with a clear message.
"""


def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    # BUG: no guard for b == 0
    return a / b


def power(base: float, exp: int) -> float:
    result = 1.0
    for _ in range(exp):
        result *= base
    return result
