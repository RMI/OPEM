from dataclasses import InitVar, asdict, dataclass, field
from typing import Any, DefaultDict, List
from opem.utils import initialize_from_list, nested_access

# hold validated user input


@dataclass
class UserInputDto:
    # should have % combusted
    # should validate % combusted
    # # should have user transport fuel selections
    # should validate fuel selections

    # we can validate in the post init method

    # transport fuel-type options

    # transportation user inputs

    # Pipeline_Emissions_Transport_Fuel: Any
    # Pipeline_Emissions_Distance_Traveled_km: Any
    # Rail_Emissions_Transport_Fuel: Any
    # Rail_Emissions_Distance_Traveled_km: Any
    # Heavy_Duty_Truck_Emissions_Transport_Fuel: Any
    # Heavy_Duty_Truck_Emissions_Distance_Traveled_km: Any
    # Ocean_Tanker_Emissions_Transport_Fuel: Any
    # Ocean_Tanker_Emissions_Distance_Traveled_km: Any
    # Barge_Emissions_Transport_Fuel: Any
    # Barge_Emissions_Distance_Traveled_km: Any
    def __post_init__(self, input_list):
        # this allows us to get input from csv
        initialize_from_list(self, input_list)
        # print('default values')
        # print(self.product_name)
        # print(self.transport_mode)
        # print(self.transport_fuel_share)
        # for row in input_list:
        #     if len(row) == 2:
        #         setattr(self, row[0], row[1])
        #     else:
        #         print('keys from input row')
        #         print(row[1:-2])
        #         # get a reference to the object the holds the key/value pair we want to mutate
        #         ref = self.nested_access(
        #             dict=getattr(self, row[0]), keys=row[1:-2])
        #         ref[row[-2]] = row[-1]

        # print('new values')
        # print(self.product_name)
        # print(self.transport_mode)
        # print(self.transport_fuel_share)

    # def nested_access(self, dict, keys):
    #     for key in keys:
    #         dict = dict[key]
    #     return dict

    input_list: InitVar[List] = []
    product_name: str = 'Default Product'
    transport_mode: DefaultDict = field(default_factory=lambda: {"Pipeline_Emissions": {
                                        "Transport_Fuel": "Natural Gas", "Distance_Traveled_km": 2414}})
    transport_fuel_share: DefaultDict = field(default_factory=lambda: {"Pipeline": {
        "Natural Gas": 0.11}})
    transport_fuel_options: List[str] = field(default_factory=lambda: ["Natural Gas", "LNG Diesel", "Bunker Fuel Residual Oil",
                                                                       "LPG DME FTD Biodiesel", "Renewable Diesel", "Renewable Gasoline", "Hydrogen", "Ethanol", "Methanol"])
