import collections
import datetime

from matplotlib import pyplot as plt


class Plotter:
    def __init__(self, data):
        self.raw_data = data
        pass

    def extract_info(self):
        pass

    def plot_events_day(self):
        values = collections.Counter(self._preprare_days())

        x = list(values.keys())
        y = list(values.values())
        fig, ax = plt.subplots(layout="constrained")

        ax.bar(x, y)
        plt.show()

    def plot_events_month(self):
        values = collections.Counter(self._preprare_months())

        x = list(values.keys())
        y = list(values.values())
        fig, ax = plt.subplots(layout="constrained")

        ax.bar(x, y)
        plt.show()

    def _preprare_days(self):
        c = self.raw_data.Data.to_list()
        for idx, d in enumerate(c):
            aux = datetime.datetime.fromisoformat(d)
            c[idx] = datetime.datetime.strftime(aux, "%Y-%m-%d")

        return c

    def _preprare_months(self):
        c = self.raw_data.Data.to_list()
        for idx, d in enumerate(c):
            aux = datetime.datetime.fromisoformat(d)
            c[idx] = datetime.datetime.strftime(aux, "%Y-%m")

        return c

    def _prepare_mags(self):
        pass
        # c = self.raw_data.


if __name__ == "__main__":
    import parser

    asdf = parser.parse("../dados.txt")

    a = Plotter(asdf)
    print(a.raw_data.dtypes)
