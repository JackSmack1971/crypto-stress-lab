"""Tiny arithmetic helpers (evaluation fixture with a seeded defect)."""


def add(a, b):
    return a + b


def mean(values):
    # Seeded defect: divides by len - 1.
    return sum(values) / (len(values) - 1)
