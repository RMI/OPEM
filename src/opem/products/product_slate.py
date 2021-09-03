from dataclasses import InitVar, dataclass, field
from typing import Any, DefaultDict

from opem.utils import initialize_from_dataclass, initialize_from_list


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
    user_input: InitVar[DefaultDict] = {}
    volume_flow_bbl: DefaultDict = field(default_factory=lambda:
                                     {
                                         "full_table_name": 'Volume Flow',
                                         "Barrels of Crude per Day": Any,
                                         "Gasoline": Any,
                                         "Jet Fuel": Any,
                                         "Diesel": Any,
                                         "Fuel Oil": Any,
                                         "Coke": Any,
                                         "Residual fuels": Any,
                                         "Surplus_Refinery Fuel_Gas (RFG)": Any,
                                         "Liquefied_Petroleum Gases (LPG)": Any,
                                         "Petrochemical Feedstocks": Any,
                                         "Asphalt": Any})

    energy_flow_MJ: DefaultDict = field(default_factory=lambda:
                                     {"full_table_name": 'Energy Flow',
                                         "Gasoline": Any,
                                         "Jet Fuel": Any,
                                         "Diesel": Any,
                                         "Fuel Oil": Any,
                                         "Coke": Any,
                                         "Residual fuels": Any,
                                         "Surplus RFG": Any,
                                         "Surplus NCR H2": Any,
                                         "Liquefied Petroleum Gases (LPG)": Any,
                                         "Petrochemical Feedstocks": Any,
                                         "Asphalt": Any,
                                         "Gasoline S wt": Any,
                                         "Gasoline H2 wt": Any
                                      })

    mass_flow_kg: DefaultDict = field(default_factory=lambda:
                                   {   # keys "full_table_name" and "row_index_name" will be ignored during iteration
                                       "full_table_name": "Mass Flow",
                                       "Gasoline": Any,
                                       "Jet Fuel": Any,
                                       "Diesel": Any,
                                       "Fuel Oil": Any,
                                       "Coke": Any,
                                       "Residual fuels": Any,
                                       "Sulphur": Any,
                                       "Surplus RFG": Any,
                                       "Surplus NCR H2": Any,
                                       "Liquefied Petroleum Gases (LPG)": Any,
                                       "Petrochemical Feedstocks": Any,
                                       "Asphalt": Any,
                                       "Net Upstream Petcoke": Any,

                                   }
                                   )
