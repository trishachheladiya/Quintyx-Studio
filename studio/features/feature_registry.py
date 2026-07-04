from __future__ import annotations

from typing import Type

try:
    from ..models.feature_definition import FeatureDefinition
    from .feature_calculator import (
        BaseFeatureCalculator,
        DayOfWeekCalculator,
        LowerWickCalculator,
        MomentumRsiCalculator,
        PriceActionCalculator,
        PriceStructureDistance200Calculator,
        PriceStructureDistance50Calculator,
        PriceStructureDistanceCalculator,
        RangeCalculator,
        Return24Calculator,
        Return5Calculator,
        ReturnCalculator,
        TimeCalculator,
        TrendEma100Calculator,
        TrendEma200Calculator,
        TrendEma50Calculator,
        TrendEmaCalculator,
        UpperWickCalculator,
        VolatilityAtrCalculator,
    )
except ImportError:
    from models.feature_definition import FeatureDefinition
    from features.feature_calculator import (
        BaseFeatureCalculator,
        DayOfWeekCalculator,
        LowerWickCalculator,
        MomentumRsiCalculator,
        PriceActionCalculator,
        PriceStructureDistance200Calculator,
        PriceStructureDistance50Calculator,
        PriceStructureDistanceCalculator,
        RangeCalculator,
        Return24Calculator,
        Return5Calculator,
        ReturnCalculator,
        TimeCalculator,
        TrendEma100Calculator,
        TrendEma200Calculator,
        TrendEma50Calculator,
        TrendEmaCalculator,
        UpperWickCalculator,
        VolatilityAtrCalculator,
    )


class FeatureRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, FeatureDefinition] = {}
        self._calculators: dict[str, Type[BaseFeatureCalculator]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        for calculator_cls in (
            TrendEmaCalculator,
            TrendEma50Calculator,
            TrendEma100Calculator,
            TrendEma200Calculator,
            MomentumRsiCalculator,
            VolatilityAtrCalculator,
            ReturnCalculator,
            Return5Calculator,
            Return24Calculator,
            PriceStructureDistanceCalculator,
            PriceStructureDistance50Calculator,
            PriceStructureDistance200Calculator,
            PriceActionCalculator,
            UpperWickCalculator,
            LowerWickCalculator,
            RangeCalculator,
            TimeCalculator,
            DayOfWeekCalculator,
        ):
            self.register(calculator_cls)

    def register(self, calculator_cls: Type[BaseFeatureCalculator]) -> None:
        calculator = calculator_cls()
        feature_name = calculator.name
        if feature_name in self._definitions:
            raise ValueError(f"Duplicate feature registration: {feature_name}")
        self._definitions[feature_name] = FeatureDefinition(
            name=calculator.name,
            category=calculator.category,
            description=calculator.description,
        )
        self._calculators[feature_name] = calculator_cls

    def get_definitions(self) -> list[FeatureDefinition]:
        return sorted(self._definitions.values(), key=lambda item: item.name)

    def get_definitions_by_category(self) -> dict[str, list[FeatureDefinition]]:
        grouped: dict[str, list[FeatureDefinition]] = {}
        for definition in self.get_definitions():
            grouped.setdefault(definition.category, []).append(definition)
        return grouped

    def get_calculator(self, feature_name: str) -> BaseFeatureCalculator:
        if feature_name not in self._calculators:
            raise KeyError(f"Unsupported feature: {feature_name}")
        return self._calculators[feature_name]()

    def get_feature_names(self) -> list[str]:
        return [definition.name for definition in self.get_definitions()]
