
from dataclasses import InitVar, asdict, dataclass, field
from typing import DefaultDict
import collections

from opem.utils import initialize_from_dataclass, visit_dict, nested_access, initialize_from_list


# @dataclass
# class TankerBargeEF:
#     def __post_init__():
#         calculate_tanker_barge_ef()

#     def calculate_tanker_barge__ef()


# @dataclass
# class HeavyDutyTruckEF:
#     def __post_init__():
#         calculate_heavy_duty_truck_ef()

#     def calculate_heavy_duty_truck_ef()


@dataclass
class TransportEF:

    def __post_init__(self, user_input):
        # calculate_transport_ef()
        print("from transport ef")
        print(type(user_input))
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    def calculate_transport_ef(self):
        pass

    # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}
    # TransportEF sheet, table: Transport Emission Factors by Process Fuel (g CO2eq. per kgkm)
    # only manual input column
    # CALCULATED
    transport_emission_factors_by_process_fuel_g_CO2eq_per_kgkm: DefaultDict = field(default_factory=lambda: {"Pipeline Emissions": {
        "Manual Input": None},
        "Rail Emissions": {
        "Manual Input": None},
        "Heavy-Duty Truck Emissions": {
        "Manual Input": None},
        "Ocean Tanker Emissions": {
        "Manual Input": None},
        "Barge Emissions": {
        "Manual Input": None}})

    # TransportEF sheet, subtable: Manual Input
    # fraction of fuel type for each transport mode
    fraction_of_fuel_type_for_transport_mode: DefaultDict = field(default_factory=lambda: {"Pipeline": {
        "Natural Gas": None, "LNG": None,	"Diesel": None,
        "Bunker Fuel": None,	"Residual Oil":	None, "LPG": None,
        "DME": None,	"FTD": None,	"Biodiesel": None,
        "Renewable Diesel": None,	"Renewable Gasoline": None,
        "Hydrogen": None,	"Ethanol":	None, "Methanol": None},

        "Rail Emissions": {
        "Natural Gas": None, "LNG": None,	"Diesel": None,
        "Bunker Fuel": None,	"Residual Oil":	None, "LPG": None,
        "DME": None,	"FTD": None,	"Biodiesel": None,
        "Renewable Diesel": None,	"Renewable Gasoline": None,
        "Hydrogen": None,	"Ethanol":	None, "Methanol": None},

        "Heavy-Duty Truck Emissions": {
        "Natural Gas": None, "LNG": None,	"Diesel": None,
        "Bunker Fuel": None,	"Residual Oil":	None, "LPG": None,
        "DME": None,	"FTD": None,	"Biodiesel": None,
        "Renewable Diesel": None,	"Renewable Gasoline": None,
        "Hydrogen": None,	"Ethanol":	None, "Methanol": None},

        "Ocean Tanker Emissions": {
        "Natural Gas": None, "LNG": None,	"Diesel": None,
        "Bunker Fuel": None,	"Residual Oil":	None, "LPG": None,
        "DME": None,	"FTD": None,	"Biodiesel": None,
        "Renewable Diesel": None,	"Renewable Gasoline": None,
        "Hydrogen": None,	"Ethanol":	None, "Methanol": None},

        "Barge Emissions": {
        "Natural Gas": None, "LNG": None,	"Diesel": None,
        "Bunker Fuel": None,	"Residual Oil":	None, "LPG": None,
        "DME": None,	"FTD": None,	"Biodiesel": None,
        "Renewable Diesel": None,	"Renewable Gasoline": None,
        "Hydrogen": None,	"Ethanol":	None, "Methanol": None},

    })
