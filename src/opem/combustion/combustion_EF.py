from dataclasses import InitVar, dataclass, field
from typing import Dict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells


# Define functions for filling calculated cells in the tables here


def calc_total_ghg_per_gal(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None,
                           extra=None):
    return target_table_ref["Product Combustion Emission Factors"][row_key]["kg CO2 per gallon"] * \
           other_table_refs["Table 1: Global Warming Potentials"]["CO2"]["User Selection"] + \
           target_table_ref["Product Combustion Emission Factors"][row_key]["g CH4 per gallon"] * \
           other_table_refs["Table 1: Global Warming Potentials"]["CH4"]["User Selection"] / 1000 + \
           target_table_ref["Product Combustion Emission Factors"][row_key]["g N2O per gallon"] * \
           other_table_refs["Table 1: Global Warming Potentials"]["N2O"]["User Selection"] / 1000
    # made change from ["100 year GWP"] to ["User Selection"]


def calc_total_ghg_per_bbl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None,
                           extra=None):
    return target_table_ref["Product Combustion Emission Factors"][row_key]["Total GHGs (kg CO2eq. per gallon)"] * 42


def calc_total_ghg_per_kg_petcoke(row_key, col_key, target_table_ref=None, other_table_refs=None,
                                  other_tables_keymap=None, extra=None):
    return (target_table_ref["Product Combustion Emission Factors"][row_key]["Total GHGs (kg CO2eq. per ton)"] /
            other_table_refs["Table 2: Conversion Factors"]["kg per short ton"]["Conversion Factor"])


def calc_total_ghg_per_ton(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None,
                           extra=None):
    return ((target_table_ref["Product Combustion Emission Factors"][row_key]["kg CO2 per mmBtu"] +
             target_table_ref["Product Combustion Emission Factors"][row_key]["g CH4 per mmBtu"] *
             other_table_refs["Table 1: Global Warming Potentials"]["CH4"]["User Selection"] / 1000 +

             target_table_ref["Product Combustion Emission Factors"][row_key]["g N20 per mmBtu"] *
             other_table_refs["Table 1: Global Warming Potentials"]["N2O"]["User Selection"] *
             other_table_refs["Table 1: Global Warming Potentials"]["CO2"]["User Selection"] / 1000) *
            target_table_ref["Product Combustion Emission Factors"][row_key]["mmBtu per ton"])
    # made change from ["100 year GWP"] to ["User Selection"]


def calc_total_ghg_per_scf(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None,
                           extra=None):
    return (target_table_ref["Product Combustion Emission Factors"][row_key]["kg CO2 per scf"] *
            other_table_refs["Table 1: Global Warming Potentials"]["CO2"]["User Selection"] +
            target_table_ref["Product Combustion Emission Factors"][row_key]["g CH4 per scf"] *
            other_table_refs["Table 1: Global Warming Potentials"]["CH4"]["User Selection"] / 1000 +
            target_table_ref["Product Combustion Emission Factors"][row_key]["g N2O per scf"] *
            other_table_refs["Table 1: Global Warming Potentials"]["N2O"]["User Selection"] / 1000)
    # made change from ["100 year GWP"] to ["User Selection"]


def calc_total_ghg_per_boe(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None,
                           extra=None):
    return (target_table_ref["Product Combustion Emission Factors"][row_key]["Total GHGs (kg CO2eq. per scf)"] *
            other_table_refs["Table 6: BOE conversions"]["Natural Gas (MCF/BOE)"]["conversion factor"]) * 1000


def calc_ngl_estimate(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None,
                      extra=None):
    sum = 0
    for row in other_table_refs["pet products"].items():
        if row[0] in extra["included_products"]:
            sum += row[1][col_key]
    return sum / len(extra["included_products"])


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

        fill_calculated_cells(
            target_table_ref={"Product Combustion Emission Factors": self.product_combustion_emission_factors_petroleum,
                              "has_wrapper": True},
            func_to_apply=calc_total_ghg_per_gal,
            included_cols=[
                "Total GHGs (kg CO2eq. per gallon)"],
            other_table_refs={"Table 1: Global Warming Potentials": self.constants.table_1_gwp})

        fill_calculated_cells(
            target_table_ref={"Product Combustion Emission Factors": self.product_combustion_emission_factors_petroleum,
                              "has_wrapper": True},
            func_to_apply=calc_total_ghg_per_bbl,
            included_cols=["Total GHGs (kg CO2eq. per bbl)"])

        fill_calculated_cells(target_table_ref={
            "Product Combustion Emission Factors": self.product_combustion_emission_factors_derived_solids,
            "has_wrapper": True},
                              func_to_apply=calc_total_ghg_per_ton,
                              included_cols=["Total GHGs (kg CO2eq. per ton)"],
                              other_table_refs={"Table 1: Global Warming Potentials": self.constants.table_1_gwp})

        fill_calculated_cells(target_table_ref={
            "Product Combustion Emission Factors": self.product_combustion_emission_factors_derived_solids,
            "has_wrapper": True},
                              func_to_apply=calc_total_ghg_per_kg_petcoke,
                              included_cols=[
                                  "Total GHGs (kg CO2eq. per kg petcoke)"],
                              other_table_refs={
                                  "Table 2: Conversion Factors": self.constants.table_2_conversion_factors})

        fill_calculated_cells(target_table_ref={
            "Product Combustion Emission Factors": self.product_combustion_emission_factors_natural_gas,
            "has_wrapper": True},
                              func_to_apply=calc_total_ghg_per_scf,
                              included_cols=["Total GHGs (kg CO2eq. per scf)"],
                              other_table_refs={"Table 1: Global Warming Potentials": self.constants.table_1_gwp})

        fill_calculated_cells(target_table_ref={
            "Product Combustion Emission Factors": self.product_combustion_emission_factors_natural_gas,
            "has_wrapper": True},
                              func_to_apply=calc_total_ghg_per_boe,
                              included_cols=[
                                  "Total GHGs (kg CO2eq. per boe)"],
                              other_table_refs={"Table 6: BOE conversions": self.constants.table_6_boe_conversions})

        fill_calculated_cells(
            target_table_ref={"Product Combustion Emission Factors": self.ngl_estimate, "has_wrapper": True},
            func_to_apply=calc_ngl_estimate,
            other_table_refs={"pet products": self.product_combustion_emission_factors_petroleum},
            extra={"included_products": ["Butane", "Ethane", "Pentanes Plus", "Propane"]})

    constants: Constants
    user_input: InitVar[Dict] = {}

    # Prod CombustEF sheet, table: Product Combustion Emission Factors -- Petroleum Products
    # CALCULATED
    product_combustion_emission_factors_petroleum: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Product_Combustion_Emission_Factors_Petroleum_Products',
                                                         'combustion'))

    # Prod CombustEF sheet, table: Product Combustion Emission Factors -- Fossil-Fuel-Derived Fuels (Solid)
    # CALCULATED
    product_combustion_emission_factors_derived_solids: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
            'Product_Combustion_Emission_Factors_Fossil_Fuel_Derived_Fuels_Solid', 'combustion'))

    # Prod CombustEF sheet, table: Product Combustion Emission Factors -- Natural Gas
    # CALCULATED
    product_combustion_emission_factors_natural_gas: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Product_Combustion_Emission_Factors_Natural_Gas',
                                                         'combustion'))

    # Prod CombustEF sheet, 
    # CALCULATED
    ngl_estimate: Dict = field(
        default_factory=lambda: build_dict_from_defaults('NGL_Estimate', 'combustion'))
