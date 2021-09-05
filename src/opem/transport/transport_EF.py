from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
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


def calc_emission_factors(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    # print(other_table_refs[extra[row_key][0]][extra[row_key][1]].items())
    fuel_sum = 0
    for col, val in other_table_refs[extra["keymap"][row_key][0]][extra["keymap"][row_key][1]].items():
        fuel_fraction = other_table_refs[0][row_key].get((lambda col:
                                                          extra["fuel_lookup"][col] if col in extra["fuel_lookup"].keys() else col)(col))

        if fuel_fraction is not None and not isnan(fuel_fraction):
            fuel_sum += val * fuel_fraction
    return fuel_sum


def lookup_emission_factors(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    for fuel_name in other_table_refs[extra["keymap"][row_key][0]][extra["keymap"][row_key][1]].keys():

        if extra["fuel_lookup"].get(fuel_name):
            if col_key == extra["fuel_lookup"].get(fuel_name):
                col_key = fuel_name
    return other_table_refs[extra["keymap"][row_key][0]][extra["keymap"][row_key][1]].get(col_key)


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

        fill_calculated_cells(target_table_ref=self.transport_emission_factors_weighted_average,
                              func_to_apply=calc_emission_factors,
                              included_cols=["Manual Input"],
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

        fill_calculated_cells(target_table_ref=self.transport_emission_factors_weighted_average,
                              func_to_apply=lookup_emission_factors,
                              excluded_cols=["Manual Input"],
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

    pipeline_ef: PipelineEF
    rail_ef: RailEF
    heavy_duty_truck_ef: HeavyDutyTruckEF
    tanker_barge_ef: TankerBargeEF
    # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}

    # TransportEF sheet, table: Transport Emission Factors
    # collect references to nested objects for ease
    # CALCULATED
    transport_emission_factors_weighted_average: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Transport Emission Factors'))

    # TransportEF sheet, subtable: Manual Input
    # fraction of fuel type for each transport mode
    fraction_of_fuel_type_for_transport_mode: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Transport Process Fuel Share'))
