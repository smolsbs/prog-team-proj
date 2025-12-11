import collections
import datetime

import numpy as np
import stats
from matplotlib import pyplot as plt


class Plotter:
    def __init__(self, data):
        self.raw_data = data
        pass

    def extract_info(self):
        pass

    def plot_events_day(self):
        values = collections.Counter(stats._preprare_days(self.raw_data))

        x = list(values.keys())
        y = list(values.values())
        fig, ax = plt.subplots(layout="constrained")

        ax.bar(x, y)
        plt.show()

    def plot_events_month(self):
        values = collections.Counter(stats._preprare_months(self.raw_data))

        x = list(values.keys())
        y = list(values.values())
        fig, ax = plt.subplots(layout="constrained")

        ax.bar(x, y)
        plt.show()


if __name__ == "__main__":
    import parser

    asdf = parser.parse("../dados.txt")

    a = Plotter(asdf)
    # b = stats._filter_mags(a.raw_data, more_than=2.5, less_than=2.9)
    c = stats.filter_date(
        a.raw_data,
        after=datetime.datetime(year=2014, month=1, day=6),
        before=datetime.datetime(year=2014, month=1, day=12),
    )
    print(c)
