

from dataclasses import dataclass

from opem.transport.transport_EF import TransportEF


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
