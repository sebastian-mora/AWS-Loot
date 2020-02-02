

class Color:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    # noinspection SpellCheckingInspection
    ENDC = '\033[0m'

    @staticmethod
    def print(color, text):
        print(f'{color}{text}{Color.ENDC}')
