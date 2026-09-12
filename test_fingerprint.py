# test_fingerprint.py
from brain.onboarding.fingerprint import build_style_profile

samples = [
    "hey can u send me the file when u get a sec, no rush",
    "yo that meeting today got moved to 3pm btw",
    "lol yeah i'll take a look at it tonight",
]

print(build_style_profile(samples))