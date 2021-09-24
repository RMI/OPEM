from dataclasses import asdict
from opem.combustion.combustion_EF import CombustionEF
from opem.constants import Constants
from opem.core import OPEM
from opem import input
from opem.input.user_input_dto import UserInputDto
from opem.transport.pipeline_EF import PipelineEF
from opem.transport.rail_EF import RailEF
from opem.transport.tanker_barge_EF import TankerBargeEF
from opem.transport.transport_EF import TransportEF
from opem.utils import write_csv_output
from opem.transport import HeavyDutyTruckEF


def main():
    """Entry point for the application script"""
    print("Welcome to OPEM V.1.1")

    user_input = input.initialize_model_inputs(
        input.get_csv_input, input.validate_input)

    print("Found opem_input.csv, running model.")
    print(user_input)

    user_input_dto = UserInputDto(input_list=user_input)
    print(user_input_dto.fraction_of_fuel_type_for_transport_mode)
    print("Fetching product slate . . .")

    product_slate = input.get_product_slate_csv(user_input_dto.product_name)

    # make a constants object and pass a ref to heavy_duty truck
    constants = Constants()

    print("Processing Tanker/Barge Emission Factors . . .")

    tanker_barge_ef = TankerBargeEF(
        user_input=asdict(user_input_dto), constants=constants, product_slate=product_slate)

    print("Processing Heavy-Duty Truck Emission Factors . . .")

    heavy_duty_truck_ef = HeavyDutyTruckEF(
        user_input=asdict(user_input_dto), constants=constants)

    print("Processing Rail Emission Factors . . .")

    rail_ef = RailEF(user_input=asdict(user_input_dto), constants=constants)

    print("Processing Pipeline Emission Factors . . .")

    pipeline_ef = PipelineEF(user_input=asdict(user_input_dto), constants=constants)

    transport_ef = TransportEF(user_input=asdict(user_input_dto), pipeline_ef=pipeline_ef,
                               rail_ef=rail_ef,
                               heavy_duty_truck_ef=heavy_duty_truck_ef,
                               tanker_barge_ef=tanker_barge_ef)

    print("Processing Combustion Emission Factors . . .")

    combustion_ef = CombustionEF(user_input=asdict(user_input_dto), constants=constants)

    print("Calculating results . . .")
    opem = OPEM(user_input=asdict(user_input_dto), transport_ef=transport_ef,
                combustion_ef=combustion_ef, product_slate=product_slate)

    print("Model run completed.")
    print("Writing results . . .")
    #print(user_input_dto)
    print(opem.results())

    # question: are defualt dicts necessary for the dataclass fields?
    # other question, are default dicts haveing harmful effect?
    # to initialize from defaults (cvs tables) do we need default dict (I think no)
    # to take user input, do we need default dict? (I think no)
    # does default dict mean that incorrect key in user input will add key to dict?
    # does default dict mean that incorrect key in calculation will add key to dict?

if __name__=="__main__":
	main()