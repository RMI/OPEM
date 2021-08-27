
from dataclasses import InitVar, dataclass, field
from typing import DefaultDict

from opem.utils import initialize_from_dataclass, initialize_from_list



@dataclass
class HeavyDutyTruckEF:
    def __post_init__(self, user_input):
        print(type(user_input))
        if type(user_input) == dict:
           # this allows us to get input from a dict generated from another dataclass 
           initialize_from_dataclass(self, user_input) 
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")
        

    def calculate_heavy_duty_truck_ef():
        pass

      # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {} 

    # RailEF sheet, table: Transport Emission Factors by Process Fuel (g CO2eq. per kgkm) 
    # all fuels for pipeline transport modes
    # CALCULATED
    transport_emission_factors_by_process_fuel_g_CO2eq_per_kgkm: DefaultDict = field(default_factory=lambda: {
        "Rail - Forward Trip": {	"	Diesel	":	0.014740235	,"	Natural Gas	":	0.012005423	,"	LPG	":	0.012868112	,"	DME	":	0.013186098	,"	FTD	":	0.014384056	,"	Biodiesel	":	0.015076918	,"	Renewable Diesel	":	0.014442858	,"	Renewable Gasoline	":	0.014168452	,"	Hydrogen	":	0	},
"Rail - Backhaul": {	"	Diesel	":	0.014740235	,"	Natural Gas	":	0.012005423	,"	LPG	":	0.012868112	,"	DME	":	0.013186098	,"	FTD	":	0.014384056	,"	Biodiesel	":	0.015076918	,"	Renewable Diesel	":	0.014442858	,"	Renewable Gasoline	":	0.014168452	,"	Hydrogen	":	0	},
"Rail Emissions": {	"	Diesel	":	0.02948047	,"	Natural Gas	":	0.024010846	,"	LPG	":	0.025736224	,"	DME	":	0.026372195	,"	FTD	":	0.028768112	,"	Biodiesel	":	0.030153835	,"	Renewable Diesel	":	0.028885717	,"	Renewable Gasoline	":	0.028336904	,"	Hydrogen	":	0	}})