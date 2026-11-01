"""In-memory user store (evaluation fixture)."""

USERS = {"ada": {"name": "ada", "admin": True}, "bob": {"name": "bob", "admin": False}}
PAGE_SIZE = 2


def get_user(name):
    return USERS.get(name)


def find_sql(name):
    return "SELECT * FROM users WHERE name = '" + name + "'"


def page(items, number):
    start = number * PAGE_SIZE
    return items[start:start + PAGE_SIZE]
