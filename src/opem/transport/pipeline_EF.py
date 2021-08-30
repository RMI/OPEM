from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


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

    constants: Constants
    # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}

    # PipelineEF sheet, table: Pipeline Emission Factors
    # all fuels for pipeline transport modes
    # CALCULATED
    pipeline_emission_factors: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Pipeline Emission Factors'))

    # PipelineEF sheet, table: Energy Intensity of Pipeline Transportation (Btu:ton-mile)
    # USER INPUT
    energy_intensity_of_pipeline_transportation: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Energy Intensity of Pipeline Transportation (Btu:ton-mile)'))

    # PipelineEF sheet, table: Share of Pipeline Technologies Used
    # USER INPUT
    share_of_pipeline_technologies_used: DefaultDict = field(default_factory=lambda: build_dict_from_defaults(
        'Share of Pipeline Technologies Used'))

    # PipelineEF sheet, table: Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Pipeline Turbine
    # STATIC

    pipeline_emission_factors_combustion_pipeline_turbine: DefaultDict = field(default_factory=lambda: build_dict_from_defaults(
        'Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Pipeline Turbine'))

    # PipelineEF sheet, table: Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Pipeline Reciprocating Engine: Current
    # STATIC

    pipeline_emission_factors_combustion_pipeline_recip_engine_current: DefaultDict = field(default_factory=lambda: build_dict_from_defaults(
        'Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Pipeline Reciprocating Engine- Current'))

    # PipelineEF sheet, table: Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Pipeline Reciprocating Engine: Future
    # STATIC

    pipeline_emission_factors_combustion_pipeline_recip_engine_future: DefaultDict = field(default_factory=lambda: build_dict_from_defaults(
        'Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Pipeline Reciprocating Engine- Future'))
