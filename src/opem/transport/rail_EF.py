from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


@dataclass
class RailEF:
    def __post_init__(self, user_input):
        print(type(user_input))
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    def calculate_rail_ef():
        pass

    constants: Constants
    # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}

    # RailEF sheet, table: Rail Emission Factors
    # CALCULATED
    rail_emission_factors: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Rail Emission Factors'))

    # RailEF sheet, table: Energy Intensity of Rail Transportation (Btu:ton-mile)
    # USER INPUT
    energy_intensity_of_rail_transportation: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Energy Intensity of Rail Transportation (Btu:ton-mile)'))

    # RailEF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Origin to Product Destination (grams per mmBtu of fuel burned)
    # STATIC
    rail_emission_factors_combustion_origin_to_destination: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults("Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Origin to Product Destination (grams per mmBtu) -- Locomotive"))

# RailEF sheet, table: EEmission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned)
    # STATIC
    rail_emission_factors_combustion_destination_to_origin: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Destination Back to Product Origin (grams per mmBtu) -- Locomotive'))
