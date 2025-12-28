from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    def __init__(self, **kwargs):
        self.params = kwargs

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generates trading signals for the given DataFrame.
        Returns a Series where: 1 = Buy, -1 = Sell, 0 = Hold.
        """
        pass
