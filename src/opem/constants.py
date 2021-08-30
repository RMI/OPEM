
from dataclasses import InitVar, dataclass, field
from typing import DefaultDict

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


@dataclass
class Constants:

    def __post_init__(self, user_input):
        print(type(user_input))
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

        # fill_calculated_cells(target_table_ref=self.emission_factors_of_fuel_combustion_origin_to_destination,
        #                       func_to_apply=emission_factors_calc2, included_cols=[
        #                           'Diesel'],
        #                       other_table_refs=[self.fuel_economy_and_resultant_energy_consumption])

        # fill_calculated_cells(target_table_ref=self.emission_factors_of_fuel_combustion_origin_to_destination,
        #                       func_to_apply=emission_factors_calc, excluded_rows=[
        #                           'SOx', 'CO2'],
        #                       excluded_cols=[
        #                           'Class 8B Diesel Truck Emission Factors (g/mi.)', 'Diesel'],
        #                       other_tables_keymap={f"{self.emission_ratios_by_fuel_type_relative_to_baseline_fuel['full_table_name']}": {
        #                           "row_keymap": {}, "col_keymap": {'Ethanol': 'E90', 'Methanol': 'M90'}}},
        #                       other_table_refs=[self.emission_ratios_by_fuel_type_relative_to_baseline_fuel])

    user_input: InitVar[DefaultDict] = {}

    # Constants sheet, table: Table 1: Hundred-Year Global Warming Potentials
    # STATIC
    table_1_100year_gwp: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Table 1- Hundred-Year Global Warming Potentials'))

    # Constants sheet, table: Table 2: Conversion Factors
    # NOTE: I CHANGED THE ORDER OF COLUMNS from the Excel workbook (unit, factor)
    # STATIC
    table_2_conversion_factors: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Table 2- Conversion Factors'))

    # Constants sheet, table: Table 3: Table 3- Fuel Specifications -- Liquid Fuels
    # STATIC
    # CALCULATED
    # USER INPUT
    table_3_fuel_specifications_liquid_fuels: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Table 3- Fuel Specifications -- Liquid Fuels'))

    # Constants sheet, table: Table 3: Table 3- Fuel Specifications -- Gaseous Fuels (at 32F and 1atm)
    # STATIC
    # CALCULATED
    table_3_fuel_specifications_gaseous_fuels: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Table 3- Fuel Specifications -- Gaseous Fuels (at 32F and 1atm)'))

    # Constants sheet, table: Table 3: Table 3- Fuel Specifications -- Solid Fuels
    # STATIC
    # CALCULATED
    table_3_fuel_specifications_solid_fuels: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Table 3- Fuel Specifications -- Solid Fuels'))

    # Constants sheet, table: Table 4- Carbon and Sulfur Ratios of Pollutants
    # STATIC
    table_4_carbon_and_sulfer_ratios: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Table 4- Carbon and Sulfur Ratios of Pollutants'))

    # Constants sheet, table: Table 5: Solid Fuel Densities
    # STATIC
    table_5_solid_fuel_densities: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Table 5: Solid Fuel Densities'))

    # Constants sheet, table: Table 5: Solid Fuel Densities
    # STATIC
    table_6_boe_conversions: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Table 6- BOE Conversions'))
