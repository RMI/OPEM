from dataclasses import InitVar, dataclass, field
from typing import Any, Dict

from opem.utils import build_dict_from_defaults, initialize_from_dataclass, initialize_from_list


@dataclass
class ProductSlate:
    def __post_init__(self, product_slate_input):

        if type(product_slate_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, product_slate_input)
        elif type(product_slate_input) == list:

            initialize_from_list(self, product_slate_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    product_name: str = None

    product_slate_input: InitVar[Dict] = {}

    volume_flow_bbl: Dict = field(default_factory=lambda: build_dict_from_defaults(
        "volume_flow_bbl", 'product_slate'))

    energy_flow_MJ: Dict = field(default_factory=lambda: build_dict_from_defaults(
        "energy_flow_MJ", 'product_slate'))

    mass_flow_kg: Dict = field(default_factory=lambda: build_dict_from_defaults(
        "mass_flow_kg", 'product_slate'))
