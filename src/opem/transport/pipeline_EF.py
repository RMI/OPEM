from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


def calc_pipeline_emissions_factors(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    result = 0
    for key, row in other_table_refs[0].items():
        if key not in ['full_table_name', 'row_index_name']:
            result += row[col_key] * \
                other_table_refs[1][key]['GWP']
    result = (result * other_table_refs[2]["Oil Product Pipeline"][extra["trip_details"]]) / \
        1000000/other_table_refs[3]["kg per short ton"]["Conversion Factor"] / \
        other_table_refs[3]["km per mile"]["Conversion Factor"]
    return result


def calc_pipeline_emissions_factors_total(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    
    return sum(row[col_key] *
               other_table_refs[0]['Oil Product Pipeline'][other_tables_keymap[other_table_refs[0]
                                                                            ["full_table_name"]]["col_keymap"][key]]
               for key, row in target_table_ref.items()
               if key not in ['full_table_name', 'row_index_name', 'Pipeline'])


@dataclass
class PipelineEF:
    def __post_init__(self, user_input):
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors,
                              func_to_apply=calc_pipeline_emissions_factors,
                              extra={
                                  "trip_details": "Turbine"},
                              included_rows=["Pipeline Turbine"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_turbine,
                                                self.constants.table_1_100year_gwp,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors,
                              func_to_apply=calc_pipeline_emissions_factors,
                              extra={
                                  "trip_details": "Reciprocating Engine"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Current"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_current,
                                                self.constants.table_1_100year_gwp,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors,
                              func_to_apply=calc_pipeline_emissions_factors,
                              extra={
                                  "trip_details": "NG Engine: Future"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Future"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_future,
                                                self.constants.table_1_100year_gwp,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors,
                              func_to_apply=calc_pipeline_emissions_factors_total,
                              extra={
                                  "trip_details": "NG Engine: Future"},
                              included_rows=["Pipeline"],
                              other_table_refs=[
                                  self.share_of_pipeline_technologies_used],
                              other_tables_keymap={f"{self.share_of_pipeline_technologies_used['full_table_name']}": {
                                  "row_keymap": {}, "col_keymap": {"Pipeline Turbine": "Turbine", "Pipeline Reciprocating Engine: Current": "Reciprocating Engine", "Pipeline Reciprocating Engine: Future": "NG Engine: Future"}}},
                              )
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
