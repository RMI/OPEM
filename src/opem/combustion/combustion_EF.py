from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here
def calc_total_ghg_per_gal(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
   return target_table_ref["Product Combustion Emission Factors"][row_key]["kg CO2 per gallon"] * \
        other_table_refs["Table 1: Hundred-Year Global Warming Potentials"]["CO2"]["GWP"] + \
            target_table_ref["Product Combustion Emission Factors"][row_key]["g CH4 per gallon"] * \
        other_table_refs["Table 1: Hundred-Year Global Warming Potentials"]["CH4"]["GWP"] / 1000 + \
    target_table_ref["Product Combustion Emission Factors"][row_key]["g N2O per gallon"] * \
        other_table_refs["Table 1: Hundred-Year Global Warming Potentials"]["N2O"]["GWP"] / 1000

def calc_total_ghg_per_bbl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return target_table_ref["Product Combustion Emission Factors"][row_key]["Total GHGs (kg CO2eq. per gallon)"] * 42

def calc_total_ghg_per_kg_petcoke(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return (target_table_ref["Product Combustion Emission Factors"][row_key]["Total GHGs (kg CO2eq. per ton)"] / 
       other_table_refs["Table 2: Conversion Factors"]["kg per short ton"]["Conversion Factor"])

def calc_total_ghg_per_ton(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    print(((target_table_ref["Product Combustion Emission Factors"][row_key]["kg CO2 per mmBtu"] +
            target_table_ref["Product Combustion Emission Factors"][row_key]["g CH4 per mmBtu"] * 
        other_table_refs["Table 1: Hundred-Year Global Warming Potentials"]["CH4"]["GWP"] / 1000 + 

    target_table_ref["Product Combustion Emission Factors"][row_key]["g N20 per mmBtu"] * 
        other_table_refs["Table 1: Hundred-Year Global Warming Potentials"]["N2O"]["GWP"] *
        other_table_refs["Table 1: Hundred-Year Global Warming Potentials"]["CO2"]["GWP"] / 1000) * 
        target_table_ref["Product Combustion Emission Factors"][row_key]["mmBtu per ton"]))
    return ((target_table_ref["Product Combustion Emission Factors"][row_key]["kg CO2 per mmBtu"] +
            target_table_ref["Product Combustion Emission Factors"][row_key]["g CH4 per mmBtu"] * 
        other_table_refs["Table 1: Hundred-Year Global Warming Potentials"]["CH4"]["GWP"] / 1000 + 

    target_table_ref["Product Combustion Emission Factors"][row_key]["g N20 per mmBtu"] * 
        other_table_refs["Table 1: Hundred-Year Global Warming Potentials"]["N2O"]["GWP"] *
        other_table_refs["Table 1: Hundred-Year Global Warming Potentials"]["CO2"]["GWP"] / 1000) * 
        target_table_ref["Product Combustion Emission Factors"][row_key]["mmBtu per ton"])

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

        
        fill_calculated_cells(target_table_ref={"Product Combustion Emission Factors": self.product_combustion_emission_factors_petroleum, "has_wrapper": True},
                              func_to_apply=calc_total_ghg_per_gal,
                              included_cols=["Total GHGs (kg CO2eq. per gallon)"],
                              other_table_refs={"Table 1: Hundred-Year Global Warming Potentials": self.constants.table_1_100year_gwp})
        
        fill_calculated_cells(target_table_ref={"Product Combustion Emission Factors": self.product_combustion_emission_factors_petroleum, "has_wrapper": True},
                              func_to_apply=calc_total_ghg_per_bbl,
                              included_cols=["Total GHGs (kg CO2eq. per bbl)"])
                             

        fill_calculated_cells(target_table_ref={"Product Combustion Emission Factors": self.product_combustion_emission_factors_derived_solids, "has_wrapper": True},
                              func_to_apply=calc_total_ghg_per_ton,
                              included_cols=["Total GHGs (kg CO2eq. per ton)"],
                              other_table_refs={"Table 1: Hundred-Year Global Warming Potentials": self.constants.table_1_100year_gwp})

        fill_calculated_cells(target_table_ref={"Product Combustion Emission Factors": self.product_combustion_emission_factors_derived_solids, "has_wrapper": True},
                              func_to_apply=calc_total_ghg_per_kg_petcoke,
                              included_cols=["Total GHGs (kg CO2eq. per kg petcoke)"],
                              other_table_refs={"Table 2: Conversion Factors": self.constants.table_2_conversion_factors})
       

        
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
