class Output:

    @staticmethod
    def make_title(title):
        print(u'\n\n\u2554' + ''.join([u'\u2550' for _ in range(0, len(title) + 2)]) + u'\u2557')
        print(u'\u2551 ' + title.upper() + u' \u2551')
        print(u'\u255A' + ''.join([u'\u2550' for _ in range(0, len(title) + 2)]) + u'\u255D\n')

    @staticmethod
    def make_bold(text):
        bold = "\033[1m"
        reset = "\033[0;0m"
        print(bold + text + reset)
