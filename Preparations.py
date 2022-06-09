import matplotlib.pyplot as plt
import numpy as np

documented_file_names = ['stream_1','stream_1_edited','stream_2_no_beg','wachingmachi_edited','150921_washi']

def get_loads_options_in_vectors(phase):
    Loads_vectors =[]
    idx_2_load = []
    if phase == 1:
        idx_2_load = ["Microwave", "Toaster", "Dryer"]
        idx_2_P_av = [1.33, 0.9, 2]
        idx_2_T_av = [29, 137, 4 * 60]
        panilty_4_consecutive = [1, 1, 0]
        Loads_vectors = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1], [1, 1, 1]]

    elif phase == 2:

        idx_2_load = ["Tami4_auto", "Tami4_manual", "Dishwasher_mode1","Dishwasher_mode2","Dishwasher_mode3","Dishwasher_mode4",
                      "AC","doubleAC"]

        idx_2_P_av = [1.93, 1.93, 1.95, 1.96, 1.996, 2,
                      0.72, 1.8]

        idx_2_T_av = [9,40,(491+620)/2, (265+312)/2, (660+692)/2, (1023+1156)/2
                      ,10*60,10*60]

        panilty_4_consecutive = [1,1,0,0,0,0,0,0]
        Loads_vectors = [[0,0,0,0,0,0,0,0],[1,0,0,0,0,0,0,0],[0,1,0,0,0,0,0,0],
                         [0,0,1,0,0,0,0,0],[0,0,0,1,0,0,0,0], [0,0,0,0,1,0,0,0], [0,0,0,0,0,1,0,0],
                         [0,0,1,0,0,0,1,0],[0,0,0,1,0,0,1,0], [0,0,0,0,1,0,1,0], [0,0,0,0,0,1,1,0],
                         [0,1,1,0,0,0,0,0],[0,1,0,1,0,0,0,0], [0,1,0,0,1,0,0,0], [0,1,0,0,0,1,0,0],
                         [1,0,1,0,0,0,0,0],[1,0,0,1,0,0,0,0],[1,0,0,0,1,0,0,0],
                         [1,0,0,0,0,1,0,0], [0,0,0,0,0,0,1,0],[1,0,0,0,0,0,1,0]]
    return Loads_vectors, idx_2_load, idx_2_P_av,idx_2_T_av, panilty_4_consecutive

def get_phase_loads(phase):
    Loads = {}
    # [P]=kW, [T]=sec, [prob]= %

    if phase == 1:
        Loads["Microwave"] = {"phase": 1, 'Pmin': 1.39 * 0.97, 'Pmax': 1.44 * 1.03, "Tmin": 29 * 0.75, "Tmax": 59 * 1.25,
                              "Emin": 10, 'Emax': 45, 'phase_prob': 80}
        Loads["Toaster"] = {"phase": 1, 'Pmin': 0.90 * 0.97, 'Pmax': 0.91 * 1.03, "Tmin": 137 * 0.75, "Tmax": 137 * 1.25,
                            "Emin": 51, 'Emax': 70, 'phase_prob': 80}
        Loads["Dryer"] = {"phase": 1, 'Pmin': 1.87 * 0.97, 'Pmax': 2.00 * 1.03, "Tmin": 236 * 0.75, "Tmax": 238 * 1.25,
                          "Emin": 300, 'Emax': 500, 'phase_prob': 80}

    if phase == 2:
        Loads["Tami4_auto"] = {"phase": 2, 'Pmin': 1.93 * 0.96, 'Pmax': 2.00 * 1.03, "Tmin": 9, "Tmax": 30, "Emin": 0.01,
                               'Emax': 79, 'phase_prob': 80}
        Loads["Tami4_manual"] = {"phase": 2, 'Pmin': 1.92 * 0.97, 'Pmax': 2.00 * 1.03, "Tmin": 100, "Tmax": 115, "Emin": 79.5,
                                 'Emax': 160, 'phase_prob': 20}

        Loads["Dishwasher_mode1"] = {"phase": 2, 'Pmin': 1.85 * 0.97, 'Pmax': 1.95 * 1.03, "Tmin": 491 * 0.90,
                                     "Tmax": 620 * 1.10, "Emin": 510, 'Emax': 595, 'phase_prob': 80}

        Loads["Dishwasher_mode2"] = {"phase": 2, 'Pmin': 1.874 * 0.97, 'Pmax': 1.903 * 1.03, "Tmin": 265 * 0.90,
                                     "Tmax": 312 * 1.10, "Emin": 240, 'Emax': 305, 'phase_prob': 80}

        Loads["Dishwasher_mode3"] = {"phase": 2, 'Pmin': 1.863 * 0.97, 'Pmax': 1.935 * 1.03, "Tmin": 660 * 0.90,
                                     "Tmax": 692 * 1.10, "Emin": 500, 'Emax': 621, 'phase_prob': 80}

        Loads["Dishwasher_mode4"] = {"phase": 2, 'Pmin': 1.85 * 0.97, 'Pmax': 2.00 * 1.03, "Tmin": 1023 * 0.90,
                                     "Tmax": 1156 * 1.10, "Emin": 1070, 'Emax': 1130, 'phase_prob': 80}
        # Loads["Main_aircond"] = {"phase": 2, 'Pmin': 0.70 * 0.97, 'Pmax': 0.89 * 1.03, "Tmin": 0.1 * 0.90,
        #                          "Tmax": 999 * 1.10, "Emin": 0.75 * (0.70 * 0.97 * 0.1 * 0.90),
        #                          'Emax': 1.25 * (0.89 * 1.03 * 999 * 1.10), 'phase_prob': 80}

    if phase == 3:
        Loads["washing_mode1"] = {"phase": 3, 'Pmin': 1.95 * 0.97, 'Pmax': 2.00 * 1.03, "Tmin": 367 * 0.9,
                                  "Tmax": 367 * 1.10, "Emin": 770, 'Emax': 850, 'phase_prob': 80}
        Loads["washing_mode2"] = {"phase": 3, 'Pmin': 1.95 * 0.97, 'Pmax': 2.00 * 1.03, "Tmin": 644 * 0.9,
                                  "Tmax": 644 * 1.10, "Emin": 65, 'Emax': 80, 'phase_prob': 80}
        Loads["washing_mode3"] = {"phase": 3, 'Pmin': 1.95 * 0.97, 'Pmax': 2.00 * 1.03, "Tmin": 644 * 0.9,
                                  "Tmax": 644 * 1.10, "Emin": 50, 'Emax': 75, 'phase_prob': 80}
        Loads["washing_mode4"] = {"phase": 3, 'Pmin': 0.33 * 0.97, 'Pmax': 0.35 * 1.03, "Tmin": 644 * 0.9,
                                  "Tmax": 644 * 1.10, "Emin": 2, 'Emax': 15, 'phase_prob': 80}
        Loads["washing_mode5"] = {"phase": 3, 'Pmin': 0.33 * 0.97, 'Pmax': 0.35 * 1.03, "Tmin": 644 * 0.9,
                                  "Tmax": 644 * 1.10, "Emin": 2, 'Emax': 15, 'phase_prob': 80}
        Loads["washing_mode6"] = {"phase": 3, 'Pmin': 0.37 * 0.97, 'Pmax': 0.40 * 1.03, "Tmin": 644 * 0.9,
                                  "Tmax": 644 * 1.10, "Emin": 20, 'Emax': 40, 'phase_prob': 80}

    return Loads

