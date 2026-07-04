from __future__ import annotations

import numpy as np
import pandas as pd


class BaseFeatureCalculator:
    name = ""
    category = ""
    description = ""

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        raise NotImplementedError


class TrendEmaCalculator(BaseFeatureCalculator):
    def __init__(self) -> None:
        self.name = "EMA20"
        self.category = "Trend"
        self.description = "20-period exponential moving average"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["close"].ewm(span=20, adjust=False).mean()


class TrendEma50Calculator(TrendEmaCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "EMA50"
        self.description = "50-period exponential moving average"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["close"].ewm(span=50, adjust=False).mean()


class TrendEma100Calculator(TrendEmaCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "EMA100"
        self.description = "100-period exponential moving average"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["close"].ewm(span=100, adjust=False).mean()


class TrendEma200Calculator(TrendEmaCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "EMA200"
        self.description = "200-period exponential moving average"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["close"].ewm(span=200, adjust=False).mean()


class MomentumRsiCalculator(BaseFeatureCalculator):
    def __init__(self) -> None:
        self.name = "RSI14"
        self.category = "Momentum"
        self.description = "14-period relative strength index"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        close = pd.to_numeric(frame["close"], errors="coerce")
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(com=13, min_periods=14).mean()
        avg_loss = loss.ewm(com=13, min_periods=14).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)


class VolatilityAtrCalculator(BaseFeatureCalculator):
    def __init__(self) -> None:
        self.name = "ATR14"
        self.category = "Volatility"
        self.description = "14-period average true range"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        high = pd.to_numeric(frame["high"], errors="coerce")
        low = pd.to_numeric(frame["low"], errors="coerce")
        close = pd.to_numeric(frame["close"], errors="coerce")
        prev_close = close.shift(1)
        tr = pd.concat(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        return tr.ewm(alpha=1 / 14, adjust=False).mean()


class ReturnCalculator(BaseFeatureCalculator):
    def __init__(self) -> None:
        self.name = "Return1"
        self.category = "Returns"
        self.description = "1-period return"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["close"].pct_change(1)


class Return5Calculator(ReturnCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Return5"
        self.description = "5-period return"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["close"].pct_change(5)


class Return24Calculator(ReturnCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Return24"
        self.description = "24-period return"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["close"].pct_change(24)


class PriceStructureDistanceCalculator(BaseFeatureCalculator):
    def __init__(self) -> None:
        self.name = "Distance EMA20"
        self.category = "Price Structure"
        self.description = "Close minus EMA20"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        ema20 = frame["close"].ewm(span=20, adjust=False).mean()
        return frame["close"] - ema20


class PriceStructureDistance50Calculator(PriceStructureDistanceCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Distance EMA50"
        self.description = "Close minus EMA50"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        ema50 = frame["close"].ewm(span=50, adjust=False).mean()
        return frame["close"] - ema50


class PriceStructureDistance200Calculator(PriceStructureDistanceCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Distance EMA200"
        self.description = "Close minus EMA200"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        ema200 = frame["close"].ewm(span=200, adjust=False).mean()
        return frame["close"] - ema200


class PriceActionCalculator(BaseFeatureCalculator):
    def __init__(self) -> None:
        self.name = "Body"
        self.category = "Price Action"
        self.description = "Candle body"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["close"] - frame["open"]


class UpperWickCalculator(PriceActionCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Upper Wick"
        self.description = "Upper wick length"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["high"] - frame[["open", "close"]].max(axis=1)


class LowerWickCalculator(PriceActionCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Lower Wick"
        self.description = "Lower wick length"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame[["open", "close"]].min(axis=1) - frame["low"]


class RangeCalculator(PriceActionCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Range"
        self.description = "High-low range"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["high"] - frame["low"]


class TimeCalculator(BaseFeatureCalculator):
    def __init__(self) -> None:
        self.name = "Hour"
        self.category = "Time"
        self.description = "Hour of the candle"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["timestamp"].dt.hour


class DayOfWeekCalculator(TimeCalculator):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Day Of Week"
        self.description = "Day of the week"

    def calculate(self, frame: pd.DataFrame) -> pd.Series:
        return frame["timestamp"].dt.dayofweek
