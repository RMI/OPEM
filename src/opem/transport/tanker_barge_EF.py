
from dataclasses import InitVar, dataclass, field
from typing import DefaultDict

from opem.utils import initialize_from_dataclass, initialize_from_list


@dataclass
class TankerBargeEF:
    def __post_init__(self, user_input):
        print(type(user_input))
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    def calculate_tanker_barge_ef():
        pass

      # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}

    # Tanker & Barge EF sheet, table: Tanker and Barge Emission Factors
    # CALCULATED
    tanker_and_barge_emission_factors: DefaultDict = field(default_factory=lambda: {"Transport Emission Factors by Process Fuel(g CO2eq. per kgkm)": {
        "Ocean Tanker Forward Journey": {	"	Bunker Fuel	":	None	, "	Residual Oil	":	None	, "	Diesel	":	None	, "	Natural Gas	":	None	, "	LPG	":	None	, "	DME	":	None	, "	FTD	":	None	, "	Biodiesel	":	None	, "	Renewable Diesel	":	None	, "	Renewable Gasoline	":	None	, "	Hydrogen	":	0	},
        "Ocean Tanker Backhaul": {	"	Bunker Fuel	":	None	, "	Residual Oil	":	None	, "	Diesel	":	None	, "	Natural Gas	":	None	, "	LPG	":	None	, "	DME	":	None	, "	FTD	":	None	, "	Biodiesel	":	None	, "	Renewable Diesel	":	None	, "	Renewable Gasoline	":	None	, "	Hydrogen	":	0	},
        "Ocean Tanker Emissions": {	"	Bunker Fuel	":	None	, "	Residual Oil	":	None	, "	Diesel	":	None	, "	Natural Gas	":	None	, "	LPG	":	None	, "	DME	":	None	, "	FTD	":	None	, "	Biodiesel	":	None	, "	Renewable Diesel	":	None	, "	Renewable Gasoline	":	None	, "	Hydrogen	":	0	},
        "Barge Forward Journey": {	"	Bunker Fuel	":	None	, "	Residual Oil	":	None	, "	Diesel	":	None	, "	Natural Gas	":	None	, "	LPG	":	None	, "	DME	":	None	, "	FTD	":	None	, "	Biodiesel	":	None	, "	Renewable Diesel	":	None	, "	Renewable Gasoline	":	None	, "	Hydrogen	":	1	},
        "Barge Backhaul": {	"	Bunker Fuel	":	None	, "	Residual Oil	":	None	, "	Diesel	":	None	, "	Natural Gas	":	None	, "	LPG	":	None	, "	DME	":	None	, "	FTD	":	None	, "	Biodiesel	":	None	, "	Renewable Diesel	":	None	, "	Renewable Gasoline	":	None	, "	Hydrogen	":	2	},
        "Barge Emissions": {	"	Bunker Fuel	":	None	, "	Residual Oil	":	None	, "	Diesel	":	None	, "	Natural Gas	":	None	, "	LPG	":	None	, "	DME	":	None	, "	FTD	":	None	, "	Biodiesel	":	None	, "	Renewable Diesel	":	None	, "	Renewable Gasoline	":	None	, "	Hydrogen	":	3	}}})

    # Tanker & Barge EF sheet, table: Cargo Payload by Transportation Mode and by Product Fuel Type (short tons)
    # USER INPUT
    cargo_payload_by_transportation_mode_and_by_product_fuel_type_short_tons: DefaultDict = field(default_factory=lambda: {
        "Ocean Tanker": {"Gasoline": 90000.00,	"Diesel": 100000.00,	"Jet Fuel": 100000.00,	"Residual Oil": 100000.00,	"Petcoke": 100000.00},
        "Barge": {"Gasoline": 20000.00,	"Diesel": 22500.00,	"Jet Fuel": 22500.00,	"Residual Oil": 22500.00,	"Petcoke": 22500.00}})
