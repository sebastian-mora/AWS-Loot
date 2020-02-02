import math


def shannon_entropy(data):
    if not data:
        return 0

    entropy = 0
    for character_i in range(256):
        px = data.count(chr(character_i)) / len(data)
        if px > 0:
            entropy += - px * math.log(px, 2)
    return entropy


# This is slightly arbitrary. It's the value used in TruffleHog. Could be improved
def contains_secret(data, THRESHOLD=3.5):
    return shannon_entropy(data) > THRESHOLD
