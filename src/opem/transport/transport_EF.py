from dataclasses import InitVar, asdict, dataclass, field
from typing import DefaultDict
import collections

from opem.utils import initialize_from_dataclass, visit_dict, nested_access




# @dataclass
# class PipelineEF:
#     def __post_init__():
#         calculate_pipeline_ef()

#     def calculate_pipeline_ef()


# @dataclass
# class RailEF:
#     def __post_init__():
#         calculate_rail_ef()

#     def calculate_rail_ef()


# @dataclass
# class TankerBargeEF:
#     def __post_init__():
#         calculate_tanker_barge_ef()

#     def calculate_tanker_barge__ef()


# @dataclass
# class HeavyDutyTruckEF:
#     def __post_init__():
#         calculate_heavy_duty_truck_ef()

#     def calculate_heavy_duty_truck_ef()


@dataclass
class TransportEF:

    def __post_init__(self, user_input):
        # calculate_transport_ef()
        print("from transport ef")

        # this allows us to get input from a dict generated from another dataclass
        initialize_from_dataclass(self, user_input)

    def calculate_transport_ef(self):
        pass

    # put this in utils
    # def nested_access(self, dict, keys):
    #     for key in keys:
    #         dict = dict[key]
    #     return dict

    user_input: InitVar[DefaultDict] = {}
    transport_fuel_share: DefaultDict = field(default_factory=lambda: {"Pipeline": {
        "Natural Gas": 0.11, "LNG": 0}})
    # pipeline: PipelineEF
    # rail: RailEF
    # tanker_barge: TankerBargeEF
    # heavy_duty_truck: HeavyDutyTruckEF
