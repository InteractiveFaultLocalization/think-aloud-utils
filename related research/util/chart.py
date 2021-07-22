import dataclasses
from typing import Dict, Union, Tuple, Optional

from matplotlib import pyplot as plt

from util.string import part_before, enclose


@dataclasses.dataclass
class AxisLabel:
    name: str
    unit: Optional[str] = None
    note: Optional[str] = None


class DistributionChart(object):
    def __init__(
            self,
            distribution: Tuple[Tuple[str, Union[int, float]], ...], file_name: str,
            x_label: AxisLabel = AxisLabel('items'), y_label: AxisLabel = AxisLabel('count')):
        self.distribution = distribution
        self.file_name = file_name
        self.x_label = x_label
        self.y_label = y_label

    def __enter__(self):
        self.figure: plt.Figure
        self.axes: plt.Axes
        self.figure, self.axes = plt.subplots()
        self.axes.bar(
            x=[e[0] for e in self.distribution], height=[e[1] for e in self.distribution],
            color='lightgray', edgecolor='black'
        )
        self.figure.set_size_inches(12, 6)
        self.axes.set_xlabel(
            self.x_label.name
            + part_before(enclose(self.x_label.unit, open_mark='[', close_mark=']'))
            + part_before(enclose(self.x_label.note)))
        self.axes.set_ylabel(
            self.y_label.name
            + part_before(enclose(self.y_label.unit, open_mark='[', close_mark=']'))
            + part_before(enclose(self.y_label.note)))
        self.figure.autofmt_xdate()
        return self.figure, self.axes

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.figure.show()
        self.figure.savefig(self.file_name)
