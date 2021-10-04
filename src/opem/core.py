

from dataclasses import InitVar, dataclass, field
from typing import Dict, Dict
from math import isnan
from opem.combustion.combustion_EF import CombustionEF
from opem.constants import Constants
from opem.input import user_input_dto
from opem.input.opgee_input import OpgeeInput
from opem.products.product_slate import ProductSlate
from opem.transport.petrochem_EF import PetroChemEF

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells
from opem.transport.transport_EF import TransportEF


def verify_user_fuel_shares(user_shares):
    for key, row in user_shares.items():
        if key not in ["full_table_name", "row_index_name"]:
            share_sum = sum(share for share in row.values()
                            if not isnan(share))
            if share_sum != 1:
                raise(ValueError(
                    f'Shares of fuel types for {key} do not add to 1. Sum is {share_sum}'))
    print("fuel shares valid")
# Define functions for filling calculated cells in the tables here
def calc_gas_production_volume(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["gas_prod_volume"] / other_table_refs["table_6"]["Natural Gas (MCF/BOE)"]["conversion factor"]

def calc_oil_volume_ratio(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["oil_volume"] / other_table_refs["product_slate"]["Barrels of Crude per Day"]["Flow"]

def calc_total_field_ngl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if other_table_refs["ngl_volume_source"] == 1:
    
        return 1
    elif other_table_refs ["ngl_volume_source"] == 2:
        
        return other_table_refs["c2"] + other_table_refs["c3"] + other_table_refs["c4"] + other_table_refs["c5"] 

def calc_opgee_coke_mass(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None): 
    return (other_table_refs["coke_mass"] * 
         other_table_refs["table_5"]["Petroleum Coke Density, average bbl/ton"]["density"] /
         other_table_refs["table_2"]["kg per short ton"]["Conversion Factor"])

def calc_total_boe(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return (other_table_refs["gas_vol"]["row"]["col"] +
            other_table_refs["oil_vol"] +
            other_table_refs["ngl_vol"] +
            other_table_refs["coke_mass"])

def calc_product_slate(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
   if row_key == "Coke" and target_table_ref["full_table_name"] == "Refinery_Product_Transport":
       return other_table_refs["opgee_coke_mass"] + other_table_refs["product_slate"][row_key]["Flow"] * other_table_refs["oil_vol_ratio"]["row"]["col"]
   return other_table_refs["product_slate"][row_key]["Flow"] * other_table_refs["oil_vol_ratio"]["row"]["col"]


def calc_sum(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    sum = 0
    # don't use name wrapper for target table, makes reuse difficult.
    for row in target_table_ref.items():
        if row[0] not in ["full_table_name", "row_index_name", "Sum"]:
           sum += row[1][col_key]
    return sum

def lookup_emission_factors_transport(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["transport_em_factors_by_mass"][col_key][row_key]

def calc_total_em(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    #print("")
    return target_table_ref[row_key]["Kilograms of Product per Day"] * target_table_ref[row_key][other_tables_keymap[col_key]] / 1000

def calc_em_intensity(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return target_table_ref[row_key][other_tables_keymap[col_key]] / other_table_refs["row"]["col"]

# NGL transport
def calc_ngl_product_slate(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
   print(row_key)
   return (other_tables_keymap["opgee"][row_key] * 
          other_table_refs[0][other_tables_keymap["constants"]
                                    [row_key]]["Density, grams/gal"] *
          42/1000)

# coke combustion
def fetch_upstream_coke(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
   if other_table_refs["opgee_coke_mass"] == 0:
      
      
      return other_table_refs["product_slate"]["Net Upstream Petcoke"]["Flow"] 
   return other_table_refs["opgee_coke_mass"] 

# natural gas combustion
def fetch_upstream_gas(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
   return other_table_refs["gas_prod_vol"]

# NGL combustion
def fetch_upstream_ngl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Ethane":
        return other_table_refs["ngl_c2_vol"] * (1 - other_table_refs["ngl_c2_percent"])
    return other_table_refs[row_key]

# combustion
def lookup_emission_factors_combustion(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Coke":
        return other_table_refs["CombustionEF::ProductEmFactorsSolid"][extra["fuel_lookup"][row_key]]["Total GHGs (kg CO2eq. per kg petcoke)"]
    else:
        return other_table_refs["CombustionEF::ProductEmFactorsPet"][extra["fuel_lookup"][row_key]]["Total GHGs (kg CO2eq. per bbl)"]

def lookup_emission_factors_nat_gas(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["CombustionEF::ProductEmFactorsNaturalGas"][extra["fuel_lookup"][row_key]]["Total GHGs (kg CO2eq. per scf)"] * 1000
   
    
def lookup_emission_factors_ngl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Sum":
        return other_table_refs[1]["Natural Gas Liquid Average Estimate"]["Total GHGs (kg CO2eq. per bbl)"]
    return other_table_refs[0][row_key]["Total GHGs (kg CO2eq. per bbl)"]

def calc_total_em_combust(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if col_key == "Total Combustion Emissions (kg CO2eq/day)":
       return (target_table_ref[row_key]["Volume or Mass of Product per Day"] *
             target_table_ref[row_key]["Combustion Emission Factors"] *
             target_table_ref[row_key]["% Combusted"])
    if row_key == "Coke":
        emissions = (other_table_refs[1][extra["fuel_lookup"][row_key]]
               [extra["coke_col_lookup"][col_key]] *
                  target_table_ref[row_key]["Volume or Mass of Product per Day"] *
                 target_table_ref[row_key]["% Combusted"] /
                 other_table_refs[2]["kg per short ton"]["Conversion Factor"])
        if col_key == "Total Combustion CO2 Emissions (kg CO2 /day)":
            return emissions
        return emissions / 1000
    result =  (other_table_refs[0][extra["fuel_lookup"][row_key]]
               [extra["col_lookup"][col_key]] *
                  target_table_ref[row_key]["Volume or Mass of Product per Day"] *
                 target_table_ref[row_key]["% Combusted"] * 42)
    if col_key == "Total Combustion CO2 Emissions (kg CO2 /day)":
       return result
    return result / 1000

    
  


def calc_emissions_combustion(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Coke":
        return (target_table_ref["Combustion Results"][row_key]["Combustion Emission Factors"] *
                target_table_ref["Combustion Results"][row_key]["% Combusted"] *
                (other_table_refs["ProductSlate::mass_flow"]["Coke"]["Flow"] +
                 other_table_refs["ProductSlate::mass_flow"]["Net Upstream Petcoke"]["Flow"]) /
                other_table_refs["ProductSlate::volume_flow"]["Barrels of Crude per Day"]["Flow"])
    else:
        return (target_table_ref["Combustion Results"][row_key]["Combustion Emission Factors"] *
                target_table_ref["Combustion Results"][row_key]["% Combusted"] *
                other_table_refs["ProductSlate::volume_flow"][row_key]["Flow"] /
                other_table_refs["ProductSlate::volume_flow"]["Barrels of Crude per Day"]["Flow"])

def calc_total_em_nat_gas(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if col_key == "Total Combustion Emissions (kg CO2eq/day)":
       return (target_table_ref[row_key]["Volume or Mass of Product per Day"] *
             target_table_ref[row_key]["Combustion Emission Factors"] *
             target_table_ref[row_key]["% Combusted"])
    result =  (other_table_refs[0][extra["fuel_lookup"][row_key]]
               [extra["col_lookup"][col_key]] *
                  target_table_ref[row_key]["Volume or Mass of Product per Day"] 
                 )
    if col_key == "Total Combustion CO2 Emissions (kg CO2 /day)":
       return result * 1000
    return result 


def calc_total_em_sum_ngl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if other_table_refs[0] == 1:
        if col_key == "Total Combustion Emissions (kg CO2eq. / day)":
            return (target_table_ref[row_key]["Volume of Product per Day"] * 
                 target_table_ref[row_key]["Combustion Emission Factors"] * 
                 target_table_ref[row_key]["% Combusted"])
        return (other_table_refs[1]["Natural Gas Liquid Average Estimate"][extra[col_key]])
    else:
        em_sum = 0
        for row, col in target_table_ref.items():
            if row not in ["Sum", "full_table_name", "row_index_name"]:
                em_sum += col[col_key]
        return em_sum
# Total Combustion Emissions Table
def sum_all_combust(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return (other_table_refs[0]["Sum"][col_key] +
            other_table_refs[1]["Coke"][col_key] + 
            other_table_refs[2]["Natural Gas"][col_key] +
            other_table_refs[3]["Sum"][col_key]
            )
# non-combusted product emissions
def calc_product_slate_non_combust(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
   if row_key == "Ethane":
       return other_table_refs["ngl_c2"] * other_table_refs["%_allocated_ethylene"]
   return other_table_refs["product_slate"][row_key]["Flow"] * other_table_refs["oil_vol_ratio"]["row"]["col"]

# fetch emissions factors
def fetch_emission_factors_non_combusted(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs

def calc_total_em_non_combust(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if col_key == "Total Process Emissions (kg CO2eq.)":
        return target_table_ref[row_key]["Volume or Mass of Product per Day"] * target_table_ref[row_key]["Emission Factors"]
    petrochem_em = (target_table_ref[row_key]["Volume or Mass of Product per Day"] *
            other_table_refs[0][extra[col_key]]["mass"] / other_table_refs[1]["Natural Gas Liquids"]["bbl (HHV)"])
    if col_key == "Total Process CO2 Emissions (kg CO2)":
        return petrochem_em
    if col_key == "Total Process CH4 Emissions (kg CH4)":
       print("PETROCHEM")
       print(other_table_refs[0][extra[col_key]]["mass"])
       print(other_table_refs[1]["Natural Gas Liquids"]["bbl (HHV)"])
       return petrochem_em/1000
    if col_key == "Total Process N2O Emissions (kg N2O)":
       return petrochem_em/1000000










def calc_transport_sum(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    return sum(other_table_refs["Transport Results"][key][col_key]
               for key, row in other_table_refs["Transport Results"].items() if key not in ["full_table_name", "row_index_name"])


def calc_combustion_sum(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return sum(other_table_refs["Combustion Results"][key][col_key]
               for key, row in other_table_refs["Combustion Results"].items() if key not in ["full_table_name", "row_index_name"])


@dataclass
class OPEM:

    def __post_init__(self, user_input):
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

        # fill_calculated_cells(target_table_ref=self.transport_results,
        #                       func_to_apply=calc_product_slate_combustion_sum,
        #                       included_cols=["Transport Emissions (kg CO2eq. / bbl of crude)"],
        #                       other_table_refs=[self.transport_ef.tanker_barge_ef.share_of_petroleum_products])
        
        # fill calc fields related to OPGEE input
        # calc_gas_production_volume
     
        fill_calculated_cells(target_table_ref=self.gas_production_volume_boed,
                              func_to_apply=calc_gas_production_volume,
                              other_table_refs={"gas_prod_volume": self.opgee_input.gas_production_volume, 
                                                "table_6": self.constants.table_6_boe_conversions})
        print("gas prod volume",self.gas_production_volume_boed)
        # calc_oil_volume_ratio
        fill_calculated_cells(target_table_ref=self.oil_volume_ratio_to_prelim,
                              func_to_apply=calc_oil_volume_ratio,
                              other_table_refs={"oil_volume": self.opgee_input.oil_production_volume, 
                                                "product_slate": self.product_slate.volume_flow_bbl})
            
        # calc_total_field_ngl
        print("before call total field ngl")
        fill_calculated_cells(target_table_ref=self.total_field_ngl_volume,
                              func_to_apply=calc_total_field_ngl,
                              other_table_refs={"ngl_volume_source": self.ngl_volume_source, 
                                                "c2": self.opgee_input.ngl_c2_volume,
                                                "c3": self.opgee_input.ngl_c3_volume,
                                                "c4": self.opgee_input.ngl_c4_volume,
                                                "c5": self.opgee_input.ngl_c5plus_volume})
                        
        # calc_opgee_coke_mass
        fill_calculated_cells(target_table_ref=self.opgee_coke_mass_boed,
                              func_to_apply=calc_opgee_coke_mass,
                              other_table_refs={"coke_mass": self.opgee_input.opgee_coke_mass, 
                                                "table_5": self.constants.table_5_solid_fuel_densities, 
                                                "table_2": self.constants.table_2_conversion_factors})
        # calc_total_boe           
        fill_calculated_cells(target_table_ref=self.total_boe_produced,
                              func_to_apply=calc_total_boe,
                              other_table_refs={"gas_vol": self.gas_production_volume_boed,
                                                "oil_vol": self.opgee_input.oil_production_volume,
                                                "ngl_vol": self.opgee_input.total_field_ngl_volume,
                                                "coke_mass": self.opgee_input.opgee_coke_mass}) 

        # Refinery Transport Table
        # calc_product_slate         
        fill_calculated_cells(target_table_ref=self.refinery_product_transport,
                              func_to_apply=calc_product_slate,
                              included_cols=["Kilograms of Product per Day"],
                              excluded_rows=["Sum"],
                              other_table_refs={"product_slate": self.product_slate.mass_flow_kg,
                                                "oil_vol_ratio": self.oil_volume_ratio_to_prelim,
                                                "opgee_coke_mass": self.opgee_input.opgee_coke_mass}) 
          

        # lookup refinery transport emissions factors
        fill_calculated_cells(target_table_ref={"refinery_prod_trans": self.refinery_product_transport, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_transport,
                              included_cols=["Emissions Factor (g CO2eq/kg product)",
                                             "CO2 Emissions Factor (g CO2/kg product)",
                                             "CH4 Emissions Factor (g CH4/kg product)",
                                             "N2O Emissions Factor (g N2O/kg product)",
                                            ],
                              excluded_rows=["Sum"],
                              other_table_refs={"transport_em_factors_by_mass": self.transport_ef.transport_emissions_by_prod_mass})
       
        # calc total refinery transport emissions for all gasses
        fill_calculated_cells(target_table_ref=self.refinery_product_transport,
                              func_to_apply=calc_total_em,   
                              included_cols=["Total Transport Emissions (kg CO2eq/ day)", 
                                              "Total Transport CO2 Emissions (kg CO2/ day)",
                                              "Total Transport CH4 Emissions (kg CH4/ day)",
                                              "Total Transport N2O Emissions (kg N2O/ day)"],
                              other_tables_keymap={"Total Transport Emissions (kg CO2eq/ day)": "Emissions Factor (g CO2eq/kg product)", 
                                              "Total Transport CO2 Emissions (kg CO2/ day)":  "CO2 Emissions Factor (g CO2/kg product)",
                                              "Total Transport CH4 Emissions (kg CH4/ day)": "CH4 Emissions Factor (g CH4/kg product)",
                                              "Total Transport N2O Emissions (kg N2O/ day)": "N2O Emissions Factor (g N2O/kg product)"},
                              excluded_rows=["Sum"],
                              )
        
        
        
        # calc refinery product emissions intensity for all gasses
        fill_calculated_cells(target_table_ref=self.refinery_product_transport,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Transport Emissions Intensity (kg CO2eq. /BOE)",
                                             "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Transport N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Transport Emissions Intensity (kg CO2eq. /BOE)": "Total Transport Emissions (kg CO2eq/ day)",
                                             "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)": "Total Transport CO2 Emissions (kg CO2/ day)",
                                             "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)": "Total Transport CH4 Emissions (kg CH4/ day)",
                                             "Total Transport N2O Emissions Intensity (kg N2O / BOE)": "Total Transport N2O Emissions (kg N2O/ day)"} ,
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)


        # Refinery transport Sums         
        fill_calculated_cells(target_table_ref=self.refinery_product_transport,
                              func_to_apply=calc_sum,
                              included_cols=["Kilograms of Product per Day", 
                              "Total Transport Emissions (kg CO2eq/ day)",
                              "Transport Emissions Intensity (kg CO2eq. /BOE)",
                              "Total Transport CO2 Emissions (kg CO2/ day)",
                              "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)",
                              "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)",
                              "Total Transport CH4 Emissions (kg CH4/ day)",
                              "Total Transport N2O Emissions (kg N2O/ day)",
                              "Total Transport N2O Emissions Intensity (kg N2O / BOE)"
                              ],
                              included_rows=["Sum"])


        # NGL Transport Table
        print("before calc product slate", self.total_field_ngl_volume)
        # calc_product_slate_ngl         
        fill_calculated_cells(target_table_ref=self.ngl_transport,
                              func_to_apply=calc_ngl_product_slate,
                              included_cols=["Kilograms of Product per Day"],
                              #excluded_rows=["Sum"],
                              other_table_refs=[self.constants.table_3_fuel_specifications_liquid_fuels],
                              other_tables_keymap={"opgee": {"Ethane": self.opgee_input.ngl_c2_volume, 
                                                                "Propane": self.opgee_input.ngl_c3_volume,
                                                                "Butane": self.opgee_input.ngl_c4_volume,
                                                                "Pentanes Plus": self.opgee_input.ngl_c5plus_volume,
                                                                "NGLs": self.total_field_ngl_volume["row"]["col"]},
                                                    "constants": {"Ethane":"Propane",
                                                                  "Propane": "Propane",
                                                                  "Butane": "Butane",
                                                                  "Pentanes Plus": "n-Hexane",
                                                                  "NGLs": "Natural gas liquids"
                                                    }}) 
          

        # lookup ngl transport emissions factors
        fill_calculated_cells(target_table_ref=self.ngl_transport,
                              func_to_apply=lookup_emission_factors_transport,
                              included_cols=["Emissions Factor (g CO2eq/kg product)",
                                             "CO2 Emissions Factor (g CO2/kg product)",
                                             "CH4 Emissions Factor (g CH4/kg product)",
                                             "N2O Emissions Factor (g N2O/kg product)",
                                            ],
                             
                              other_table_refs={"transport_em_factors_by_mass": self.transport_ef.transport_emissions_by_prod_mass})
       
        # calc total ngl transport emissions for all gasses
        fill_calculated_cells(target_table_ref=self.ngl_transport,
                              func_to_apply=calc_total_em,   
                              included_cols=["Total Transport Emissions (kg CO2eq/ day)", 
                                              "Total Transport CO2 Emissions (kg CO2/ day)",
                                              "Total Transport CH4 Emissions (kg CH4/ day)",
                                              "Total Transport N2O Emissions (kg N2O/ day)"],
                              other_tables_keymap={"Total Transport Emissions (kg CO2eq/ day)": "Emissions Factor (g CO2eq/kg product)", 
                                              "Total Transport CO2 Emissions (kg CO2/ day)":  "CO2 Emissions Factor (g CO2/kg product)",
                                              "Total Transport CH4 Emissions (kg CH4/ day)": "CH4 Emissions Factor (g CH4/kg product)",
                                              "Total Transport N2O Emissions (kg N2O/ day)": "N2O Emissions Factor (g N2O/kg product)"},
                              
                              )
        
        
        
        # calc ngl emissions intensity for all gasses
        fill_calculated_cells(target_table_ref=self.ngl_transport,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Transport Emissions Intensity (kg CO2eq. /BOE)",
                                             "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Transport N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Transport Emissions Intensity (kg CO2eq. /BOE)": "Total Transport Emissions (kg CO2eq/ day)",
                                             "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)": "Total Transport CO2 Emissions (kg CO2/ day)",
                                             "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)": "Total Transport CH4 Emissions (kg CH4/ day)",
                                             "Total Transport N2O Emissions Intensity (kg N2O / BOE)": "Total Transport N2O Emissions (kg N2O/ day)"} ,
                             
                              other_table_refs=self.total_boe_produced)


        # NGL transport Sums         
        if self.ngl_volume_source == 1:
           fill_calculated_cells(target_table_ref=self.refinery_product_transport,
                              func_to_apply=calc_sum,
                              included_cols=[
                              "Total Transport Emissions (kg CO2eq/ day)",
                              "Transport Emissions Intensity (kg CO2eq. /BOE)",
                              "Total Transport CO2 Emissions (kg CO2/ day)",
                              "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)",
                              "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)",
                              "Total Transport CH4 Emissions (kg CH4/ day)",
                              "Total Transport N2O Emissions (kg N2O/ day)",
                              "Total Transport N2O Emissions Intensity (kg N2O / BOE)"
                              ],
                              included_rows=["NGLs"])

        # refinery product combustion
        # calc_product_slate refinery combustion         
        fill_calculated_cells(target_table_ref=self.refinery_product_combustion,
                              func_to_apply=calc_product_slate,
                              included_cols=["Volume or Mass of Product per Day"],
                              excluded_rows=["Sum"],
                              other_table_refs={"product_slate": self.product_slate.volume_flow_bbl,
                                                "oil_vol_ratio": self.oil_volume_ratio_to_prelim,
                                                "opgee_coke_mass": self.opgee_input.opgee_coke_mass}) 
        
        # look up combustion factors
        fill_calculated_cells(target_table_ref={"Combustion Results": self.refinery_product_combustion, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_combustion,
                              included_cols=["Combustion Emission Factors"],
                              excluded_rows=[
                                  "Sum"],
                              other_table_refs={"CombustionEF::ProductEmFactorsPet": self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                "CombustionEF::ProductEmFactorsSolid": self.combustion_ef.product_combustion_emission_factors_derived_solids},
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)"
                                                     }})
        # calc combustion emissions
        fill_calculated_cells(target_table_ref=self.refinery_product_combustion,
                              func_to_apply=calc_total_em_combust,
                              included_cols=["Total Combustion Emissions (kg CO2eq/day)", 
                                             "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions (kg N2O/ day)"],
                              excluded_rows=[
                                  "Sum"],
                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                self.combustion_ef.product_combustion_emission_factors_derived_solids,
                                                self.constants.table_2_conversion_factors],
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)"
                                                     },
                                    "coke_col_lookup": {"Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per ton",
                                                        "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per ton",
                                                        "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per ton"},
                                    "col_lookup": {
                                        "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per gallon",
                                        "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per gallon",
                                        "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per gallon"
                                    }})

        # calc refinery product combustion emissions intensity for all gasses
        fill_calculated_cells(target_table_ref=self.refinery_product_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"} ,
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)
        
        # Refinery combustion Sums         
        fill_calculated_cells(target_table_ref=self.refinery_product_combustion,
                              func_to_apply=calc_sum,
                              included_cols=["Volume or Mass of Product per Day", 
                              "Total Combustion Emissions (kg CO2eq/day)",
                              "Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                              "Total Combustion CO2 Emissions (kg CO2 /day)",
                              "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                              "Total Combustion CH4 Emissions (kg CH4/ day)",
                              "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                              "Total Combustion N2O Emissions (kg N2O/ day)",
                              "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"
                              ],
                              included_rows=["Sum"])
           

        # coke combustion 
        fill_calculated_cells(target_table_ref=self.coke_combustion,
                              func_to_apply=fetch_upstream_coke,
                              included_cols=["Volume or Mass of Product per Day"],
                              #excluded_rows=["Sum"],
                              other_table_refs={"product_slate": self.product_slate.mass_flow_kg,
                                                "opgee_coke_mass": self.opgee_input.opgee_coke_mass})
        
        # look up combustion factors
        fill_calculated_cells(target_table_ref={"Combustion Results": self.coke_combustion, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_combustion,
                              included_cols=["Combustion Emission Factors"],

                              other_table_refs={"CombustionEF::ProductEmFactorsPet": self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                "CombustionEF::ProductEmFactorsSolid": self.combustion_ef.product_combustion_emission_factors_derived_solids},
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)"
                                                     }})


        # calc combustion emissions coke
        fill_calculated_cells(target_table_ref=self.coke_combustion,
                              func_to_apply=calc_total_em_combust,
                              included_cols=["Total Combustion Emissions (kg CO2eq/day)", 
                                             "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions (kg N2O/ day)"],
                              excluded_rows=[
                                  "Sum"],
                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_natural_gas,
                                                self.combustion_ef.product_combustion_emission_factors_derived_solids,
                                                self.constants.table_2_conversion_factors],
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)"
                                                     },
                                    "coke_col_lookup": {"Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per ton",
                                                        "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per ton",
                                                        "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per ton"},
                                    "col_lookup": {
                                        "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per scf",
                                        "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per scf",
                                        "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per scf"
                                    }})

        # calc coke combustion emissions intensity for all gasses
        fill_calculated_cells(target_table_ref=self.coke_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"} ,
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)


        # Natural Gas
        # Lookup volume flow
        fill_calculated_cells(target_table_ref=self.natural_gas_combustion,
                              func_to_apply=fetch_upstream_gas,
                              included_cols=["Volume or Mass of Product per Day"],
                              #excluded_rows=["Sum"],
                              other_table_refs={"gas_prod_vol": self.gas_production_volume_boed["row"]["col"]})

        # look up combustion factors
        fill_calculated_cells(target_table_ref={"Combustion Results": self.natural_gas_combustion, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_nat_gas,
                              included_cols=["Combustion Emission Factors"],

                              other_table_refs={"CombustionEF::ProductEmFactorsNaturalGas": self.combustion_ef.product_combustion_emission_factors_natural_gas},
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)",
                                                     "Natural Gas": "Natural Gas"
                                                     }}) 
        
        # calc combustion emissions natural gas
        fill_calculated_cells(target_table_ref=self.natural_gas_combustion,
                              func_to_apply=calc_total_em_nat_gas,
                              included_cols=["Total Combustion Emissions (kg CO2eq/day)", 
                                             "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions (kg N2O/ day)"],
                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_natural_gas,
                                                self.combustion_ef.product_combustion_emission_factors_derived_solids,
                                                self.constants.table_2_conversion_factors],
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)",
                                                     "Natural Gas": "Natural Gas"
                                                     },
                                    "coke_col_lookup": {"Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per ton",
                                                        "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per ton",
                                                        "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per ton"},
                                    "col_lookup": {
                                        "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per scf",
                                        "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per scf",
                                        "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per scf"
                                    }})

        # emissions intensity Natural Gas
        fill_calculated_cells(target_table_ref=self.natural_gas_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"} ,
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)


        # NGL Combustion
        # Lookup volume flow
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=fetch_upstream_ngl,
                              included_cols=["Volume or Mass of Product per Day"],
                              other_table_refs={"ngl_c2_vol": self.opgee_input.ngl_c2_volume,
                                                "ngl_c2_percent": self.percent_ngl_c2_to_ethylene,
                                                "Propane": self.opgee_input.ngl_c3_volume,
                                                "Butane": self.opgee_input.ngl_c4_volume,
                                                "Pentanes Plus": self.opgee_input.ngl_c5plus_volume,
                                                "Sum": self.total_field_ngl_volume["row"]["col"]})
        # lookup emissions factors
        # look up combustion factors
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=lookup_emission_factors_ngl,
                              included_cols=["Combustion Emission Factors"],

                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                self.combustion_ef.ngl_estimate]) 

        # calc combustion emissions ngl
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=calc_total_em_combust,
                              excluded_rows=["Sum"],
                              included_cols=["Total Combustion Emissions (kg CO2eq/day)", 
                                             "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions (kg N2O/ day)"],
                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                self.combustion_ef.product_combustion_emission_factors_derived_solids,
                                                self.constants.table_2_conversion_factors],
                              extra={"fuel_lookup": {"Ethane": "Ethane",
                                                    "Propane": "Propane",
                                                    "Butane": "Butane",
                                                    "Pentanes Plus": "Pentanes Plus"
                                                     },
                                    "coke_col_lookup": {"Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per ton",
                                                        "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per ton",
                                                        "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per ton"},
                                    "col_lookup": {
                                        "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per gallon",
                                        "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per gallon",
                                        "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per gallon"
                                    }}) 
       
        # emissions intensity NGL
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"} ,
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)

        # sum ngl
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=calc_total_em_sum_ngl,
                              included_cols=[
                              "Total Combustion Emissions (kg CO2eq/day)",
                              "Total Combustion CO2 Emissions (kg CO2 /day)",
                              "Total Combustion CH4 Emissions (kg CH4/ day)",
                              "Total Combustion N2O Emissions (kg N2O/ day)",
                              ],
                              included_rows=["Sum"],
                              other_table_refs=[self.ngl_volume_source, self.combustion_ef.ngl_estimate],
                              extra={
                                        "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per gallon",
                                        "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per gallon",
                                        "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per gallon"
                                    }
                              )
        # emissions intensity NGL SUM
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"} ,
                              included_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)

        # Total Combustion Emissions
        fill_calculated_cells(target_table_ref=self.total_combustion_emissions,
                              func_to_apply=sum_all_combust,
                              other_table_refs=[self.refinery_product_combustion,
                              self.coke_combustion,
                              self.natural_gas_combustion,
                              self.ngl_combustion],)
            
        # Non-combusted Product emissions
        # calc_product_slate         
        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=calc_product_slate_non_combust,
                              included_cols=["Volume or Mass of Product per Day"],
                              excluded_rows=["Sum"],
                              other_table_refs={"product_slate": self.product_slate.volume_flow_bbl,
                                                "oil_vol_ratio": self.oil_volume_ratio_to_prelim,
                                                "opgee_coke_mass": self.opgee_input.opgee_coke_mass,
                                                "ngl_c2": self.opgee_input.ngl_c2_volume,
                                                "%_allocated_ethylene": self.percent_ngl_c2_to_ethylene}) 
        
        # lookup emission factors non-combusted products
        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=fetch_emission_factors_non_combusted,
                              included_cols=["Emission Factors"],
                              excluded_rows=["Sum"],
                              other_table_refs=self.petrochem_ef.ethylene_conversion_100yr_gwp["Sum"]["kg CO2e/bbl Natural Gas Liquids (HHV)"])  
      
        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=calc_total_em_non_combust,
                              included_cols=["Total Process Emissions (kg CO2eq.)",
                                             "Total Process CO2 Emissions (kg CO2)",      
                                             "Total Process CH4 Emissions (kg CH4)",
                                             "Total Process N2O Emissions (kg N2O)"],
                              excluded_rows=["Sum"],
                              extra={"Total Process CO2 Emissions (kg CO2)": "CO2",      
                                             "Total Process CH4 Emissions (kg CH4)": "CH4",
                                             "Total Process N2O Emissions (kg N2O)": "N2O"},
                              other_table_refs=[self.petrochem_ef.ethylene_conversion_kg_co2e,
                                                self.petrochem_ef.onsite_energy_inputs])  
     
        # emissions intensity non-combusted
        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Process Emissions Intensity (kg CO2eq./boe total",
                                             "Total Process CO2 Emissions Intensity (kg CO2/boe total)",      
                                             "Total ProcessCH4  Emissions Intensity (kg CH4/boe total)",
                                             "Total Process N2O Emissions Intensity (kg N2O./boe total)"],
                              other_tables_keymap={"Total Process Emissions Intensity (kg CO2eq./boe total": "Total Process Emissions (kg CO2eq.)",
                                             "Total Process CO2 Emissions Intensity (kg CO2/boe total)": "Total Process CO2 Emissions (kg CO2)",      
                                             "Total ProcessCH4  Emissions Intensity (kg CH4/boe total)": "Total Process CH4 Emissions (kg CH4)",
                                             "Total Process N2O Emissions Intensity (kg N2O./boe total)": "Total Process N2O Emissions (kg N2O)"} ,
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)
        # non-combusted sum
        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=calc_sum,
                              included_cols=[
                              "Volume or Mass of Product per Day",
                              "Total Process Emissions Intensity (kg CO2eq./boe total",
                              "Total Process CO2 Emissions Intensity (kg CO2/boe total)",      
                              "Total ProcessCH4  Emissions Intensity (kg CH4/boe total)",
                              "Total Process N2O Emissions Intensity (kg N2O./boe total)",
                              "Total Process Emissions (kg CO2eq.)",
                              "Total Process CO2 Emissions (kg CO2)",      
                              "Total Process CH4 Emissions (kg CH4)",
                              "Total Process N2O Emissions (kg N2O)" 
                              ],
                              included_rows=["Sum"])
    
 
        
        # fill_calculated_cells(target_table_ref={"Transport Results": self.transport_results, "has_wrapper": True},
        #                       func_to_apply=calc_emissions_transport,
        #                       included_cols=[
        #                           "Transport Emissions (kg CO2eq. / bbl of crude)"],
        #                       other_table_refs={"TankerBargeEF::ShareOfPetProducts": self.transport_ef.tanker_barge_ef.share_of_petroleum_products})

        # fill_calculated_cells(target_table_ref={"Combustion Results": self.combustion_results, "has_wrapper": True},
        #                       func_to_apply=calc_emissions_combustion,
        #                       other_table_refs={"ProductSlate::mass_flow": self.product_slate.mass_flow_kg,
        #                                         "ProductSlate::volume_flow": self.product_slate.volume_flow_bbl},
        #                       included_cols=["Total Combustion Emissions (kg CO2eq. / bbl of crude)"])

        # fill_calculated_cells(target_table_ref={"Transport Sum": self.transport_sum, "has_wrapper": True},
        #                       func_to_apply=calc_transport_sum,
        #                       other_table_refs={"Transport Results": self.transport_results})

        # fill_calculated_cells(target_table_ref={"Combustion Sum": self.combustion_sum, "has_wrapper": True},
        #                       func_to_apply=calc_combustion_sum,
        #                       other_table_refs={"Combustion Results": self.combustion_results})

    # def results(self):
    #     # should move mass flow total to a higher level object. It is strangle to
    #     # find it only in the tanker_barge object.
    #     return [["Output Name", "Value"],
    #             ["--OPEM Transport--", ""],
    #             ["Sum: Kilograms of Product per Day",
    #                 self.transport_ef.tanker_barge_ef.share_of_petroleum_products["mass_flow_sum"]["total"]],
    #             ["Transport Emissions (kg CO2eq. / bbl of crude)", ""],
    #             ["Pipeline Emissions", self.transport_results["Pipeline Emissions"]
    #                 ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Rail Emissions", self.transport_results["Rail Emissions"]
    #                 ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Heavy-Duty Truck Emissions", self.transport_results["Heavy-Duty Truck Emissions"]
    #                 ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Ocean Tanker Emissions", self.transport_results["Ocean Tanker Emissions"]
    #                 ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Barge Emissions", self.transport_results["Barge Emissions"]
    #                 ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Sum", self.transport_sum["Sum"]
    #                 ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Sum Distance Travelled", self.transport_sum["Sum"]
    #                 ["Select Distance Traveled (km)"]],
    #             ["--OPEM Combustion--", ""],
    #             ["Total Combustion Emissions (kg CO2eq. / bbl of crude)", ""],
    #             ["Gasoline", self.combustion_results["Gasoline"]
    #                 ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Jet Fuel", self.combustion_results["Jet Fuel"]
    #                 ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Diesel", self.combustion_results["Diesel"]
    #                 ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Fuel Oil", self.combustion_results["Fuel Oil"]
    #                 ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Coke", self.combustion_results["Coke"]
    #                 ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Residual fuels", self.combustion_results["Residual fuels"]
    #                 ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Liquefied Petroleum Gases (LPG)", self.combustion_results["Liquefied Petroleum Gases (LPG)"]
    #              ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
    #             ["Sum", self.combustion_sum["Sum"]["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]]]
    constants: Constants
    transport_ef: TransportEF
    petrochem_ef: PetroChemEF
    combustion_ef: CombustionEF
    product_slate: ProductSlate
    opgee_input: OpgeeInput

    # calculate these in post_init
    gas_production_volume_boed: Dict = field(
        default_factory=lambda: {"row": { "col": None }})
    oil_volume_ratio_to_prelim: Dict = field(
        default_factory=lambda:{"row": { "col": None }})
    total_field_ngl_volume: Dict = field(
        default_factory=lambda:{"row": { "col": None }})
    opgee_coke_mass_boed: Dict = field(
        default_factory=lambda:{"row": { "col": None }})
    total_boe_produced: Dict = field(
        default_factory=lambda:{"row": { "col": None }})

    # fill from user_input_dto
    # DTO CAN"T FILL
    ngl_volume_source: int = None
    percent_ngl_c2_to_ethylene: int = None
 

    # will this cause problems if I try to pass in a list?
    user_input: InitVar[Dict] = {}

    # User Inputs & Results sheet, table: OPEM Transport
    # USER INPUT
    # CALCULATED
    refinery_product_transport: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Refinery_Product_Transport', 'results'))

    # User Inputs & Results sheet, table: OPEM Transport
    # CALCULATED
    ngl_transport: Dict = field(
        default_factory=lambda: build_dict_from_defaults('NGL_Transport', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    refinery_product_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Refinery_Product_Combustion', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    coke_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Coke_Combustion', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    natural_gas_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Natural_Gas_Combustion', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    ngl_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults('NGL_Combustion', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # CALCULATED
    total_combustion_emissions: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Total_Combustion_Emissions', 'results'))

    # User Inputs & Results sheet, table: Non-combusted Product Emissions
    # CALCULATED
    non_combusted_product_emissions: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Non_Combusted_Product_Emissions', 'results'))

    # hold sum of product volume from product slate here
    # product_volume_sum: int = None


@dataclass
class CombustionResults:
    pass


# @dataclass
# class ResultsDto:
#     transport: TransportResults
#     combustion: CombustionResults
#     opem_total: float


# def run_model():
#     # orchestrator function
#     # will call input functions,
#     # initialize EF objects
#     # and calculate opem
#     # main should call this function when it is ready.
#     user_params = input.initialize_model_inputs(
#         input.get_csv_input, input.validate_input)
#     product_slate = input.get_product_slate('test')

#     calculate_opem()


def calculate_opem_transport(user_input):
    # -> TransportResults:
    # instantiate all transport model EF objects (using the input dto),
    # pull required params for each object out of the generic user params input
    # object by turning the input object in a dictionary and using
    # TransportObj(for key in transport_obj.properties: input_dict[key])
    # then use them to instantiate total transport EF object
    # then us the Transport EF object, the product slate, and the input dto to
    # create the results object
    return TransportEF(user_input=user_input)


# def calculate_opem() -> ResultsDto:

#     calculate_opem_transport():

#     caclulate_opem_combustion():
