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
        # for key in user_input.keys():
        #     if key in asdict(self).keys():
        #         for path in visit_dict(user_input[key]):
        #             # print(user_input[key])

        #             if len(path[0]) == 1:
        #                 print('path length = 1')
        #                 print(user_input[key])
        #                 setattr(self, key, user_input[key][path[0]])
        #             else:

        #                 keys_length = len(path[0]) - 1
        #             # get a reference to the object the holds the key/value pair we want to mutate
        #                 ref = self.nested_access(
        #                     dict=getattr(self, key), keys=path[0][0:keys_length])

        #                 ref[path[0][-1]] = path[-1]
        # print('results')
        # print(self.transport_fuel_share)

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
