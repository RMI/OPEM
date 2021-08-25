from dataclasses import dataclass

# hold validated user input


@dataclass
class CombustionInputDto:
    key1: str
    key2: str
    # should have % combusted


@dataclass
class TransportInputDto:
    pass
    # should have user transport fuel selections


@dataclass
class ProductSlateDto:
    pass
