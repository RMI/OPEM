from dataclasses import InitVar, dataclass, field
from typing import Any, Dict

from opem.utils import build_dict_from_defaults, initialize_from_dataclass, initialize_from_list


@dataclass
class ProductSlate:
    def __post_init__(self, product_name, user_input):
        self.product_name = product_name

        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
           
           
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    product_name: InitVar[str]

    # We will us an initvar and custom function to fill
    # the fields from json so that we don't overwrite
    # any default values in the dictionary fields
    user_input: InitVar[Dict] = {}

    volume_flow_bbl: Dict = field(default_factory=lambda: build_dict_from_defaults("volume_flow_bbl"))

    energy_flow_MJ: Dict = field(default_factory=lambda: build_dict_from_defaults("energy_flow_MJ"))

    mass_flow_kg: Dict = field(default_factory=lambda: build_dict_from_defaults("mass_flow_kg"))