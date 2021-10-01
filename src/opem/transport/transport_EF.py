from dataclasses import InitVar, dataclass, field
from typing import Dict
from opem.transport.heavy_duty_truck_EF import HeavyDutyTruckEF
from opem.transport.pipeline_EF import PipelineEF
from opem.transport.rail_EF import RailEF
from opem.transport.tanker_barge_EF import TankerBargeEF
from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

from math import isnan

# verify that user input for fuel shares sum to 1 for each fuel


def verify_user_fuel_shares(user_shares):
    for key, row in user_shares.items():
        if key not in ["full_table_name", "row_index_name"]:
            share_sum = sum(share for share in row.values()
                            if not isnan(share))
            if share_sum != 1:
                raise(ValueError(
                    f'Shares of fuel types for {key} do not add to 1. Sum is {share_sum}'))

# Define functions for filling calculated cells in the tables here


def calc_manual_fuel_share_ave(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    sum = 0 
    for col, val in target_table_ref[row_key].items():
        if val and (col != "Manual Fuel Share averaged"):
           if not isnan(other_table_refs["fuel_share"][other_tables_keymap[row_key]][col]): 
              sum += val * other_table_refs["fuel_share"][other_tables_keymap[row_key]][col]
    return sum


def calc_emission_factors(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    # print(other_table_refs[extra[row_key][0]][extra[row_key][1]].items())
    fuel_sum = 0
    for col, val in other_table_refs[extra["keymap"][row_key][0]][extra["keymap"][row_key][1]].items():
        fuel_fraction = other_table_refs[0][row_key].get((lambda col:
                                                          extra["fuel_lookup"][col] if col in extra["fuel_lookup"].keys() else col)(col))

        if fuel_fraction is not None and not isnan(fuel_fraction):
            fuel_sum += val * fuel_fraction
    return fuel_sum

#def lookup_emission_factors_other_co2eq(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

def lookup_emission_factors_other(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    for fuel_name in other_table_refs[extra["keymap"][row_key][0]][extra["keymap"][row_key][1]].keys():

        if extra["fuel_lookup"].get(fuel_name):
            if col_key == extra["fuel_lookup"].get(fuel_name):
                col_key = fuel_name
    return other_table_refs[extra["keymap"][row_key][0]][extra["keymap"][row_key][1]].get(col_key)

def lookup_emission_factors_tanker_barge(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if col_key in other_table_refs[0][row_key].keys():
        return other_table_refs[0][row_key][col_key]
def cal_emissions_by_mass(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    sum = 0
    for row in other_table_refs["transport_distance"].items():
        if row[0] not in ["full_table_name", "row_index_name"] and not isnan(row[1][col_key]):
          if row[0] == "Ocean Tanker":
               if col_key in other_table_refs["factors_by_fuel_tanker"].keys(): 
                   result = row[1][col_key] * other_table_refs["factors_by_fuel_tanker"][col_key]["Manual Fuel Share averaged"]
                  
                   if not isnan(result):
                       
                       sum += result
          elif row[0] == "Barge":
               if col_key in other_table_refs["factors_by_fuel_barge"].keys():
                   result = row[1][col_key] * other_table_refs["factors_by_fuel_barge"][col_key]["Manual Fuel Share averaged"]
                  
                   if not isnan(result):
                      
                       sum += result
          else:
               result = row[1][col_key] * other_table_refs["factors_by_fuel_other"][row[0]]["Manual Fuel Share averaged"]
             
               if not isnan(result):
                    
                    sum += result 
    return sum 
@dataclass
class TransportEF:

    def __post_init__(self, user_input):
        # calculate_transport_ef()

        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")
        verify_user_fuel_shares(self.fraction_of_fuel_type_for_transport_mode)

        # fill_calculated_cells(target_table_ref=self.transport_emission_factors_weighted_average,
        #                       func_to_apply=calc_emission_factors,
        #                       included_cols=["Manual Fuel Share averaged"],
        #                       # extra holds two dicts, map from target to other table
        #                       # and a lookup table to standardize fuel names
        #                       # maps row in target table to a tuple (index_into_other_table_ref_array, row_in_other_table)
        #                       extra={"fuel_lookup": {"NG": "Natural Gas"
        #                                              },
        #                              "keymap": {"Pipeline": (1, "Pipeline"),
        #                                         "Rail": (2, "Rail Emissions"),
        #                                         "Heavy-Duty Truck": (3, "Heavy-Duty Truck Emissions (full load)")}},
                                                
        #                       other_table_refs=[self.fraction_of_fuel_type_for_transport_mode,
        #                                         self.pipeline_ef.pipeline_emission_factors,
        #                                         self.rail_ef.rail_emission_factors,
        #                                         self.heavy_duty_truck_ef.heavy_duty_truck_emission_factors,
        #    
        #                                      self.tanker_barge_ef.tanker_barge_emission_factors])
        
        # CO2eq 
        # other modes
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_other_co2eq,
                              func_to_apply=lookup_emission_factors_other,
                              excluded_cols=["Manual Fuel Share averaged"],
                              # extra holds two dicts, map from target to other table
                              # and a lookup table to standardize fuel names
                              # maps row in target table to a tuple (index_into_other_table_ref_array, row_in_other_table)
                              extra={"fuel_lookup": {"NG": "Natural Gas"

                                                     },
                                     "keymap": {"Pipeline": (0, "Pipeline"),
                                                "Rail": (1, "Rail Emissions"),
                                                "Heavy-Duty Truck": (2, "Heavy-Duty Truck Emissions (full load)")}},
                              other_table_refs=[
                                                self.pipeline_ef.pipeline_emission_factors_co2eq,
                                                self.rail_ef.rail_emission_factors_co2eq,
                                                self.heavy_duty_truck_ef.heavy_duty_truck_emission_factors_co2eq,
                                                ])
        # other modes sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_other_co2eq,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Pipeline": "Pipeline", 
                                                    "Rail": "Rail",
                                                    "Heavy-Duty Truck": "Heavy-Duty Truck",
                                                    })
        # tanker barge   
        # Tanker                             
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_tanker_co2eq,
                              func_to_apply=lookup_emission_factors_tanker_barge,
                              excluded_cols=["Manual Fuel Share averaged"],
                              other_table_refs=[
                                                self.tanker_barge_ef.tanker_emission_factors_co2eq
                                                ])
        # tanker sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_tanker_co2eq,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Gasoline": "Ocean Tanker",
                                                   "Diesel": "Ocean Tanker",
                                                   "Jet Fuel": "Ocean Tanker",
                                                   "Residual Oil": "Ocean Tanker",
                                                   "Petcoke": "Ocean Tanker",
                                                   "Liquefied Petroleum Gases (LPG)": "Ocean Tanker"})

        # Barge                             
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_barge_co2eq,
                              func_to_apply=lookup_emission_factors_tanker_barge,
                              excluded_cols=["Manual Fuel Share averaged"],
                              other_table_refs=[
                                                self.tanker_barge_ef.barge_emission_factors_co2eq
                                                ])
        # barge sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_barge_co2eq,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Gasoline": "Barge",
                                                   "Diesel": "Barge",
                                                   "Jet Fuel": "Barge",
                                                   "Residual Oil": "Barge",
                                                   "Petcoke": "Barge",
                                                   "Liquefied Petroleum Gases (LPG)": "Barge"})
        # emissions by product mass
        fill_calculated_cells(target_table_ref=self.transport_emissions_by_prod_mass,
                              func_to_apply=cal_emissions_by_mass,
                              included_rows=["Emissions Factor (g CO2eq/kg product)"],
                              other_table_refs={"factors_by_fuel_other": self.transport_emission_factors_other_co2eq,
                                                "factors_by_fuel_tanker": self.transport_emission_factors_tanker_co2eq,
                                                "factors_by_fuel_barge": self.transport_emission_factors_barge_co2eq,
                                                "transport_distance": self.transport_distance}) 
        # CO2
        # other modes
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_other_co2,
                              func_to_apply=lookup_emission_factors_other,
                              excluded_cols=["Manual Fuel Share averaged"],
                              # extra holds two dicts, map from target to other table
                              # and a lookup table to standardize fuel names
                              # maps row in target table to a tuple (index_into_other_table_ref_array, row_in_other_table)
                              extra={"fuel_lookup": {"NG": "Natural Gas"

                                                     },
                                     "keymap": {"Pipeline": (0, "Pipeline"),
                                                "Rail": (1, "Rail Emissions"),
                                                "Heavy-Duty Truck": (2, "Heavy-Duty Truck Emissions (full load)")}},
                              other_table_refs=[
                                                self.pipeline_ef.pipeline_emission_factors_co2,
                                                self.rail_ef.rail_emission_factors_co2,
                                                self.heavy_duty_truck_ef.heavy_duty_truck_emission_factors_co2,
                                                ])
        # other modes sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_other_co2,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Pipeline": "Pipeline", 
                                                    "Rail": "Rail",
                                                    "Heavy-Duty Truck": "Heavy-Duty Truck",
                                                    })
        # tanker barge   
        # Tanker                             
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_tanker_co2,
                              func_to_apply=lookup_emission_factors_tanker_barge,
                              excluded_cols=["Manual Fuel Share averaged"],
                              other_table_refs=[
                                                self.tanker_barge_ef.tanker_emission_factors_co2
                                                ])
        # tanker sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_tanker_co2,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Gasoline": "Ocean Tanker",
                                                   "Diesel": "Ocean Tanker",
                                                   "Jet Fuel": "Ocean Tanker",
                                                   "Residual Oil": "Ocean Tanker",
                                                   "Petcoke": "Ocean Tanker",
                                                   "Liquefied Petroleum Gases (LPG)": "Ocean Tanker"})

        # Barge                             
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_barge_co2,
                              func_to_apply=lookup_emission_factors_tanker_barge,
                              excluded_cols=["Manual Fuel Share averaged"],
                              other_table_refs=[
                                                self.tanker_barge_ef.barge_emission_factors_co2
                                                ])
        # barge sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_barge_co2,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Gasoline": "Barge",
                                                   "Diesel": "Barge",
                                                   "Jet Fuel": "Barge",
                                                   "Residual Oil": "Barge",
                                                   "Petcoke": "Barge",
                                                   "Liquefied Petroleum Gases (LPG)": "Barge"})
        # emissions by product mass
        fill_calculated_cells(target_table_ref=self.transport_emissions_by_prod_mass,
                              func_to_apply=cal_emissions_by_mass,
                              included_rows=["CO2 Emissions Factor (g CO2/kg product)"],
                              other_table_refs={"factors_by_fuel_other": self.transport_emission_factors_other_co2,
                                                "factors_by_fuel_tanker": self.transport_emission_factors_tanker_co2,
                                                "factors_by_fuel_barge": self.transport_emission_factors_barge_co2,
                                                "transport_distance": self.transport_distance}) 
        
        # CH4
        # other modes
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_other_ch4,
                              func_to_apply=lookup_emission_factors_other,
                              excluded_cols=["Manual Fuel Share averaged"],
                              # extra holds two dicts, map from target to other table
                              # and a lookup table to standardize fuel names
                              # maps row in target table to a tuple (index_into_other_table_ref_array, row_in_other_table)
                              extra={"fuel_lookup": {"NG": "Natural Gas"

                                                     },
                                     "keymap": {"Pipeline": (0, "Pipeline"),
                                                "Rail": (1, "Rail Emissions"),
                                                "Heavy-Duty Truck": (2, "Heavy-Duty Truck Emissions (full load)")}},
                              other_table_refs=[
                                                self.pipeline_ef.pipeline_emission_factors_ch4,
                                                self.rail_ef.rail_emission_factors_ch4,
                                                self.heavy_duty_truck_ef.heavy_duty_truck_emission_factors_ch4,
                                                ])
        # other modes sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_other_ch4,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Pipeline": "Pipeline", 
                                                    "Rail": "Rail",
                                                    "Heavy-Duty Truck": "Heavy-Duty Truck",
                                                    })
        # tanker barge   
        # Tanker                             
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_tanker_ch4,
                              func_to_apply=lookup_emission_factors_tanker_barge,
                              excluded_cols=["Manual Fuel Share averaged"],
                              other_table_refs=[
                                                self.tanker_barge_ef.tanker_emission_factors_ch4
                                                ])
        # tanker sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_tanker_ch4,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Gasoline": "Ocean Tanker",
                                                   "Diesel": "Ocean Tanker",
                                                   "Jet Fuel": "Ocean Tanker",
                                                   "Residual Oil": "Ocean Tanker",
                                                   "Petcoke": "Ocean Tanker",
                                                   "Liquefied Petroleum Gases (LPG)": "Ocean Tanker"})

        # Barge                             
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_barge_ch4,
                              func_to_apply=lookup_emission_factors_tanker_barge,
                              excluded_cols=["Manual Fuel Share averaged"],
                              other_table_refs=[
                                                self.tanker_barge_ef.barge_emission_factors_ch4
                                                ])
        # barge sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_barge_ch4,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Gasoline": "Barge",
                                                   "Diesel": "Barge",
                                                   "Jet Fuel": "Barge",
                                                   "Residual Oil": "Barge",
                                                   "Petcoke": "Barge",
                                                   "Liquefied Petroleum Gases (LPG)": "Barge"})
        # emissions by product mass
        fill_calculated_cells(target_table_ref=self.transport_emissions_by_prod_mass,
                              func_to_apply=cal_emissions_by_mass,
                              included_rows=["CH4 Emissions Factor (g CH4/kg product)"],
                              other_table_refs={"factors_by_fuel_other": self.transport_emission_factors_other_ch4,
                                                "factors_by_fuel_tanker": self.transport_emission_factors_tanker_ch4,
                                                "factors_by_fuel_barge": self.transport_emission_factors_barge_ch4,
                                                "transport_distance": self.transport_distance}) 

        # N2O
        # other modes
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_other_n2o,
                              func_to_apply=lookup_emission_factors_other,
                              excluded_cols=["Manual Fuel Share averaged"],
                              # extra holds two dicts, map from target to other table
                              # and a lookup table to standardize fuel names
                              # maps row in target table to a tuple (index_into_other_table_ref_array, row_in_other_table)
                              extra={"fuel_lookup": {"NG": "Natural Gas"

                                                     },
                                     "keymap": {"Pipeline": (0, "Pipeline"),
                                                "Rail": (1, "Rail Emissions"),
                                                "Heavy-Duty Truck": (2, "Heavy-Duty Truck Emissions (full load)")}},
                              other_table_refs=[
                                                self.pipeline_ef.pipeline_emission_factors_n2o,
                                                self.rail_ef.rail_emission_factors_n2o,
                                                self.heavy_duty_truck_ef.heavy_duty_truck_emission_factors_n2o,
                                                ])
        # other modes sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_other_n2o,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Pipeline": "Pipeline", 
                                                    "Rail": "Rail",
                                                    "Heavy-Duty Truck": "Heavy-Duty Truck",
                                                    })
        # tanker barge   
        # Tanker                             
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_tanker_n2o,
                              func_to_apply=lookup_emission_factors_tanker_barge,
                              excluded_cols=["Manual Fuel Share averaged"],
                              other_table_refs=[
                                                self.tanker_barge_ef.tanker_emission_factors_n2o
                                                ])
        # tanker sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_tanker_n2o,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Gasoline": "Ocean Tanker",
                                                   "Diesel": "Ocean Tanker",
                                                   "Jet Fuel": "Ocean Tanker",
                                                   "Residual Oil": "Ocean Tanker",
                                                   "Petcoke": "Ocean Tanker",
                                                   "Liquefied Petroleum Gases (LPG)": "Ocean Tanker"})

        # Barge                             
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_barge_n2o,
                              func_to_apply=lookup_emission_factors_tanker_barge,
                              excluded_cols=["Manual Fuel Share averaged"],
                              other_table_refs=[
                                                self.tanker_barge_ef.barge_emission_factors_n2o
                                                ])
        # barge sum
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_barge_n2o,
                              func_to_apply=calc_manual_fuel_share_ave,
                              included_cols=["Manual Fuel Share averaged"],
                              other_table_refs = {"fuel_share": self.fraction_of_fuel_type_for_transport_mode},
                              other_tables_keymap={"Gasoline": "Barge",
                                                   "Diesel": "Barge",
                                                   "Jet Fuel": "Barge",
                                                   "Residual Oil": "Barge",
                                                   "Petcoke": "Barge",
                                                   "Liquefied Petroleum Gases (LPG)": "Barge"})
        # emissions by product mass
        fill_calculated_cells(target_table_ref=self.transport_emissions_by_prod_mass,
                              func_to_apply=cal_emissions_by_mass,
                              included_rows=["N2O Emissions Factor (g N2O/kg product)"],
                              other_table_refs={"factors_by_fuel_other": self.transport_emission_factors_other_n2o,
                                                "factors_by_fuel_tanker": self.transport_emission_factors_tanker_n2o,
                                                "factors_by_fuel_barge": self.transport_emission_factors_barge_n2o,
                                                "transport_distance": self.transport_distance}) 
        
        

        

    def calculate_transport_ef(self):
        pass

    pipeline_ef: PipelineEF
    rail_ef: RailEF
    heavy_duty_truck_ef: HeavyDutyTruckEF
    tanker_barge_ef: TankerBargeEF
    # will this cause problems if I try to pass in a list?
    user_input: InitVar[Dict] = {}

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_other_co2eq: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Other_CO2eq', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_other_co2: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Other_CO2', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_other_ch4: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Other_CH4', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_other_n2o: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Other_N2O', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_barge_co2eq: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Barge_CO2eq', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_barge_co2: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Barge_CO2', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_barge_ch4: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Barge_CH4', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_barge_n2o: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Barge_N2O', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_tanker_co2eq: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Tanker_CO2eq', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_tanker_co2: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Tanker_CO2', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_tanker_ch4: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Tanker_CH4', 'transport'))

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_tanker_n2o: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emission_Factors_Tanker_N2O', 'transport'))

    # TransportEF sheet, subtable: Transport Fuel Manual Input
    # fraction of fuel type for each transport mode
    fraction_of_fuel_type_for_transport_mode: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Process_Fuel_Share', 'transport'))

    # TransportEF sheet, subtable: Transport Distance Manual Input
    # fraction of fuel type for each transport mode
    transport_distance: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Distance', 'transport'))

    # TransportEF sheet, subtable: Transport Emissions Factors by Product Mass
    # fraction of fuel type for each transport mode
    transport_emissions_by_prod_mass: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Transport_Emissions_Factors_by_Prod_Mass', 'transport'))
