from dataclasses import asdict
from opem.combustion.combustion_EF import CombustionEF
from opem.combustion.combustion_model import CombustionModel
from opem.constants import Constants
from opem.core import calculate_opem_transport
from opem import input
from opem.transport.pipeline_EF import PipelineEF
from opem.transport.rail_EF import RailEF
from opem.transport.tanker_barge_EF import TankerBargeEF
from opem.transport.transport_EF import TransportEF
from opem.transport.transport_model import TransportModel
from opem.utils import initialize_from_list, nested_access, visit_dict, initialize_from_dataclass
import os
from opem.transport import HeavyDutyTruckEF


def main():
    """Entry point for the application script"""
    print("Get started with OPEM model")
    # run_model()
    user_input = input.initialize_model_inputs(
        input.get_csv_input, input.validate_input)
    # make a constants object and pass a ref to heavy_duty truck
    constants = Constants()
    # tanker_barge_ef = TankerBargeEF(user_input=user_input, constants=constants)
    heavy_duty_truck_ef = HeavyDutyTruckEF(
        user_input=user_input, constants=constants)
    # rail_ef = RailEF(user_input=user_input, constants=constants)
    # pipeline_ef = PipelineEF(user_input=user_input, constants=constants)
    # transport_ef = TransportEF(user_input=user_input, pipeline_ef=pipeline_ef,
    #                            rail_ef=rail_ef,
    #                            heavy_duty_truck_ef=heavy_duty_truck_ef,
    #                            tanker_barge_ef=tanker_barge_ef)

    # transport_model = TransportModel(
    #     user_input=user_input, transport_ef=transport_ef)

    # combustion_ef = CombustionEF(user_input=user_input, constants=constants)
    # combustion_model = CombustionModel(
    #     user_input=user_input, combustion_ef=combustion_ef)

    # don't need asdict, since user_params comes straight from csv now (list of lists)
    #transport_results = calculate_opem_transport(asdict(user_params))
    #product_slate = input.get_product_slate(user_params.product_name)
