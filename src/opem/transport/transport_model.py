from dataclasses import dataclass
from opem.transport.transport_distance import TransportDistance
from opem.input.user_input import initialize_model_inputs
from opem.transport.transport_EF import HeavyDutyTruckEF, PipelineEF, RailEF, TankerBargeEF, TransportEF


# @dataclass
# class TransportResults:


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
