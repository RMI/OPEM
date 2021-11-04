from opem import run_model


def demo():

    # Parameter object with input as list of lists
    list_input = {"user_input": [["User Inputs & Results",
                                  "Global:",
                                  "Assay (Select Oil)",
                                  "-",
                                  "Algeria Hassi R’Mel"],
                                 ["User Inputs & Results",
                                 "Global:",
                                  "Gas Production Volume (MCFD)",
                                  "-",
                                  600000],
                                 ["User Inputs & Results",
                                 "Global:",
                                  "Oil Production Volume (BOED)",
                                  "-",
                                  100000],
                                 ["User Inputs & Results",
                                 "Global:",
                                  "% Field NGL C2 Volume allocated to Ethylene converstion",
                                  "-",
                                  1],
                                 ["User Inputs & Results",
                                 "Global:",
                                  "GWP selection (yr period, 100 or 20)",
                                  "-",
                                  100]]
                  }
    results = run_model(list_input, return_dict=False)
    print("List inputs\n", results)

    # Parameter object with input as dictionary
    dict_input = {"user_input": {("User Inputs & Results",
                                  "Global:",
                                  "Assay (Select Oil)",
                                  "-"):
                                 "Canada Athabasca DC SCO",
                                 ("User Inputs & Results",
                                  "Global:",
                                  "Gas Production Volume (MCFD)",
                                  "-"): 600000,
                                 ("User Inputs & Results",
                                  "Global:",
                                  "Oil Production Volume (BOED)",
                                  "-"): 100000,
                                 ("User Inputs & Results",
                                 "Global:",
                                  "% Field NGL C2 Volume allocated to Ethylene converstion",
                                  "-"):
                                 1,
                                 ("User Inputs & Results",
                                 "Global:",
                                  "GWP selection (yr period, 100 or 20)",
                                  "-"):
                                 100}
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
                                            "-"): "Canada Athabasca DC SCO",
                                           ("User Inputs & Results",
                                            "Global:",
                                            "% Field NGL C2 Volume allocated to Ethylene converstion",
                                            "-"):
                                           1,
                                           ("User Inputs & Results",
                                            "Global:",
                                            "GWP selection (yr period, 100 or 20)",
                                            "-"):
                                           100},
                            "opgee_input": {("User Inputs & Results",
                                             "Global:",
                                             "Gas Production Volume (MCFD)",
                                             "-"): 600000,
                                            ("User Inputs & Results",
                                            "Global:",
                                             "Oil Production Volume (BOED)",
                                             "-"): 100000}
                            }
    results = run_model(separate_opgee_input, return_dict=True)
    print("OPGEE input parameters separated from others\n", results)

    # Full product slate data passed in under the "product_slate" key.
    # Use this option to run the model with an oil that is not in the
    # interal "all_product_slates.csv"

    # Product slate data can be structured as a list of lists or as a dictionary
    product_slate_list = [['product_name', '', 'Angola Kuito'],
                          ['volume_flow_bbl', 'Barrels of Crude per Day',
                           'Flow', 96240.38798],
                          ['volume_flow_bbl', 'Gasoline', 'Flow', 48981.75874],
                          ['volume_flow_bbl', 'Jet Fuel', 'Flow', 10217.02334],
                          ['volume_flow_bbl', 'Diesel', 'Flow', 34222.39197],
                          ['volume_flow_bbl', 'Fuel Oil', 'Flow', 3.2e-08],
                          ['volume_flow_bbl', 'Coke', 'Flow', 7919.203734],
                          ['volume_flow_bbl', 'Residual fuels', 'Flow', 3807.856089],
                          ['volume_flow_bbl',
                           'Surplus Refinery Fuel Gas (RFG)', 'Flow', 0.0],
                          ['volume_flow_bbl',
                           'Liquefied Petroleum Gases (LPG)', 'Flow', 5966.874498],
                          ['volume_flow_bbl', 'Petrochemical Feedstocks', 'Flow', 0.0],
                          ['volume_flow_bbl', 'Asphalt', 'Flow', 0.0],
                          ['energy_flow_MJ', 'Gasoline', 'Flow', 241756398.7],
                          ['energy_flow_MJ', 'Jet Fuel', 'Flow', 54484505.27],
                          ['energy_flow_MJ', 'Diesel', 'Flow', 185084562.4],
                          ['energy_flow_MJ', 'Fuel Oil', 'Flow', 0.000173091],
                          ['energy_flow_MJ', 'Coke', 'Flow', 52235911.74],
                          ['energy_flow_MJ', 'Residual fuels', 'Flow', 23600695.82],
                          ['energy_flow_MJ', 'Surplus RFG', 'Flow', 0.0],
                          ['energy_flow_MJ', 'Surplus NCR H2', 'Flow', 0.0],
                          ['energy_flow_MJ',
                           'Liquefied Petroleum Gases (LPG)', 'Flow', 22305500.16],
                          ['energy_flow_MJ', 'Petrochemical Feedstocks',
                           'Flow', 13719295.11],
                          ['energy_flow_MJ', 'Asphalt', 'Flow', 0.0],
                          ['energy_flow_MJ', 'Gasoline S wt%', 'Flow', 5.53e-05],
                          ['energy_flow_MJ', 'Gasoline H2 wt%', 'Flow', 14.6773632],
                          ['mass_flow_kg', 'Gasoline', 'Flow', 5695261.684],
                          ['mass_flow_kg', 'Jet Fuel', 'Flow', 1312496.58],
                          ['mass_flow_kg', 'Diesel', 'Flow', 4480095.988],
                          ['mass_flow_kg', 'Fuel Oil', 'Flow', 4.19e-06],
                          ['mass_flow_kg', 'Coke', 'Flow', 1436579.267],
                          ['mass_flow_kg', 'Residual fuels', 'Flow', 611454.766],
                          ['mass_flow_kg', 'Sulphur', 'Flow', 85629.88757],
                          ['mass_flow_kg', 'Surplus RFG', 'Flow', 0.0],
                          ['mass_flow_kg', 'Surplus NCR H2', 'Flow', 0.0],
                          ['mass_flow_kg',
                           'Liquefied Petroleum Gases (LPG)', 'Flow', 481920.5857],
                          ['mass_flow_kg', 'Petrochemical Feedstocks', 'Flow', 0.0],
                          ['mass_flow_kg', 'Asphalt', 'Flow', 0.0],
                          ['mass_flow_kg', 'Net Upstream Petcoke', 'Flow', 0.0]]

    product_slate_dict = {('product_name', ''): 'Angola Kuito',
                          ('volume_flow_bbl', 'Barrels of Crude per Day',
                           'Flow'): 96240.38798,
                          ('volume_flow_bbl', 'Gasoline', 'Flow'): 48981.75874,
                          ('volume_flow_bbl', 'Jet Fuel', 'Flow'): 10217.02334,
                          ('volume_flow_bbl', 'Diesel', 'Flow'): 34222.39197,
                          ('volume_flow_bbl', 'Fuel Oil', 'Flow'): 3.2e-08,
                          ('volume_flow_bbl', 'Coke', 'Flow'): 7919.203734,
                          ('volume_flow_bbl', 'Residual fuels', 'Flow'): 3807.856089,
                          ('volume_flow_bbl',
                           'Surplus Refinery Fuel Gas (RFG)', 'Flow'): 0.0,
                          ('volume_flow_bbl',
                           'Liquefied Petroleum Gases (LPG)', 'Flow'): 5966.874498,
                          ('volume_flow_bbl', 'Petrochemical Feedstocks', 'Flow'): 0.0,
                          ('volume_flow_bbl', 'Asphalt', 'Flow'): 0.0,
                          ('energy_flow_MJ', 'Gasoline', 'Flow'): 241756398.7,
                          ('energy_flow_MJ', 'Jet Fuel', 'Flow'): 54484505.27,
                          ('energy_flow_MJ', 'Diesel', 'Flow'): 185084562.4,
                          ('energy_flow_MJ', 'Fuel Oil', 'Flow'): 0.000173091,
                          ('energy_flow_MJ', 'Coke', 'Flow'): 52235911.74,
                          ('energy_flow_MJ', 'Residual fuels', 'Flow'): 23600695.82,
                          ('energy_flow_MJ', 'Surplus RFG', 'Flow'): 0.0,
                          ('energy_flow_MJ', 'Surplus NCR H2', 'Flow'): 0.0,
                          ('energy_flow_MJ',
                           'Liquefied Petroleum Gases (LPG)', 'Flow'): 22305500.16,
                          ('energy_flow_MJ', 'Petrochemical Feedstocks',
                           'Flow'): 13719295.11,
                          ('energy_flow_MJ', 'Asphalt', 'Flow'): 0.0,
                          ('energy_flow_MJ', 'Gasoline S wt%', 'Flow'): 5.53e-05,
                          ('energy_flow_MJ', 'Gasoline H2 wt%', 'Flow'): 14.6773632,
                          ('mass_flow_kg', 'Gasoline', 'Flow'): 5695261.684,
                          ('mass_flow_kg', 'Jet Fuel', 'Flow'): 1312496.58,
                          ('mass_flow_kg', 'Diesel', 'Flow'): 4480095.988,
                          ('mass_flow_kg', 'Fuel Oil', 'Flow'): 4.19e-06,
                          ('mass_flow_kg', 'Coke', 'Flow'): 1436579.267,
                          ('mass_flow_kg', 'Residual fuels', 'Flow'): 611454.766,
                          ('mass_flow_kg', 'Sulphur', 'Flow'): 85629.88757,
                          ('mass_flow_kg', 'Surplus RFG', 'Flow'): 0.0,
                          ('mass_flow_kg', 'Surplus NCR H2', 'Flow'): 0.0,
                          ('mass_flow_kg',
                           'Liquefied Petroleum Gases (LPG)', 'Flow'): 481920.5857,
                          ('mass_flow_kg', 'Petrochemical Feedstocks', 'Flow'): 0.0,
                          ('mass_flow_kg', 'Asphalt', 'Flow'): 0.0,
                          ('mass_flow_kg', 'Net Upstream Petcoke', 'Flow'): 0.0}

    # If an oil name is included under "user_input", it will be ignored and
    # and the product slate data under the "product_slate" key will be used.

    input_with_full_product_slate = {"user_input": {("User Inputs & Results",
                                                     "Global:",
                                                     "% Field NGL C2 Volume allocated to Ethylene converstion",
                                                     "-"):
                                                    1,
                                                    ("User Inputs & Results",
                                                     "Global:",
                                                     "GWP selection (yr period, 100 or 20)",
                                                     "-"):
                                                    100},
                                     "opgee_input": {("User Inputs & Results",
                                                      "Global:",
                                                      "Gas Production Volume (MCFD)",
                                                      "-"): 600000,
                                                     ("User Inputs & Results",
                                                      "Global:",
                                                      "Oil Production Volume (BOED)",
                                                      "-"): 100000},
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
