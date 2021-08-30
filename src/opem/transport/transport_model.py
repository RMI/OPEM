from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.transport.transport_EF import TransportEF

from opem.utils import initialize_from_dataclass, initialize_from_list

# Define functions for filling calculated cells in the tables here


@dataclass(init=True)
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

    transport_ef: TransportEF
    user_input: InitVar[DefaultDict] = {}

    transport_results: DefaultDict = field(
        default_factory=lambda: {})
