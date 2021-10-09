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


from opem.core import run_model
from opem.utils import write_csv_output
from opem import input

def main():
    
    print("Welcome to OPEM V.1.2")

    user_input = input.initialize_model_inputs(
        input.get_csv_input, input.validate_input)
 
    processed_input = [{"user_input": input } for input in user_input]

    print("Found opem_input.csv, running model.")

    results = run_model(processed_input, return_dict=False)
     
    print("Writing results . . .")
 
    write_csv_output(results)

  