def get_documented_loads(file_name): #need to fix duch that input is file name and phase.

    if file_name not in documented_file_names:
        raise ValueError('the given file dose not have a doucumentation')

    ###-select MDB file name-###
    Loads_comparison_phase1 = {}
    Loads_comparison_phase2 = {}
    Loads_comparison_phase3 = {}

    # file_name = 'stream_1'
    Loads_comparison_phase1["stream_1"] = ["Microwave", "Toaster", "Microwave", "Microwave", "Microwave"]
    Loads_comparison_phase2["stream_1"] = ["Tami4_manual", "Tami4_auto", "Dishwasher_mode1",
                                           "Tami4_auto", "Dishwasher_mode2",
                                           "Tami4_auto", "Tami4_auto",
                                           "Dishwasher_mode3", "Tami4_auto",
                                           "Tami4_auto", "Tami4_auto",
                                           "Tami4_auto", "Tami4_auto",
                                           "Dishwasher_mode4", "Tami4_auto",
                                           "Tami4_auto", "Tami4_auto"]

    # file_name = 'stream_1_edited'
    Loads_comparison_phase1["stream_1_edited"] = ["Microwave", "Toaster", "Microwave", "Microwave"]
    Loads_comparison_phase2["stream_1_edited"] = ["Tami4_manual", "Tami4_auto", "Dishwasher_mode1",
                                                  "Tami4_auto", "Dishwasher_mode2",
                                                  "Tami4_auto", "Tami4_auto",
                                                  "Dishwasher_mode3",
                                                  "Tami4_auto", "Tami4_auto",
                                                  "Tami4_auto", "Tami4_auto",
                                                  "Dishwasher_mode4",
                                                  "Tami4_auto", "Tami4_auto"]

    Loads_comparison_phase2["stream_2_no_beg"] = ["Tami4_auto", "Tami4_manual", "Tami4_manual"]

    file_name = '180921_washi'

    Loads_comparison_phase3['wachingmachi_edited'] = ["washing_mode1", "washing_mode2", "washing_mode3",
                                                      "washing_mode4", "washing_mode5", "washing_mode6"]
    Loads_comparison_phase3["150921_washi"] = ["washing_mode1", "washing_mode2", "washing_mode3", "washing_mode4",
                                               "washing_mode5", "washing_mode6"]
    Loads_comparison_phase3["180921_washi"] = ["washing_mode1", "washing_mode2", "washing_mode3", "washing_mode4",
                                               "washing_mode5", "washing_mode6"]
    return Loads_comparison_phase1, Loads_comparison_phase2, Loads_comparison_phase3


# set Power and Energy minimum thresholds:
def get_thresholds(phase, Ts):
    if (phase == 1):
        P_threshold = 0.6
        if (Ts == 60):
            E_threshold = 20
        elif (Ts == 120):
            E_threshold = 28
        elif (Ts == 180):
            E_threshold = 42
        elif (Ts == 240):
            E_threshold = 50
        elif (Ts == 300):
            E_threshold = 62
        else:
            E_threshold = 20
    elif (phase == 2):
        P_threshold = 0.6
        E_threshold_est = get_dE_threshold_est()
        E_threshold = E_threshold_est(Ts)
    elif (phase == 3):
        P_threshold = 0.35
        E_threshold = 5.5
        if (Ts >= 180):
            E_threshold = 10
        if (Ts == 300):
            E_threshold = 12
    return P_threshold, E_threshold



def get_dE_threshold_est():
    thresholds = [18,23,32, 39.5, 44]
    matching_Ts = [60,120,180,240,300]
    tresh_est = np.poly1d(np.polyfit(matching_Ts,thresholds,1))
    return tresh_est

