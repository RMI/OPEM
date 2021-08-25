

from dataclasses import dataclass


@dataclass
class Results_Dto:
    transport:
    combustion:
    opem_total:


def run_model():
    # orchestrator function
    # will call input functions,
    # initialize EF objects
    # and calculate opem
    # main should call this function when it is ready.

    calculate_opem()


def calculate_opem_transport(transport_input_dto):
    # instantiate all transport mode EF objects (using the input dto),
    # then use them to instantiate total transport EF object
    # then us the Transport EF object, the product slate, and the input dto to
    # create the results object


def calculate_opem_combustion(transport_input_dto):
    # instantiate the combustion EF object (using the input dto),
    # then us the combustion EF object, the product slate, and the input dto to
    # create the results object


def calculate_opem() -> Results_Dto:

    calculate_opem_transport():

    caclulate_opem_combustion():
