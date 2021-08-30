from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.transport.heavy_duty_truck_EF import HeavyDutyTruckEF
from opem.transport.pipeline_EF import PipelineEF
from opem.transport.rail_EF import RailEF
from opem.transport.tanker_barge_EF import TankerBargeEF

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


@dataclass
class TransportEF:

    def __post_init__(self, user_input):
        # calculate_transport_ef()
        print("from transport ef")
        print(type(user_input))
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    def calculate_transport_ef(self):
        pass

    pipeline_ef: PipelineEF
    rail_ef: RailEF
    heavy_duty_truck_ef: HeavyDutyTruckEF
    tanker_barge_ef: TankerBargeEF
    # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}

    # TransportEF sheet, table: Transport Emission Factors
    # CALCULATED
    transport_emission_factors: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Transport Emission Factors'))

    # TransportEF sheet, subtable: Manual Input
    # fraction of fuel type for each transport mode
    fraction_of_fuel_type_for_transport_mode: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Transport Process Fuel Share'))
