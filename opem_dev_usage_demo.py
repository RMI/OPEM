from opem import run_model


def demo():

    # Parameter object with input as list of lists
    list_input = {"user_input": [["User Inputs & Results",
                                  "Global:",
                                  "Assay (Select Oil)",
                                  "-",
                                  "Field Name A"],
                                 ["User Inputs & Results",
                                 "Global:",
                                  "Gas Production Volume (MCFD)",
                                  "-",
                                  901603],
                                 ["User Inputs & Results",
                                 "Global:",
                                  "Oil Production Volume (BOED)",
                                  "-",
                                  363519],
                                 ["User Inputs & Results",
                                 "Global:",
                                  "% Field NGL C2 Volume allocated to Ethylene converstion",
                                  "-",
                                  9],
                                 ["User Inputs & Results",
                                 "Global:",
                                  "GWP selection (yr period, 136 or 69)",
                                  "-",
                                  699]]
                  }
    results = run_model(list_input, return_dict=False)
    print("List inputs\n", results)

    # Parameter object with input as dictionary
    dict_input = {"user_input": {("User Inputs & Results",
                                  "Global:",
                                  "Assay (Select Oil)",
                                  "-"):
                                 "Field Name B",
                                 ("User Inputs & Results",
                                  "Global:",
                                  "Gas Production Volume (MCFD)",
                                  "-"): 263043,
                                 ("User Inputs & Results",
                                  "Global:",
                                  "Oil Production Volume (BOED)",
                                  "-"): 328278,
                                 ("User Inputs & Results",
                                 "Global:",
                                  "% Field NGL C2 Volume allocated to Ethylene converstion",
                                  "-"):
                                 5,
                                 ("User Inputs & Results",
                                 "Global:",
                                  "GWP selection (yr period, 319 or 73)",
                                  "-"):
                                 226}
                  }
    results = run_model(dict_input, return_dict=True)
    print("Dictionary inputs\n", results)

    # Input is a list of parameter objects (for multiple runs)
    #results = run_model([list_input, dict_input], return_dict=True)
    #print("List of input parameter objects for multiple runs\n", results)

    # OPGEE parameters held separately under the "opgee_input" key in the parameter object.
    # They can also be mixed in with the other parameter undert the "user_input" key.
    separate_opgee_input = {"user_input": {("User Inputs & Results",
                                            "Global:",
                                            "Assay (Select Oil)",
                                            "-"): "Field Name B",
                                           ("User Inputs & Results",
                                            "Global:",
                                            "% Field NGL C2 Volume allocated to Ethylene converstion",
                                            "-"):
                                           7,
                                           ("User Inputs & Results",
                                            "Global:",
                                            "GWP selection (yr period, 273 or 83)",
                                            "-"):
                                           142},
                            "opgee_input": {("User Inputs & Results",
                                             "Global:",
                                             "Gas Production Volume (MCFD)",
                                             "-"): 533811,
                                            ("User Inputs & Results",
                                            "Global:",
                                             "Oil Production Volume (BOED)",
                                             "-"): 272261}
                            }
    results = run_model(separate_opgee_input, return_dict=True)
    print("OPGEE input parameters separated from others\n", results)

    # Full product slate data passed in under the "product_slate" key.
    # Use this option to run the model with an oil that is not in the
    # interal "all_product_slates.csv"

    # Product slate data can be structured as a list of lists or as a dictionary
    product_slate_list = [['product_name', '', 'Field Name C'],
                          ['volume_flow_bbl', 'Barrels of Crude per Day',
                           'Flow', 77432.88475],
                          ['volume_flow_bbl', 'Gasoline', 'Flow', 70526.28054],
                          ['volume_flow_bbl', 'Jet Fuel', 'Flow', 70015.55011],
                          ['volume_flow_bbl', 'Diesel', 'Flow', 27567.38261],
                          ['volume_flow_bbl', 'Fuel Oil', 'Flow', 6.2e-86],
                          ['volume_flow_bbl', 'Coke', 'Flow', 8639.785499],
                          ['volume_flow_bbl', 'Residual fuels', 'Flow', 1616.495843],
                          ['volume_flow_bbl',
                           'Surplus Refinery Fuel Gas (RFG)', 'Flow', 2.9],
                          ['volume_flow_bbl',
                           'Liquefied Petroleum Gases (LPG)', 'Flow', 7448.771656],
                          ['volume_flow_bbl', 'Petrochemical Feedstocks', 'Flow', 9.6],
                          ['volume_flow_bbl', 'Asphalt', 'Flow', 7.7],
                          ['energy_flow_MJ', 'Gasoline', 'Flow', 173361554.5],
                          ['energy_flow_MJ', 'Jet Fuel', 'Flow', 73055522.32],
                          ['energy_flow_MJ', 'Diesel', 'Flow', 359944924.7],
                          ['energy_flow_MJ', 'Fuel Oil', 'Flow', 7.758999986],
                          ['energy_flow_MJ', 'Coke', 'Flow', 48930716.16],
                          ['energy_flow_MJ', 'Residual fuels', 'Flow', 55017120.87],
                          ['energy_flow_MJ', 'Surplus RFG', 'Flow', 3.3],
                          ['energy_flow_MJ', 'Surplus NCR H2', 'Flow', 2.5],
                          ['energy_flow_MJ',
                           'Liquefied Petroleum Gases (LPG)', 'Flow', 36347355.64],
                          ['energy_flow_MJ', 'Petrochemical Feedstocks',
                           'Flow', 96900175.65],
                          ['energy_flow_MJ', 'Asphalt', 'Flow', 5.9],
                          ['energy_flow_MJ', 'Gasoline S wt%', 'Flow', 4.53e-32],
                          ['energy_flow_MJ', 'Gasoline H2 wt%', 'Flow', 89.5721086],
                          ['mass_flow_kg', 'Gasoline', 'Flow', 3546348.474],
                          ['mass_flow_kg', 'Jet Fuel', 'Flow', 7865564.87],
                          ['mass_flow_kg', 'Diesel', 'Flow', 1182137.434],
                          ['mass_flow_kg', 'Fuel Oil', 'Flow', 8.19e-11],
                          ['mass_flow_kg', 'Coke', 'Flow', 3163493.159],
                          ['mass_flow_kg', 'Residual fuels', 'Flow', 907799.339],
                          ['mass_flow_kg', 'Sulphur', 'Flow', 70584.39795],
                          ['mass_flow_kg', 'Surplus RFG', 'Flow', 6.6],
                          ['mass_flow_kg', 'Surplus NCR H2', 'Flow', 8.2],
                          ['mass_flow_kg',
                           'Liquefied Petroleum Gases (LPG)', 'Flow', 375297.8521],
                          ['mass_flow_kg', 'Petrochemical Feedstocks', 'Flow', 8.6],
                          ['mass_flow_kg', 'Asphalt', 'Flow', 7.4],
                          ['mass_flow_kg', 'Net Upstream Petcoke', 'Flow', 8.8]]

    product_slate_dict = {('product_name', ''): 'Field Name C',
                          ('volume_flow_bbl', 'Barrels of Crude per Day',
                           'Flow'): 75825.58379,
                          ('volume_flow_bbl', 'Gasoline', 'Flow'): 54595.27520,
                          ('volume_flow_bbl', 'Jet Fuel', 'Flow'): 89114.15330,
                          ('volume_flow_bbl', 'Diesel', 'Flow'): 94859.47941,
                          ('volume_flow_bbl', 'Fuel Oil', 'Flow'): 2.2e-62,
                          ('volume_flow_bbl', 'Coke', 'Flow'): 5102.410204,
                          ('volume_flow_bbl', 'Residual fuels', 'Flow'): 8688.552841,
                          ('volume_flow_bbl',
                           'Surplus Refinery Fuel Gas (RFG)', 'Flow'): 5.4,
                          ('volume_flow_bbl',
                           'Liquefied Petroleum Gases (LPG)', 'Flow'): 7103.971890,
                          ('volume_flow_bbl', 'Petrochemical Feedstocks', 'Flow'): 5.5,
                          ('volume_flow_bbl', 'Asphalt', 'Flow'): 6.2,
                          ('energy_flow_MJ', 'Gasoline', 'Flow'): 467220480.8,
                          ('energy_flow_MJ', 'Jet Fuel', 'Flow'): 95278059.95,
                          ('energy_flow_MJ', 'Diesel', 'Flow'): 924310711.3,
                          ('energy_flow_MJ', 'Fuel Oil', 'Flow'): 9.203053597,
                          ('energy_flow_MJ', 'Coke', 'Flow'): 90587564.26,
                          ('energy_flow_MJ', 'Residual fuels', 'Flow'): 21304877.63,
                          ('energy_flow_MJ', 'Surplus RFG', 'Flow'): 3.1,
                          ('energy_flow_MJ', 'Surplus NCR H2', 'Flow'): 8.1,
                          ('energy_flow_MJ',
                           'Liquefied Petroleum Gases (LPG)', 'Flow'): 79440528.57,
                          ('energy_flow_MJ', 'Petrochemical Feedstocks',
                           'Flow'): 80303261.24,
                          ('energy_flow_MJ', 'Asphalt', 'Flow'): 4.5,
                          ('energy_flow_MJ', 'Gasoline S wt%', 'Flow'): 1.53e-26,
                          ('energy_flow_MJ', 'Gasoline H2 wt%', 'Flow'): 26.4827851,
                          ('mass_flow_kg', 'Gasoline', 'Flow'): 5673582.129,
                          ('mass_flow_kg', 'Jet Fuel', 'Flow'): 6235073.29,
                          ('mass_flow_kg', 'Diesel', 'Flow'): 5797167.163,
                          ('mass_flow_kg', 'Fuel Oil', 'Flow'): 1.19e-62,
                          ('mass_flow_kg', 'Coke', 'Flow'): 8858370.404,
                          ('mass_flow_kg', 'Residual fuels', 'Flow'): 111784.331,
                          ('mass_flow_kg', 'Sulphur', 'Flow'): 38246.65115,
                          ('mass_flow_kg', 'Surplus RFG', 'Flow'): 9.9,
                          ('mass_flow_kg', 'Surplus NCR H2', 'Flow'): 4.7,
                          ('mass_flow_kg',
                           'Liquefied Petroleum Gases (LPG)', 'Flow'): 141965.8860,
                          ('mass_flow_kg', 'Petrochemical Feedstocks', 'Flow'): 7.5,
                          ('mass_flow_kg', 'Asphalt', 'Flow'): 7.7,
                          ('mass_flow_kg', 'Net Upstream Petcoke', 'Flow'): 9.2}

    # If an oil name is included under "user_input", it will be ignored and
    # and the product slate data under the "product_slate" key will be used.

    input_with_full_product_slate = {"user_input": {("User Inputs & Results",
                                                     "Global:",
                                                     "% Field NGL C2 Volume allocated to Ethylene converstion",
                                                     "-"):
                                                    9,
                                                    ("User Inputs & Results",
                                                     "Global:",
                                                     "GWP selection (yr period, 479 or 16)",
                                                     "-"):
                                                    404},
                                     "opgee_input": {("User Inputs & Results",
                                                      "Global:",
                                                      "Gas Production Volume (MCFD)",
                                                      "-"): 471183,
                                                     ("User Inputs & Results",
                                                      "Global:",
                                                      "Oil Production Volume (BOED)",
                                                      "-"): 692904},
                                     "product_slate": product_slate_dict
                                     }
    results = run_model(input_with_full_product_slate, return_dict=True)
    print("Full product slate data from external source.\n", results)

    # If "return_dict=False" is passed to the function results will be returned as a
    # list of lists instead of a dictionary. This option is used for writing to csv files
    # meant to be read by humans.

    results = run_model(input_with_full_product_slate, return_dict=False)
    print("Full product slate data from external source.\n", results)


if __name__ == "__main__":
    demo()
