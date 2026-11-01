"""Tiny arithmetic helpers (evaluation fixture)."""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def divide(a, b):
    return a / b


def mean(values):
    return sum(values) / len(values)
