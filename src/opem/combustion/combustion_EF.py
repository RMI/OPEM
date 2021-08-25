from dataclasses import dataclass


@dataclass
CombustionEF:
    # initialize with gas/fuel emissions factors
    def __post_init__():
        calculate_total_ghg_ef()
    # calculate total GHG
    def calculate_total_ghg_ef(self):
