from dataclasses import dataclass
from opem.combustion.combustion_EF import CombustionEF


@dataclass
class CombustionResults


def calculate_opem_combustion(combustion_ef: CombustionEF) -> CombustionResults:

    # get percent combusted from combustion_input_dto


def calculate_combustion_emissions(combustion_ef: CombustionEF, percent_combusted):
