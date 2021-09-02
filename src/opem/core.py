





from dataclasses import InitVar, dataclass, field
from typing import DefaultDict, Type
from math import isnan
from opem.combustion.combustion_EF import CombustionEF
from opem.products.product_slate import ProductSlate

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


def lookup_emission_factors(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    return other_table_refs[0][row_key][target_table_ref[row_key]["Choose Transport Fuel (from drop-down)"]]

def calc_emissions(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    try:
       return target_table_ref[row_key]["Emission Factor (g CO2eq. / kgkm)"] * \
        target_table_ref[row_key]["Select Distance Traveled (km)"] * \
            other_table_refs[0]["mass_flow_sum"]["total"] / 100000000
    except TypeError:
        pass
    

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
        

        # fill_calculated_cells(target_table_ref=self.transport_results,
        #                       func_to_apply=calc_product_slate_combustion_sum,
        #                       included_cols=["Transport Emissions (kg CO2eq. / bbl of crude)"],
        #                       other_table_refs=[self.transport_ef.tanker_barge_ef.share_of_petroleum_products])


        fill_calculated_cells(target_table_ref=self.transport_results,
                              func_to_apply=lookup_emission_factors,
                              included_cols=["Emission Factor (g CO2eq. / kgkm)"],
                              extra={"fuel_lookup": {"NG": "Natural Gas"

                                                     },
                                     "keymap": {"Pipeline Emissions": (1, "Pipeline"),
                                                "Rail Emissions": (2, "Rail Emissions"),
                                                "Heavy-Duty Truck Emissions": (3, "Heavy-Duty Truck Emissions (full load)"),
                                                "Ocean Tanker Emissions": (4, "Ocean Tanker Emissions"),
                                                "Barge Emissions": (4, "Barge Emissions")}},
                              other_table_refs=[self.transport_ef.transport_emission_factors_weighted_average])
        
        fill_calculated_cells(target_table_ref=self.transport_results,
                              func_to_apply=calc_emissions,
                              included_cols=["Transport Emissions (kg CO2eq. / bbl of crude)"],
                              other_table_refs=[self.transport_ef.tanker_barge_ef.share_of_petroleum_products])

        
        print(self.transport_results)
        

    transport_ef: TransportEF
    #combustion_ef: CombustionEF
    #product_slate: ProductSlate

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
