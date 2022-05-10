from dataclasses import InitVar, dataclass, field
from typing import Dict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


def calc_pipeline_emissions_factors(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    result = 0
    for key, row in other_table_refs[0].items():
        if key not in ['full_table_name', 'row_index_name']:
            result += row[col_key] * \
                other_table_refs[1][key]['User Selection']  # ['100 year GWP']
    result = (result * other_table_refs[2]["Oil Product Pipeline"][extra["trip_details"]]) / \
        1000000/other_table_refs[3]["kg per short ton"]["Conversion Factor"] / \
        other_table_refs[3]["km per mile"]["Conversion Factor"]
    return result


def calc_pipeline_emissions_factors_other_gases(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    return ((other_table_refs[0][extra["gas"]][col_key] * other_table_refs[1]["Oil Product Pipeline"][extra["trip_details"]]) /
            1000000/other_table_refs[2]["kg per short ton"]["Conversion Factor"] /
            other_table_refs[2]["km per mile"]["Conversion Factor"])


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

        # CO2eq
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_co2eq,
                              func_to_apply=calc_pipeline_emissions_factors,
                              extra={
                                  "trip_details": "Turbine"},
                              included_rows=["Pipeline Turbine"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_turbine,
                                                self.constants.table_1_gwp,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_co2eq,
                              func_to_apply=calc_pipeline_emissions_factors,
                              extra={
                                  "trip_details": "Reciprocating Engine"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Current"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_current,
                                                self.constants.table_1_gwp,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_co2eq,
                              func_to_apply=calc_pipeline_emissions_factors,
                              extra={
                                  "trip_details": "NG Engine: Future"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Future"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_future,
                                                self.constants.table_1_gwp,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_co2eq,
                              func_to_apply=calc_pipeline_emissions_factors_total,
                              included_rows=["Pipeline"],
                              other_table_refs=[
                                  self.share_of_pipeline_technologies_used],
                              other_tables_keymap={f"{self.share_of_pipeline_technologies_used['full_table_name']}": {
                                  "row_keymap": {}, "col_keymap": {"Pipeline Turbine": "Turbine", "Pipeline Reciprocating Engine: Current": "Reciprocating Engine", "Pipeline Reciprocating Engine: Future": "NG Engine: Future"}}},
                              )

        # CO2
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_co2,
                              func_to_apply=calc_pipeline_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Turbine",
                                  "gas": "CO2"},
                              included_rows=["Pipeline Turbine"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_turbine,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_co2,
                              func_to_apply=calc_pipeline_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Reciprocating Engine",
                                  "gas": "CO2"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Current"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_current,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_co2,
                              func_to_apply=calc_pipeline_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "NG Engine: Future",
                                  "gas": "CO2"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Future"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_future,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_co2,
                              func_to_apply=calc_pipeline_emissions_factors_total,
                              included_rows=["Pipeline"],
                              other_table_refs=[
                                  self.share_of_pipeline_technologies_used],
                              other_tables_keymap={f"{self.share_of_pipeline_technologies_used['full_table_name']}": {
                                  "row_keymap": {}, "col_keymap": {"Pipeline Turbine": "Turbine", "Pipeline Reciprocating Engine: Current": "Reciprocating Engine", "Pipeline Reciprocating Engine: Future": "NG Engine: Future"}}},
                              )
        # CH4
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_ch4,
                              func_to_apply=calc_pipeline_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Turbine",
                                  "gas": "CH4"},
                              included_rows=["Pipeline Turbine"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_turbine,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_ch4,
                              func_to_apply=calc_pipeline_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Reciprocating Engine",
                                  "gas": "CH4"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Current"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_current,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_ch4,
                              func_to_apply=calc_pipeline_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "NG Engine: Future",
                                  "gas": "CH4"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Future"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_future,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_ch4,
                              func_to_apply=calc_pipeline_emissions_factors_total,
                              included_rows=["Pipeline"],
                              other_table_refs=[
                                  self.share_of_pipeline_technologies_used],
                              other_tables_keymap={f"{self.share_of_pipeline_technologies_used['full_table_name']}": {
                                  "row_keymap": {}, "col_keymap": {"Pipeline Turbine": "Turbine", "Pipeline Reciprocating Engine: Current": "Reciprocating Engine", "Pipeline Reciprocating Engine: Future": "NG Engine: Future"}}},
                              )
        # N2O
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_n2o,
                              func_to_apply=calc_pipeline_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Turbine",
                                  "gas": "N2O"},
                              included_rows=["Pipeline Turbine"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_turbine,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_n2o,
                              func_to_apply=calc_pipeline_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "Reciprocating Engine",
                                  "gas": "N2O"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Current"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_current,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_n2o,
                              func_to_apply=calc_pipeline_emissions_factors_other_gases,
                              extra={
                                  "trip_details": "NG Engine: Future",
                                  "gas": "N2O"},
                              included_rows=[
                                  "Pipeline Reciprocating Engine: Future"],
                              other_table_refs=[self.pipeline_emission_factors_combustion_pipeline_recip_engine_future,
                                                self.energy_intensity_of_pipeline_transportation,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.pipeline_emission_factors_n2o,
                              func_to_apply=calc_pipeline_emissions_factors_total,
                              included_rows=["Pipeline"],
                              other_table_refs=[
                                  self.share_of_pipeline_technologies_used],
                              other_tables_keymap={f"{self.share_of_pipeline_technologies_used['full_table_name']}": {
                                  "row_keymap": {}, "col_keymap": {"Pipeline Turbine": "Turbine", "Pipeline Reciprocating Engine: Current": "Reciprocating Engine", "Pipeline Reciprocating Engine: Future": "NG Engine: Future"}}},
                              )

    constants: Constants
    # will this cause problems if I try to pass in a list?
    user_input: InitVar[Dict] = {}

    # PipelineEF sheet, table: Pipeline Emission Factors
    # all fuels for pipeline transport modes
    # CALCULATED
    pipeline_emission_factors_co2eq: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Pipeline_Emission_Factors_CO2eq', 'pipeline'))

    # PipelineEF sheet, table: Pipeline Emission Factors
    # all fuels for pipeline transport modes
    # CALCULATED
    pipeline_emission_factors_co2: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Pipeline_Emission_Factors_CO2', 'pipeline'))

    # PipelineEF sheet, table: Pipeline Emission Factors
    # all fuels for pipeline transport modes
    # CALCULATED
    pipeline_emission_factors_ch4: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Pipeline_Emission_Factors_CH4', 'pipeline'))

    # PipelineEF sheet, table: Pipeline Emission Factors
    # all fuels for pipeline transport modes
    # CALCULATED
    pipeline_emission_factors_n2o: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Pipeline_Emission_Factors_N2O', 'pipeline'))

    # PipelineEF sheet, table: Energy Intensity of Pipeline Transportation (Btu:ton-mile)
    # USER INPUT
    energy_intensity_of_pipeline_transportation: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Energy_Intensity_of_Pipeline_Transportation', 'pipeline'))

    # PipelineEF sheet, table: Share of Pipeline Technologies Used
    # USER INPUT
    share_of_pipeline_technologies_used: Dict = field(default_factory=lambda: build_dict_from_defaults(
        'Share_of_Pipeline_Technologies_Used', 'pipeline'))

    # PipelineEF sheet, table: Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Pipeline Turbine
    # STATIC

    pipeline_emission_factors_combustion_pipeline_turbine: Dict = field(default_factory=lambda: build_dict_from_defaults(
        'Emission_Factors_of_Fuel_Combustion_Feedstock_and_Fuel_Transportation_From_Product_Origin_to_Product_Destination_Pipeline_Turbine', 'pipeline'))

    # PipelineEF sheet, table: Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Pipeline Reciprocating Engine: Current
    # STATIC

    pipeline_emission_factors_combustion_pipeline_recip_engine_current: Dict = field(default_factory=lambda: build_dict_from_defaults(
        'Emission_Factors_of_Fuel_Combustion-_Feedstock_and_Fuel_Transportation_From_Product_Origin_to_Product_Destination_Pipeline_Reciprocating_Engine_Current', 'pipeline'))

    # PipelineEF sheet, table: Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Pipeline Reciprocating Engine: Future
    # STATIC

    pipeline_emission_factors_combustion_pipeline_recip_engine_future: Dict = field(default_factory=lambda: build_dict_from_defaults(
        'Emission_Factors_of_Fuel_Combustion-_Feedstock_and_Fuel_Transportation_From_Product_Origin_to_Product_Destination_Pipeline_Reciprocating_Engine_Future', 'pipeline'))
