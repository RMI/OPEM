from _typeshed import NoneType
from dataclasses import InitVar, dataclass, field
from typing import DefaultDict

from opem.utils import initialize_from_dataclass, initialize_from_list



@dataclass
class PipelineEF:
    def __post_init__(self, user_input):
        print(type(user_input))
        if type(user_input) == dict:
           # this allows us to get input from a dict generated from another dataclass 
           initialize_from_dataclass(self, user_input) 
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {} 

    # PipelineEF sheet, table: Transport Emission Factors by Process Fuel (g CO2eq. per kgkm) 
    # all fuels for pipeline transport modes
    # CALCULATED
    transport_emission_factors_by_process_fuel_g_CO2eq_per_kgkm: DefaultDict = field(default_factory=lambda: {"Pipeline Turbine": {
        "NG": NoneType,	"Diesel": NoneType,	"Electricity": NoneType,	"Residual Oil": NoneType,	"LPG": NoneType,	"DME": NoneType,	"FTD": NoneType,	"Biodiesel": NoneType,	"Renewable Diesel": NoneType,	"Renewable Gasoline": NoneType,	"Hydrogen": NoneType},
"Pipeline Reciprocating Engine: Current": {
        "NG": NoneType,	"Diesel": NoneType,	"Electricity": NoneType,	"Residual Oil": NoneType,	"LPG": NoneType,	"DME": NoneType,	"FTD": NoneType,	"Biodiesel": NoneType,	"Renewable Diesel": NoneType,	"Renewable Gasoline": NoneType,	"Hydrogen": NoneType},
        "Pipeline Reciprocating Engine: Future": {
        "NG": NoneType,	"Diesel": NoneType,	"Electricity": NoneType,	"Residual Oil": NoneType,	"LPG": NoneType,	"DME": NoneType,	"FTD": NoneType,	"Biodiesel": NoneType,	"Renewable Diesel": NoneType,	"Renewable Gasoline": NoneType,	"Hydrogen": NoneType},
        "Pipeline": {
        "NG": NoneType,	"Diesel": NoneType,	"Electricity": NoneType,	"Residual Oil": NoneType,	"LPG": NoneType,	"DME": NoneType,	"FTD": NoneType,	"Biodiesel": NoneType,	"Renewable Diesel": NoneType,	"Renewable Gasoline": NoneType,	"Hydrogen": NoneType}})

    # PipelineEF sheet, table: Energy Intensity of Pipeline Transportation (Btu/ton-mile)
    # USER INPUT   
    energy_intensity_of_pipeline_transportation_btu_ton_mile: DefaultDict = field(default_factory=lambda: {"Oil Product Pipeline": {
        "Reciprocating Engine":404,	"Turbine":404,	"NG Engine: Future":404}})

    # PipelineEF sheet, table: Share of Pipeline Technologies Used
    # USER INPUT   
    share_of_pipeline_technologies_used: DefaultDict = field(default_factory=lambda: {"Oil Product Pipeline": {
        "Reciprocating Engine":1.0,	"Turbine":1.0,	"NG Engine: Future":1.0}})
    
    # PipelineEF sheet, table: Emission Factors of Fuel Combustion: Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned)
    # STATIC
     
    emission_factors_of_fuel_combustion_feedstock_and_fuel_transportation: DefaultDict = field(default_factory=lambda: {"Pipeline Turbine": {
"VOC":{"NG":	0.908	,"Diesel":	1.335	,"Electricity":	0	,"Residual Oil":	1.335	,"LPG":	1.335	,"DME":	1.335	,"FTD":	1.335	,"Biodiesel":	1.335	,"Renewable Diesel":	1.335	,"Renewable Gasoline":	1.335	,"Hydrogen":	0	},
"CO":{"NG":	77.18	,"Diesel":	8.714	,"Electricity":	0	,"Residual Oil":	8.714	,"LPG":	8.714	,"DME":	8.714	,"FTD":	8.714	,"Biodiesel":	8.714	,"Renewable Diesel":	8.714	,"Renewable Gasoline":	8.714	,"Hydrogen":	0	},
"NOx":{"NG":	154.36	,"Diesel":	131.66	,"Electricity":	0	,"Residual Oil":	65.83	,"LPG":	131.66	,"DME":	65.830	,"FTD":	131.660	,"Biodiesel":	131.66	,"Renewable Diesel":	131.66	,"Renewable Gasoline":	131.66	,"Hydrogen":	98.745	},
"PM10":{"NG":	11.607	,"Diesel":	16.989	,"Electricity":	0	,"Residual Oil":	11.8923	,"LPG":	16.989	,"DME":	11.892	,"FTD":	16.989	,"Biodiesel":	16.989	,"Renewable Diesel":	16.989	,"Renewable Gasoline":	16.989	,"Hydrogen":	0	},
"PM2.5":{"NG":	11.607	,"Diesel":	13.5912	,"Electricity":	0	,"Residual Oil":	9.51384	,"LPG":	13.5912	,"DME":	9.514	,"FTD":	13.591	,"Biodiesel":	13.5912	,"Renewable Diesel":	13.5912	,"Renewable Gasoline":	13.5912	,"Hydrogen":	0	},
"SOx":{"NG":	0.268565615	,"Diesel":	8.037695601	,"Electricity":	0	,"Residual Oil":	0	,"LPG":	0	,"DME":	0.000	,"FTD":	0.000	,"Biodiesel":	0	,"Renewable Diesel":	0	,"Renewable Gasoline":	0	,"Hydrogen":	0	},
"BC":{"NG":	0.336603	,"Diesel":	1.35912	,"Electricity":	0	,"Residual Oil":	0.951384	,"LPG":	1.35912	,"DME":	0.951	,"FTD":	1.359	,"Biodiesel":	1.35912	,"Renewable Diesel":	1.35912	,"Renewable Gasoline":	1.35912	,"Hydrogen":	0	},
"OC":{"NG":	7.89276	,"Diesel":	3.3978	,"Electricity":	0	,"Residual Oil":	2.37846	,"LPG":	3.3978	,"DME":	2.378	,"FTD":	3.398	,"Biodiesel":	3.3978	,"Renewable Diesel":	3.3978	,"Renewable Gasoline":	3.3978	,"Hydrogen":	0	},
"CH4":{"NG":	23.154	,"Diesel":	0.844	,"Electricity":	0	,"Residual Oil":	0.844	,"LPG":	0.844	,"DME":	0.844	,"FTD":	0.844	,"Biodiesel":	0.844	,"Renewable Diesel":	0.844	,"Renewable Gasoline":	0.844	,"Hydrogen":	0	},
"N2O":{"NG":	2	,"Diesel":	2	,"Electricity":	0	,"Residual Oil":	2	,"LPG":	2	,"DME":	2.000	,"FTD":	2.000	,"Biodiesel":	2	,"Renewable Diesel":	2	,"Renewable Gasoline":	2	,"Hydrogen":	0	},
"CO2":{"NG":	59224.89597	,"Diesel":	78178.87763	,"Electricity":	0	,"Residual Oil":	69897.88662	,"LPG":	76281.03234	,"DME":	69,898	,"FTD":	76,281	,"Biodiesel":	79972.84308	,"Renewable Diesel":	76594.35145	,"Renewable Gasoline":	75132.21784	,"Hydrogen":	0	}},

"Pipeline Reciprocating Engine: Current": {
    "VOC":{"NG":	133.316	,"Diesel":	40.86	,"Electricity":	0	,"Residual Oil":	40.86	,"LPG":	40.86	,"DME":	40.86	,"FTD":	40.86	,"Biodiesel":	40.86	,"Renewable Diesel":	40.86	,"Renewable Gasoline":	40.86	,"Hydrogen":	0	},
"CO":{"NG":	705.993	,"Diesel":	459.6	,"Electricity":	0	,"Residual Oil":	459.6	,"LPG":	229.8	,"DME":	459.6	,"FTD":	459.6	,"Biodiesel":	459.6	,"Renewable Diesel":	459.6	,"Renewable Gasoline":	459.6	,"Hydrogen":	0	},
"NOx":{"NG":	832.952	,"Diesel":	2133.6	,"Electricity":	0	,"Residual Oil":	2133.6	,"LPG":	2133.6	,"DME":	1066.8	,"FTD":	2133.6	,"Biodiesel":	2133.6	,"Renewable Diesel":	2133.6	,"Renewable Gasoline":	2133.6	,"Hydrogen":	1600.2	},
"PM10":{"NG":	1.2	,"Diesel":	16.989	,"Electricity":	0	,"Residual Oil":	16.989	,"LPG":	1.6989	,"DME":	11.8923	,"FTD":	16.989	,"Biodiesel":	16.989	,"Renewable Diesel":	16.989	,"Renewable Gasoline":	16.989	,"Hydrogen":	0	},
"PM2.5":{"NG":	1.2	,"Diesel":	13.5912	,"Electricity":	0	,"Residual Oil":	13.5912	,"LPG":	1.35912	,"DME":	9.51384	,"FTD":	13.5912	,"Biodiesel":	13.5912	,"Renewable Diesel":	13.5912	,"Renewable Gasoline":	13.5912	,"Hydrogen":	0	},
"SOx":{"NG":	0.268565615	,"Diesel":	8.037695601	,"Electricity":	0	,"Residual Oil":	267.3268667	,"LPG":	0	,"DME":	0	,"FTD":	0	,"Biodiesel":	0	,"Renewable Diesel":	0	,"Renewable Gasoline":	0	,"Hydrogen":	0	},
"BC":{"NG":	0.24	,"Diesel":	11.0496456	,"Electricity":	0	,"Residual Oil":	11.0496456	,"LPG":	1.10496456	,"DME":	7.73475192	,"FTD":	11.0496456	,"Biodiesel":	11.0496456	,"Renewable Diesel":	11.0496456	,"Renewable Gasoline":	11.0496456	,"Hydrogen":	0	},
"OC":{"NG":	0.5136	,"Diesel":	2.4600072	,"Electricity":	0	,"Residual Oil":	2.4600072	,"LPG":	0.24600072	,"DME":	1.72200504	,"FTD":	2.4600072	,"Biodiesel":	2.4600072	,"Renewable Diesel":	2.4600072	,"Renewable Gasoline":	2.4600072	,"Hydrogen":	0	},
"CH4":{"NG":	500	,"Diesel":	4.54	,"Electricity":	0	,"Residual Oil":	4.54	,"LPG":	4.54	,"DME":	4.54	,"FTD":	4.54	,"Biodiesel":	4.54	,"Renewable Diesel":	4.54	,"Renewable Gasoline":	4.54	,"Hydrogen":	0	},
"N2O":{"NG":	50	,"Diesel":	2	,"Electricity":	0	,"Residual Oil":	2	,"LPG":	2	,"DME":	2	,"FTD":	2	,"Biodiesel":	2	,"Renewable Diesel":	2	,"Renewable Gasoline":	2	,"Hydrogen":	0	},
"CO2":{"NG":	56512.76316	,"Diesel":	77336.99224	,"Electricity":	0	,"Residual Oil":	84219.17022	,"LPG":	67560.50162	,"DME":	69056.00123	,"FTD":	75439.14694	,"Biodiesel":	79130.95769	,"Renewable Diesel":	75752.46605	,"Renewable Gasoline":	74290.33245	,"Hydrogen":	0	}},

"Pipeline Reciprocating Engine: Future": {
    "VOC":{"NG":	61.29	,"Diesel":	40.86	,"Electricity":	0	,"Residual Oil":	40.86	,"LPG":	40.86	,"DME":	40.86	,"FTD":	40.86	,"Biodiesel":	40.86	,"Renewable Diesel":	40.86	,"Renewable Gasoline":	40.86	,"Hydrogen":	0	},
"CO":{"NG":	331.42	,"Diesel":	459.6	,"Electricity":	0	,"Residual Oil":	459.6	,"LPG":	229.8	,"DME":	459.6	,"FTD":	459.6	,"Biodiesel":	459.6	,"Renewable Diesel":	459.6	,"Renewable Gasoline":	459.6	,"Hydrogen":	0	},
"NOx":{"NG":	871.68	,"Diesel":	2133.6	,"Electricity":	0	,"Residual Oil":	2133.6	,"LPG":	2133.6	,"DME":	1066.8	,"FTD":	2133.6	,"Biodiesel":	2133.6	,"Renewable Diesel":	2133.6	,"Renewable Gasoline":	2133.6	,"Hydrogen":	1600.2	},
"PM10":{"NG":	11.607	,"Diesel":	16.989	,"Electricity":	0	,"Residual Oil":	16.989	,"LPG":	1.6989	,"DME":	11.8923	,"FTD":	16.989	,"Biodiesel":	16.989	,"Renewable Diesel":	16.989	,"Renewable Gasoline":	16.989	,"Hydrogen":	0	},
"PM2.5":{"NG":	11.607	,"Diesel":	13.5912	,"Electricity":	0	,"Residual Oil":	13.5912	,"LPG":	1.35912	,"DME":	9.51384	,"FTD":	13.5912	,"Biodiesel":	13.5912	,"Renewable Diesel":	13.5912	,"Renewable Gasoline":	13.5912	,"Hydrogen":	0	},
"SOx":{"NG":	0.268565615	,"Diesel":	8.037695601	,"Electricity":	0	,"Residual Oil":	267.3268667	,"LPG":	0	,"DME":	0	,"FTD":	0	,"Biodiesel":	0	,"Renewable Diesel":	0	,"Renewable Gasoline":	0	,"Hydrogen":	0	},
"BC":{"NG":	2.3214	,"Diesel":	11.0496456	,"Electricity":	0	,"Residual Oil":	11.0496456	,"LPG":	1.10496456	,"DME":	7.73475192	,"FTD":	11.0496456	,"Biodiesel":	11.0496456	,"Renewable Diesel":	11.0496456	,"Renewable Gasoline":	11.0496456	,"Hydrogen":	0	},
"OC":{"NG":	4.967796	,"Diesel":	2.4600072	,"Electricity":	0	,"Residual Oil":	2.4600072	,"LPG":	0.24600072	,"DME":	1.72200504	,"FTD":	2.4600072	,"Biodiesel":	2.4600072	,"Renewable Diesel":	2.4600072	,"Renewable Gasoline":	2.4600072	,"Hydrogen":	0	},
"CH4":{"NG":	289.047	,"Diesel":	4.54	,"Electricity":	0	,"Residual Oil":	4.54	,"LPG":	4.54	,"DME":	4.54	,"FTD":	4.54	,"Biodiesel":	4.54	,"Renewable Diesel":	4.54	,"Renewable Gasoline":	4.54	,"Hydrogen":	0	},
"N2O":{"NG":	2	,"Diesel":	2	,"Electricity":	0	,"Residual Oil":	2	,"LPG":	2	,"DME":	2	,"FTD":	2	,"Biodiesel":	2	,"Renewable Diesel":	2	,"Renewable Gasoline":	2	,"Hydrogen":	0	},
"CO2":{"NG":	57905.97966	,"Diesel":	77336.99224	,"Electricity":	0	,"Residual Oil":	84219.17022	,"LPG":	67560.50162	,"DME":	69056.00123	,"FTD":	75439.14694	,"Biodiesel":	79130.95769	,"Renewable Diesel":	75752.46605	,"Renewable Gasoline":	74290.33245	,"Hydrogen":	0	}}})
