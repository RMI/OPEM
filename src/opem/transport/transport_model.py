from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.transport.transport_EF import TransportEF

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


@dataclass
class TransportModel:
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


user_input: InitVar[DefaultDict] = {}

transport_results = field(
    default_factory=lambda: {})

transport_EF: TransportEF


def calculate_opem_transport(user_input_object):
    # -> TransportResults:
    # need to take in users choice of transport fuels from user_dto
    # should I initialize all transport user input in one object or
    # break into smaller objects?
    transport_ef = TransportEF(user_input_object)
    # transport distance will be passed in from the core module method
    #calculate_transport_emissions(transport_ef, transport_distance)


def calculate_transport_emissions(transport_ef: TransportEF, transport_distance: TransportDistance):
    pass

    # these will be handled by object methods

    # def calculate_transport_ef(pipeline: PipelineEF, rail: RailEF, heavy_duty_truck: HeavyDutyTruckEF, tanker_barge: TankerBargeEF) -> TransportEF:
    #     calculate_pipeline_ef()
    #     calculate_rail_ef():
    #     calculate_tanker_barge_ef():
    #     calculate_heavy_duty_truck_ef():

    # def calculate_pipeline_ef():

    # def calculate_rail_ef():

    # def calculate_tanker_barge_ef():

    # def calculate_heavy_duty_truck_ef():
