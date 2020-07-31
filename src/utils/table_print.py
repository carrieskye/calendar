import re

from src.utils.logger import Logger


class TablePrint:

    def __init__(self, title, headers, lengths):
        self.lengths = lengths

        # Print title
        Logger.title(title)

        # Print header
        lines = [header.ljust(lengths[index]) for index, header in enumerate(headers)]
        Logger.log(' | '.join(lines), log_location=False)

        dashes = []
        for line in lines:
            dashes.append(re.sub(r'[a-zA-Z]|\s', '-', line))
        Logger.log(' | '.join(dashes), log_location=False)

    def print_line(self, values):
        assert len(values) == len(self.lengths)

        values = [value if value else '' for index, value in enumerate(values)]
        values = [str(value).split('\n')[0] for index, value in enumerate(values)]
        values = [value if len(value) <= self.lengths[index] else f'{value[:self.lengths[index] - 3]}...'
                  for index, value in enumerate(values)]

        line = [value.ljust(self.lengths[index]) for index, value in enumerate(values)]
        Logger.log(' | '.join(line), log_location=False)

    @staticmethod
    def end(lines):
        for i in range(0, lines):
            Logger.empty_line()
