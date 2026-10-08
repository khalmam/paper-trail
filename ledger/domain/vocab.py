"""Single source of truth for fixed vocabularies (also used to constrain LLM output later)."""
from typing import Literal, get_args

Category = Literal["leak", "mold", "heating", "pests", "structural", "electrical", "other"]
CATEGORIES: tuple[str, ...] = get_args(Category)

ContactMethod = Literal["call", "text", "email", "in_person", "letter"]
CONTACT_METHODS: tuple[str, ...] = get_args(ContactMethod)
