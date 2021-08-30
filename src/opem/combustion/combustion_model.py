from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.combustion.combustion_EF import CombustionEF
from opem.transport.transport_EF import TransportEF

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


@dataclass
class CombustionModel:
    # initialize with gas/fuel emissions factors
    def __post_init__():
        def __post_init__(self, user_input):

            if type(user_input) == dict:
                # this allows us to get input from a dict generated from another dataclass
                initialize_from_dataclass(self, user_input)
            elif type(user_input) == list:
                initialize_from_list(self, user_input)
            else:
                raise ValueError(
                    "Please pass a list or dictionary to initialize")


user_input: InitVar[DefaultDict] = {}

combustion_results = field(
    default_factory=lambda: {})

combustion_EF: CombustionEF


def calculate_opem_combustion(combustion_ef: CombustionEF) -> CombustionResults:
    pass

    # get percent combusted from combustion_input_dto


def calculate_combustion_emissions(combustion_ef: CombustionEF, percent_combusted):
    pass
