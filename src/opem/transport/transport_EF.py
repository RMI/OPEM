from dataclasses import dataclass


@dataclass
class PipelineEF:
    def __post_init__():
        calculate_pipeline_ef()

    def calculate_pipeline_ef()


@dataclass
class RailEF:
    def __post_init__():
        calculate_rail_ef()

    def calculate_rail_ef()


@dataclass
class TankerBargeEF:
    def __post_init__():
        calculate_tanker_barge_ef()

    def calculate_tanker_barge__ef()


@dataclass
class HeavyDutyTruckEF:
    def __post_init__():
        calculate_heavy_duty_truck_ef()

    def calculate_heavy_duty_truck_ef()


@dataclass
class TransportEF:

    def __post_init__():
        calculate_transport_ef()

    def calculate_transport_ef()

    pipeline: PipelineEF
    rail: RailEF
    tanker_barge: TankerBargeEF
    heavy_duty_truck: HeavyDutyTruckEF
