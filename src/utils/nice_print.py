import re


class NicePrint:

    def __init__(self, title, headers, lengths):
        self.lengths = lengths

        # Print title
        print()
        print(''.join(['='] * (len(title) + 8)))
        print(f'||{title.center(len(title) + 4)}||')
        print(''.join(['='] * (len(title) + 8)))
        print()

        # Print header
        lines = [header.rjust(lengths[index]) for index, header in enumerate(headers)]
        print(' | '.join(lines))

        dashes = []
        for line in lines:
            dashes.append(re.sub(r'[A-Z]|\s', '-', line))
        print(' | '.join(dashes))

    def print_line(self, values):
        assert len(values) == len(self.lengths)

        values = [value if value else '' for index, value in enumerate(values)]
        values = [value.split('\n')[0] for index, value in enumerate(values)]
        values = [value if len(value) <= self.lengths[index] else f'{value[:self.lengths[index] - 3]}...'
                  for index, value in enumerate(values)]

        line = [value.ljust(self.lengths[index]) for index, value in enumerate(values)]
        print(' | '.join(line))

    @staticmethod
    def end(lines):
        for i in range(0, lines):
            print()
