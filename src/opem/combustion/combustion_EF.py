from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


@dataclass
class CombustionEF:
    # initialize with gas/fuel emissions factors
    def __post_init__(self, user_input):

        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError(
                "Please pass a list or dictionary to initialize")


constants: Constants
user_input: InitVar[DefaultDict] = {}

# Prod CombustEF sheet, table: Product Combustion Emission Factors -- Petroleum Products
# CALCULATED
product_combustion_emission_factors_petroleum: DefaultDict = field(
    default_factory=lambda: build_dict_from_defaults('Product Combustion Emission Factors -- Petroleum Products'))


# Prod CombustEF sheet, table: Product Combustion Emission Factors -- Fossil-Fuel-Derived Fuels (Solid)
# CALCULATED
product_combustion_emission_factors_derived_solids: DefaultDict = field(
    default_factory=lambda: build_dict_from_defaults('Product Combustion Emission Factors -- Fossil-Fuel-Derived Fuels (Solid)'))
