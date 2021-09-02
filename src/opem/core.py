





from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from math import isnan
from opem.combustion.combustion_EF import CombustionEF

from opem.transport.heavy_duty_truck_EF import HeavyDutyTruckEF
from opem.transport.pipeline_EF import PipelineEF
from opem.transport.rail_EF import RailEF
from opem.transport.tanker_barge_EF import TankerBargeEF
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


def calc_emission_factors(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    print(row_key)
    # print(other_table_refs[extra[row_key][0]][extra[row_key][1]].items())
    fuel_sum = 0
    for col, val in other_table_refs[extra["keymap"][row_key][0]][extra["keymap"][row_key][1]].items():
        fuel_fraction = other_table_refs[0][row_key].get((lambda col:
                                                extra["fuel_lookup"][col] if col in extra["fuel_lookup"].keys() else col)(col)) 
        print(fuel_fraction)
        print(val)
        if fuel_fraction is not None and not isnan(fuel_fraction):
            fuel_sum += val * fuel_fraction                                        
    return fuel_sum
   


@dataclass
class OPEM:

    def __post_init__(self, user_input):
        print(type(user_input))
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")
        
      
        fill_calculated_cells(target_table_ref=self.transport_emission_factors_weighted_average,
                              func_to_apply=calc_emission_factors,
                              # extra holds two dicts, map from target to other table
                              # and a lookup table to standardize fuel names
                              # maps row in target table to a tuple (index_into_other_table_ref_array, row_in_other_table)
                              extra={"fuel_lookup": {"NG": "Natural Gas"

                                                     },
                                     "keymap": {"Pipeline Emissions": (1, "Pipeline"),
                                                "Rail Emissions": (2, "Rail Emissions"),
                                                "Heavy-Duty Truck Emissions": (3, "Heavy-Duty Truck Emissions (full load)"),
                                                "Ocean Tanker Emissions": (4, "Ocean Tanker Emissions"),
                                                "Barge Emissions": (4, "Barge Emissions")}},
                              other_table_refs=[self.fraction_of_fuel_type_for_transport_mode,
                                                self.pipeline_ef.pipeline_emission_factors,
                                                self.rail_ef.rail_emission_factors,
                                                self.heavy_duty_truck_ef.heavy_duty_truck_emission_factors,
                                                self.tanker_barge_ef.tanker_barge_emission_factors])

        

    def calculate_transport_ef(self):
        pass

    transport_ef: TransportEF
    combustion_ef: CombustionEF

    # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}

    # User Inputs & Results sheet, table: OPEM Transport 
    # USER INPUT
    # CALCULATED
    transport_results: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Transport'))

    # User Inputs & Results sheet, table: OPEM Transport 
    # CALCULATED
    transport_sum: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Transport Sum'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    combustion_results: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Combustion'))

    # User Inputs & Results sheet, table: OPEM Combustion 
    # CALCULATED
    combustion_sum: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Combustion Sum'))




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
