from fuzzywuzzy import fuzz

# print(fuzz.ratio("henderson", "jordan henderson"))
# print(fuzz.ratio("virgil vandijk", "virgil van dik"))
# print(fuzz.ratio("jurgen kloop", "Jürgen Klopp"))

# print(fuzz.partial_ratio("hendrsn", "jordan henderson"))
# print(fuzz.partial_ratio("virgil vandijk", "virgil van dik"))
# print(fuzz.partial_ratio("jurgen kloop", "Jürgen Klopp"))

print(fuzz.token_set_ratio("henderson", "jordan henderson"))
print(fuzz.token_set_ratio("vandijk", "virgil van dik"))
print(fuzz.token_set_ratio("jurgen kloop", "Jürgen Klopp"))