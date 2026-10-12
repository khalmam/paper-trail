"""Hand-written parsing cases: (utterance, room, category, days_ago, question_must_contain).
The same list should later be run against the Bedrock parser."""
CASES = [
    ("the ceiling in the bedroom is leaking again", "bedroom", "leak", None, None),
    ("there are ants in the kitchen", "kitchen", "pests", None, None),
    ("mold on the bathroom wall since yesterday", "bathroom", "mold", 1, None),
    ("the heater in the living room stopped working 3 days ago", "living room", "heating", 3, None),
    ("sparks from the socket in the hallway", "hallway", "electrical", None, None),
    ("big crack in the bedroom wall", "bedroom", "structural", None, None),
    ("it's wet in there again", None, None, None, "Which room"),
    ("something is wrong in the kitchen", "kitchen", None, None, "What kind of problem"),
]
