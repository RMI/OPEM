from dataclasses import dataclass
from typing import Any


@dataclass
class ProductSlate:

    product_name: str

    Crude_bbl: Any
    Gasoline_bbl: Any
    Jet_Fuel_bbl: Any
    Diesel_bbl: Any
    Fuel_Oil_bbl: Any
    Coke_bbl: Any
    Residual_fuels_bbl: Any
    Surplus_Refinery_Fuel_Gas_RFG_bbl: Any
    Liquefied_Petroleum_Gases_LPG_bbl: Any
    Petrochemical_Feedstocks_bbl: Any
    Asphalt_bbl: Any

    Gasoline_MJ: Any
    Jet_Fuel_MJ: Any
    Diesel_MJ: Any
    Fuel_Oil_MJ: Any
    Coke_MJ: Any
    Residual_fuels_MJ: Any
    Surplus_RFG_MJ: Any
    Surplus_NCR_H2_MJ: Any
    Liquefied_Petroleum_Gases_LPG_MJ: Any
    Petrochemical_Feedstocks_MJ: Any
    Asphalt_MJ: Any
    Gasoline_S_wt_MJ: Any
    Gasoline_H2_wt_MJ: Any

    Gasoline_kg: Any
    Jet_Fuel_kg: Any
    Diesel_kg: Any
    Fuel_Oil_kg: Any
    Coke_kg: Any
    Residual_fuels_kg: Any
    Sulphur_kg: Any
    Surplus_RFG_kg: Any
    Surplus_NCR_H2_kg: Any
    Liquefied_Petroleum_Gases_LPG_kg: Any
    Petrochemical_Feedstocks_kg: Any
    Asphalt_kg: Any
    Net_Upstream_Petcoke_kg: Any
