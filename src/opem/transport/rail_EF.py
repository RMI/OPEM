
from dataclasses import InitVar, dataclass, field
from typing import DefaultDict


from opem.utils import initialize_from_dataclass, initialize_from_list


@dataclass
class RailEF:
    def __post_init__(self, user_input):
        print(type(user_input))
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    def calculate_rail_ef():
        pass

      # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}

    # RailEF sheet, table: Rail Emission Factors
    # all fuels for pipeline transport modes
    # CALCULATED
    rail_emission_factors: DefaultDict = field(default_factory=lambda: {"Transport Emission Factors by Process Fuel(g CO2eq. per kgkm)": {
        "Rail - Forward Trip": {	"	Diesel	":	0.014740235	, "	Natural Gas	":	0.012005423	, "	LPG	":	0.012868112	, "	DME	":	0.013186098	, "	FTD	":	0.014384056	, "	Biodiesel	":	0.015076918	, "	Renewable Diesel	":	0.014442858	, "	Renewable Gasoline	":	0.014168452	, "	Hydrogen	":	0	},
        "Rail - Backhaul": {	"	Diesel	":	0.014740235	, "	Natural Gas	":	0.012005423	, "	LPG	":	0.012868112	, "	DME	":	0.013186098	, "	FTD	":	0.014384056	, "	Biodiesel	":	0.015076918	, "	Renewable Diesel	":	0.014442858	, "	Renewable Gasoline	":	0.014168452	, "	Hydrogen	":	0	},
        "Rail Emissions": {	"	Diesel	":	0.02948047	, "	Natural Gas	":	0.024010846	, "	LPG	":	0.025736224	, "	DME	":	0.026372195	, "	FTD	":	0.028768112	, "	Biodiesel	":	0.030153835	, "	Renewable Diesel	":	0.028885717	, "	Renewable Gasoline	":	0.028336904	, "	Hydrogen	":	0	}}})

    # RailEF sheet, table: Energy Intensity of Rail Transportation (Btu/ton-mile)
    # USER INPUT
    energy_intensity_of_rail_transportation_btu_ton_mile: DefaultDict = field(default_factory=lambda: {
        "Trip From Product Origin to Destination": 274,
        "Trip From Product Destination Back to Origin": 274})

    # RailEF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Origin to Product Destination (grams per mmBtu of fuel burned)
    # STATIC
    emission_factors_of_fuel_combustion_for_feedstock_and_fuel_transportation_origin_to_destination: DefaultDict = field(default_factory=lambda: {"Locomotive": {
        "	VOC	": {	"	Diesel	":	58.388	, "	Natural Gas	":	58.388	, "	LPG	":	58.388	, "	DME	":	58.388	, "	FTD	":	58.388	, "	Biodiesel	":	58.388	, "	Renewable Diesel	":	58.388	, "	Renewable Gasoline	":	58.388	, "	Hydrogen	":	0.000	},
        "	CO	": {	"	Diesel	":	206.530	, "	Natural Gas	":	103.265	, "	LPG	":	103.265	, "	DME	":	206.530	, "	FTD	":	206.530	, "	Biodiesel	":	206.530	, "	Renewable Diesel	":	206.530	, "	Renewable Gasoline	":	206.530	, "	Hydrogen	":	0.000	},
        "	NOx	": {	"	Diesel	":	1139.874	, "	Natural Gas	":	1139.874	, "	LPG	":	1139.874	, "	DME	":	569.937	, "	FTD	":	1139.874	, "	Biodiesel	":	1139.874	, "	Renewable Diesel	":	1139.874	, "	Renewable Gasoline	":	1139.874	, "	Hydrogen	":	854.905	},
        "	PM10	": {	"	Diesel	":	30.273	, "	Natural Gas	":	3.027	, "	LPG	":	3.027	, "	DME	":	21.191	, "	FTD	":	30.273	, "	Biodiesel	":	30.273	, "	Renewable Diesel	":	30.273	, "	Renewable Gasoline	":	30.273	, "	Hydrogen	":	0.000	},
        "	PM2.5	": {	"	Diesel	":	29.365	, "	Natural Gas	":	2.936	, "	LPG	":	2.936	, "	DME	":	20.555	, "	FTD	":	29.365	, "	Biodiesel	":	29.365	, "	Renewable Diesel	":	29.365	, "	Renewable Gasoline	":	29.365	, "	Hydrogen	":	0.000	},
        "	SOx	": {	"	Diesel	":	8.038	, "	Natural Gas	":	0.269	, "	LPG	":	0.000	, "	DME	":	0.000	, "	FTD	":	0.000	, "	Biodiesel	":	0.000	, "	Renewable Diesel	":	0.000	, "	Renewable Gasoline	":	0.000	, "	Hydrogen	":	0.000	},
        "	BC	": {	"	Diesel	":	2.467	, "	Natural Gas	":	0.247	, "	LPG	":	0.247	, "	DME	":	1.727	, "	FTD	":	2.467	, "	Biodiesel	":	2.467	, "	Renewable Diesel	":	2.467	, "	Renewable Gasoline	":	2.467	, "	Hydrogen	":	0.000	},
        "	OC	": {	"	Diesel	":	26.017	, "	Natural Gas	":	2.602	, "	LPG	":	2.602	, "	DME	":	18.212	, "	FTD	":	26.017	, "	Biodiesel	":	26.017	, "	Renewable Diesel	":	26.017	, "	Renewable Gasoline	":	26.017	, "	Hydrogen	":	0.000	},
        "	CH4	": {	"	Diesel	":	6.825	, "	Natural Gas	":	136.490	, "	LPG	":	6.825	, "	DME	":	6.825	, "	FTD	":	6.825	, "	Biodiesel	":	6.825	, "	Renewable Diesel	":	6.825	, "	Renewable Gasoline	":	6.825	, "	Hydrogen	":	0.000	},
        "	N2O	": {	"	Diesel	":	2.132	, "	Natural Gas	":	2.132	, "	LPG	":	2.132	, "	DME	":	2.132	, "	FTD	":	2.132	, "	Biodiesel	":	2.132	, "	Renewable Diesel	":	2.132	, "	Renewable Gasoline	":	2.132	, "	Hydrogen	":	0.000	},
        "	CO2	": {	"	Diesel	":	77673.762	, "	Natural Gas	":	58693.085	, "	LPG	":	67698.431	, "	DME	":	69392.771	, "	FTD	":	75775.917	, "	Biodiesel	":	79467.727	, "	Renewable Diesel	":	76089.236	, "	Renewable Gasoline	":	74627.102	, "	Hydrogen	":	0.000	},
    }

    })

    # RailEF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned)
    # STATIC
    emission_factors_of_fuel_combustion_for_feedstock_and_fuel_transportation_destination_to_origin: DefaultDict = field(default_factory=lambda: {"Locomotive": {
        "	VOC	": {	"	Diesel	":	58.388	, "	Natural Gas	":	58.388	, "	LPG	":	58.388	, "	DME	":	58.388	, "	FTD	":	58.388	, "	Biodiesel	":	58.388	, "	Renewable Diesel	":	58.388	, "	Renewable Gasoline	":	58.388	, "	Hydrogen	":	0.000	},
        "	CO	": {	"	Diesel	":	206.530	, "	Natural Gas	":	103.265	, "	LPG	":	103.265	, "	DME	":	206.530	, "	FTD	":	206.530	, "	Biodiesel	":	206.530	, "	Renewable Diesel	":	206.530	, "	Renewable Gasoline	":	206.530	, "	Hydrogen	":	0.000	},
        "	NOx	": {	"	Diesel	":	1139.874	, "	Natural Gas	":	1139.874	, "	LPG	":	1139.874	, "	DME	":	569.937	, "	FTD	":	1139.874	, "	Biodiesel	":	1139.874	, "	Renewable Diesel	":	1139.874	, "	Renewable Gasoline	":	1139.874	, "	Hydrogen	":	854.905	},
        "	PM10	": {	"	Diesel	":	30.273	, "	Natural Gas	":	3.027	, "	LPG	":	3.027	, "	DME	":	21.191	, "	FTD	":	30.273	, "	Biodiesel	":	30.273	, "	Renewable Diesel	":	30.273	, "	Renewable Gasoline	":	30.273	, "	Hydrogen	":	0.000	},
        "	PM2.5	": {	"	Diesel	":	29.365	, "	Natural Gas	":	2.936	, "	LPG	":	2.936	, "	DME	":	20.555	, "	FTD	":	29.365	, "	Biodiesel	":	29.365	, "	Renewable Diesel	":	29.365	, "	Renewable Gasoline	":	29.365	, "	Hydrogen	":	0.000	},
        "	SOx	": {	"	Diesel	":	8.038	, "	Natural Gas	":	0.269	, "	LPG	":	0.000	, "	DME	":	0.000	, "	FTD	":	0.000	, "	Biodiesel	":	0.000	, "	Renewable Diesel	":	0.000	, "	Renewable Gasoline	":	0.000	, "	Hydrogen	":	0.000	},
        "	BC	": {	"	Diesel	":	2.467	, "	Natural Gas	":	0.247	, "	LPG	":	0.247	, "	DME	":	1.727	, "	FTD	":	2.467	, "	Biodiesel	":	2.467	, "	Renewable Diesel	":	2.467	, "	Renewable Gasoline	":	2.467	, "	Hydrogen	":	0.000	},
        "	OC	": {	"	Diesel	":	26.017	, "	Natural Gas	":	2.602	, "	LPG	":	2.602	, "	DME	":	18.212	, "	FTD	":	26.017	, "	Biodiesel	":	26.017	, "	Renewable Diesel	":	26.017	, "	Renewable Gasoline	":	26.017	, "	Hydrogen	":	0.000	},
        "	CH4	": {	"	Diesel	":	6.825	, "	Natural Gas	":	136.490	, "	LPG	":	6.825	, "	DME	":	6.825	, "	FTD	":	6.825	, "	Biodiesel	":	6.825	, "	Renewable Diesel	":	6.825	, "	Renewable Gasoline	":	6.825	, "	Hydrogen	":	0.000	},
        "	N2O	": {	"	Diesel	":	2.132	, "	Natural Gas	":	2.132	, "	LPG	":	2.132	, "	DME	":	2.132	, "	FTD	":	2.132	, "	Biodiesel	":	2.132	, "	Renewable Diesel	":	2.132	, "	Renewable Gasoline	":	2.132	, "	Hydrogen	":	0.000	},
        "	CO2	": {	"	Diesel	":	77673.762	, "	Natural Gas	":	58693.085	, "	LPG	":	67698.431	, "	DME	":	69392.771	, "	FTD	":	75775.917	, "	Biodiesel	":	79467.727	, "	Renewable Diesel	":	76089.236	, "	Renewable Gasoline	":	74627.102	, "	Hydrogen	":	0.000	},
    }
    })
