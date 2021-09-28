from dataclasses import InitVar, dataclass, field
from typing import Dict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


def calc_bbl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return (target_table_ref[row_key]["MJ"]/other_table_refs[0] /
            target_table_ref[row_key][other_tables_keymap[col_key]]/other_table_refs[1])


def calc_onsite_sum(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    sum = 0
    for row in target_table_ref.keys():
        if row not in ["full_table_name", "row_index_name", "Sum"]:
            sum += target_table_ref[row][col_key]
    return sum


def calc_kg_co2e(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    result = 0
    if row_key in ["CH4", "N2O"]:
        result = target_table_ref[row_key]["mass"] * \
            other_table_refs["table_1_gwp"][row_key][other_tables_keymap[col_key]]
        if row_key == "CH4":
            result /= 1000
        else:
            result /= 1000000
    elif row_key == "CO2":
        result = target_table_ref[row_key]["mass"]
    return result


def calc_ethyl_sum(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    sum = 0
    for row in target_table_ref.keys():
        if row in extra["rows_to_sum"]:
            sum += target_table_ref[row][col_key]
    return sum


def calc_co2e_ratios(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    if col_key in ["kg CO2e/bbl Natural Gas Liquids (LHV)", "kg CO2e/bbl Natural Gas Liquids (HHV)"]:

        return (other_table_refs["kg_co2e"][row_key][other_tables_keymap["co2e"]] /
                other_table_refs["onsite_inputs"]["Natural Gas Liquids"][other_tables_keymap[col_key]])
    elif col_key in ["kg CO2e/bbl total input (LHV)", "kg CO2e/bbl total input (HHV)"]:
        return (other_table_refs["kg_co2e"][row_key][other_tables_keymap["co2e"]] /
                other_table_refs["onsite_inputs"]["Sum"][other_tables_keymap[col_key]])


@ dataclass
class PetroChemEF:
    def __post_init__(self, user_input):
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

        fill_calculated_cells(target_table_ref=self.onsite_energy_inputs,
                              func_to_apply=calc_bbl,
                              excluded_rows=["Sum"],
                              included_cols=["bbl (LHV)", "bbl (HHV)"],
                              other_table_refs=[self.gal_per_barrel,
                                                self.MJ_per_Btu],
                              other_tables_keymap={"bbl (LHV)": "LHV btu/gal", "bbl (HHV)": "HHV btu/gal"})

        fill_calculated_cells(target_table_ref=self.onsite_energy_inputs,
                              func_to_apply=calc_onsite_sum,
                              included_rows=["Sum"],
                              included_cols=["MJ", "bbl (LHV)", "bbl (HHV)"])

        fill_calculated_cells(target_table_ref=self.ethylene_conversion_kg_co2e,
                              func_to_apply=calc_kg_co2e,
                              included_rows=["CH4", "N2O", "CO2"],
                              included_cols=[
                                  "kg CO2e (100 yr GWP)", "kg CO2e (20yr GWP)"],
                              other_table_refs={
                                  "table_1_gwp": self.constants.table_1_gwp},
                              other_tables_keymap={"kg CO2e (100 yr GWP)": "100 year GWP", "kg CO2e (20yr GWP)": "20 year GWP"})

        fill_calculated_cells(target_table_ref=self.ethylene_conversion_kg_co2e,
                              func_to_apply=calc_ethyl_sum,
                              included_rows=["Sum"],
                              included_cols=[
                                  "kg CO2e (100 yr GWP)", "kg CO2e (20yr GWP)"],
                              extra={"rows_to_sum": ["CH4", "N2O", "CO2"]})

        fill_calculated_cells(target_table_ref=self.ethylene_conversion_100yr_gwp,
                              func_to_apply=calc_co2e_ratios,
                              included_rows=["CH4", "N2O", "CO2"],
                              other_table_refs={
                                  "kg_co2e": self.ethylene_conversion_kg_co2e,
                                  "onsite_inputs": self.onsite_energy_inputs},
                              other_tables_keymap={"co2e": "kg CO2e (100 yr GWP)",
                                                   "kg CO2e/bbl Natural Gas Liquids (LHV)": "bbl (LHV)",
                                                   "kg CO2e/bbl Natural Gas Liquids (HHV)": "bbl (HHV)",
                                                   "kg CO2e/bbl total input (LHV)": "bbl (LHV)",
                                                   "kg CO2e/bbl total input (HHV)": "bbl (HHV)"})
        fill_calculated_cells(target_table_ref=self.ethylene_conversion_20yr_gwp,
                              func_to_apply=calc_co2e_ratios,
                              included_rows=["CH4", "N2O", "CO2"],
                              other_table_refs={
                                  "kg_co2e": self.ethylene_conversion_kg_co2e,
                                  "onsite_inputs": self.onsite_energy_inputs},
                              other_tables_keymap={"co2e": "kg CO2e (20yr GWP)",
                                                   "kg CO2e/bbl Natural Gas Liquids (LHV)": "bbl (LHV)",
                                                   "kg CO2e/bbl Natural Gas Liquids (HHV)": "bbl (HHV)",
                                                   "kg CO2e/bbl total input (LHV)": "bbl (LHV)",
                                                   "kg CO2e/bbl total input (HHV)": "bbl (HHV)"})

        fill_calculated_cells(target_table_ref=self.ethylene_conversion_100yr_gwp,
                              func_to_apply=calc_ethyl_sum,
                              included_rows=["Sum"],
                              extra={"rows_to_sum": ["CH4", "N2O", "CO2"]})
        fill_calculated_cells(target_table_ref=self.ethylene_conversion_20yr_gwp,
                              func_to_apply=calc_ethyl_sum,
                              included_rows=["Sum"],
                              extra={"rows_to_sum": ["CH4", "N2O", "CO2"]})

    constants: Constants

    gal_per_barrel: int = 42
    MJ_per_Btu: float = 0.00105505585
    # will this cause problems if I try to pass in a list?
    user_input: InitVar[Dict] = {}

    # PetrochemEF sheet, table: Ethylene Conversion
    # CALCULATED
    ethylene_conversion_kg_co2e: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Ethylene_Conversion_kg_CO2e', 'petrochem'))

    # PetrochemEF sheet, table: Ethylene Conversion
    # CALCULATED
    ethylene_conversion_20yr_gwp: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Ethylene_Conversion_20yr_GWP', 'petrochem'))

    # PetrochemEF sheet, table: Ethylene Conversion
    # CALCULATED
    ethylene_conversion_100yr_gwp: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Ethylene_Conversion_100yr_GWP', 'petrochem'))

    # PetrochemEF sheet, table: Onsite Energy Inputs
    # CALCULATED
    onsite_energy_inputs: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Onsite_Energy_Inputs', 'petrochem'))

    # PetrochemEF sheet, table: Onsite Energy Inputs
    # CALCULATED
    onsite_energy_inputs_water: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Onsite_Energy_Inputs_Water', 'petrochem'))
