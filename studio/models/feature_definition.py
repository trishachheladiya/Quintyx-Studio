from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    category: str
    description: str
