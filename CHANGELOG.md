# Changelog

## 1.3.4

This release fixes two calculation bugs. **Results from earlier versions can change after you upgrade**, so rerun any results you plan to publish or compare.

### NGL combustion CO2, CH4 and N2O now scale with NGL volume when NGL Volume source = 1 ([#13](https://github.com/RMI/OPEM/issues/13))

When NGL Volume source was set to 1 (a single total field NGL volume, no C2–C5+ breakdown), OPEM reported the per-gallon NGL emission factor as the daily NGL combustion CO2, CH4 and N2O, without multiplying by volume. Those outputs were several orders of magnitude too low, and they didn't change when NGL volume changed.

- **Who is affected:** runs with NGL Volume source = 1. Runs with NGL Volume source = 2 are unchanged.
- **Outputs that increase:** `UpstreamNGLProd_CO2_CombustionEmissions_kgCO2/BOE`, `UpstreamNGLProd_CH4_CombustionEmissions_kgCH4/BOE` and `UpstreamNGLProd_N2O_CombustionEmissions_kgN2O/BOE`. So do the totals that include them: `Total_CO2_CombustionEmissions_kgCO2/BOE`, `Total_CH4_CombustionEmissions_kgCH4/BOE`, `Total_CO2_Emissions_kgCO2/BOE` and `Total_CH4_Emissions_kgCH4/BOE`. The N2O totals also change (see the fix below).
- **Not affected:** NGL CO2e (`UpstreamNGLProd_CombustionEmissions_kgCO2e/BOE`) and `Total_Emissions_kgCO2e/BOE`. These were already correct.
- **Size of the change:** this depends on how much of a field's production is NGL. In a test case with 10,000 BOED oil and 50,000 MCFD gas, NGL combustion CO2 went from 0.0003 to 13.1 kg CO2/BOE at 1,000 BOED NGL (total CO2 combustion +1.3%), and from 0.0003 to 54.3 kg CO2/BOE at 5,000 BOED NGL (+6.2%).

### Total N2O emissions now include coke, natural gas and NGL ([#14](https://github.com/RMI/OPEM/issues/14))

Total N2O combustion emissions included only refinery products. They left out upgrader coke, natural gas and NGL, unlike the CO2e, CO2 and CH4 totals.

- **Who is affected:** all runs.
- **Outputs that increase:** `Total_N2O_CombustionEmissions_kgN2O/BOE` and `Total_N2O_Emissions_kgN2O/BOE`, in both the CSV and dictionary outputs. They now equal the sum of the refinery product, upgrader coke, natural gas and NGL N2O outputs.
- **Size of the change:** in the same test case, total N2O combustion rose by about 2.7%. The increase is larger for fields with more gas, NGL or upgrader coke.

### Other changes

- The CLI welcome message, the README install example and the Sphinx docs now show the current version.
