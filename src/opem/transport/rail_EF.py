from dataclasses import InitVar, dataclass, field
from typing import Dict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


def calc_rail_emissions_factors(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    result = 0
    for key, row in other_table_refs[0].items():
        if key not in ['full_table_name', 'row_index_name']:
            result += row[col_key] * \
                other_table_refs[1][key]['100 year GWP']
    result = (result * other_table_refs[2][extra["trip_details"]]["Energy Intensity"]) / \
        1000000/other_table_refs[3]["kg per short ton"]["Conversion Factor"] / \
        other_table_refs[3]["km per mile"]["Conversion Factor"]
    return result


def calc_rail_emissions_factors_other_gases(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return ((other_table_refs[0][extra["gas"]][col_key] * other_table_refs[1][extra["trip_details"]]["Energy Intensity"]) /
            1000000/other_table_refs[2]["kg per short ton"]["Conversion Factor"] /
            other_table_refs[2]["km per mile"]["Conversion Factor"])


def calc_emission_factors_rail_total(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return target_table_ref["Rail - Forward Trip"][col_key] + target_table_ref["Rail - Backhaul"][col_key]


@dataclass
class RailEF:
    def __post_init__(self, user_input):
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")
        # calculate CO2eq
        fill_calculated_cells(target_table_ref=self.rail_emission_factors_co2eq,
                              func_to_apply=calc_rail_emissions_factors,
                              extra={
                                  "trip_details": "Trip From Product Origin to Destination"},
                              included_rows=["Rail - Forward Trip"],
                              other_table_refs=[self.rail_emission_factors_combustion_origin_to_destination,
                                                self.constants.table_1_gwp,
                                                self.energy_intensity_of_rail_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.rail_emission_factors_co2eq,
                              func_to_apply=calc_rail_emissions_factors,
                              extra={
                                  "trip_details": "Trip From Product Destination Back to Origin"},
                              included_rows=["Rail - Backhaul"],
                              other_table_refs=[self.rail_emission_factors_combustion_destination_to_origin,
                                                self.constants.table_1_gwp,
                                                self.energy_intensity_of_rail_transportation,
                                                self.constants.table_2_conversion_factors])

        fill_calculated_cells(target_table_ref=self.rail_emission_factors_co2eq,
                              func_to_apply=calc_emission_factors_rail_total,
                              included_rows=["Rail Emissions"])

        # calculate CO2
        fill_calculated_cells(target_table_ref=self.rail_emission_factors_co2,
                              func_to_apply=calc_rail_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Trip From Product Origin to Destination",
                                  "gas": "CO2"},
                              included_rows=["Rail - Forward Trip"],
                              other_table_refs=[self.rail_emission_factors_combustion_origin_to_destination,
                                                self.energy_intensity_of_rail_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.rail_emission_factors_co2eq,
                              func_to_apply=calc_rail_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Trip From Product Destination Back to Origin",
                                  "gas": "CO2"},
                              included_rows=["Rail - Backhaul"],
                              other_table_refs=[self.rail_emission_factors_combustion_destination_to_origin,
                                                self.energy_intensity_of_rail_transportation,
                                                self.constants.table_2_conversion_factors])

        fill_calculated_cells(target_table_ref=self.rail_emission_factors_co2,
                              func_to_apply=calc_emission_factors_rail_total,
                              included_rows=["Rail Emissions"])

        # calculate CH4
        fill_calculated_cells(target_table_ref=self.rail_emission_factors_ch4,
                              func_to_apply=calc_rail_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Trip From Product Origin to Destination",
                                  "gas": "CH4"},
                              included_rows=["Rail - Forward Trip"],
                              other_table_refs=[self.rail_emission_factors_combustion_origin_to_destination,
                                                self.energy_intensity_of_rail_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.rail_emission_factors_ch4,
                              func_to_apply=calc_rail_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Trip From Product Destination Back to Origin",
                                  "gas": "CH4"},
                              included_rows=["Rail - Backhaul"],
                              other_table_refs=[self.rail_emission_factors_combustion_destination_to_origin,
                                                self.energy_intensity_of_rail_transportation,
                                                self.constants.table_2_conversion_factors])

        fill_calculated_cells(target_table_ref=self.rail_emission_factors_ch4,
                              func_to_apply=calc_emission_factors_rail_total,
                              included_rows=["Rail Emissions"])

        # calculate N2O
        fill_calculated_cells(target_table_ref=self.rail_emission_factors_n2o,
                              func_to_apply=calc_rail_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Trip From Product Origin to Destination",
                                  "gas": "N2O"},
                              included_rows=["Rail - Forward Trip"],
                              other_table_refs=[self.rail_emission_factors_combustion_origin_to_destination,
                                                self.energy_intensity_of_rail_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.rail_emission_factors_n2o,
                              func_to_apply=calc_rail_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Trip From Product Destination Back to Origin",
                                  "gas": "N2O"},
                              included_rows=["Rail - Backhaul"],
                              other_table_refs=[self.rail_emission_factors_combustion_destination_to_origin,
                                                self.energy_intensity_of_rail_transportation,
                                                self.constants.table_2_conversion_factors])

        fill_calculated_cells(target_table_ref=self.rail_emission_factors_n2o,
                              func_to_apply=calc_emission_factors_rail_total,
                              included_rows=["Rail Emissions"])

    constants: Constants
    # will this cause problems if I try to pass in a list?
    user_input: InitVar[Dict] = {}

    # RailEF sheet, table: Rail Emission Factors
    # CALCULATED
    rail_emission_factors_co2eq: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Rail_Emission_Factors_CO2eq', 'rail'))

    # RailEF sheet, table: Rail Emission Factors
    # CALCULATED
    rail_emission_factors_co2: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Rail_Emission_Factors_CO2', 'rail'))

    # RailEF sheet, table: Rail Emission Factors
    # CALCULATED
    rail_emission_factors_ch4: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Rail_Emission_Factors_CH4', 'rail'))

    # RailEF sheet, table: Rail Emission Factors
    # CALCULATED
    rail_emission_factors_n2o: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Rail_Emission_Factors_N2O', 'rail'))

    # RailEF sheet, table: Energy Intensity of Rail Transportation (Btu:ton-mile)
    # USER INPUT
    energy_intensity_of_rail_transportation: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Energy_Intensity_of_Rail_Transportation', 'rail'))

    # RailEF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Origin to Product Destination (grams per mmBtu of fuel burned)
    # STATIC
    rail_emission_factors_combustion_origin_to_destination: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
            "Emission_Factors_of_Fuel_Combustion_for_Feedstock_and_Fuel_Transportation_Trip_From_Product_Origin_to_Product_Destination_Locomotive", 'rail'))

# RailEF sheet, table: EEmission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned)
    # STATIC
    rail_emission_factors_combustion_destination_to_origin: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
            'Emission_Factors_of_Fuel_Combustion_for_Feedstock_and_Fuel_Transportation_Trip_From_Product_Destination_Back_to_Product_Origin_Locomotive', 'rail'))
