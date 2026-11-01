"""In-memory user store (evaluation fixture)."""

USERS = {"ada": {"name": "ada", "admin": True}, "bob": {"name": "bob", "admin": False}}
PAGE_SIZE = 2


def get_user(name):
    if not isinstance(name, str) or not name:
        raise ValueError("name must be a non-empty string")
    return USERS.get(name)


def page(items, number):
    if number < 1:
        raise ValueError("page numbers start at 1")
    start = (number - 1) * PAGE_SIZE
    return items[start:start + PAGE_SIZE]
