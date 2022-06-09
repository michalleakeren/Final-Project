import numpy as np
from Preparations import *
from Utilities import *


def remove_baseline(signal,thresh=1):
    plt.figure()
    plt.axhline(y=thresh, color='g')
    baseline=0
    diff = np.diff(signal)
    a = np.diff(diff)
    output = []
    for i in range(len(signal)):
        if signal[i] < thresh:
            baseline = signal[i]
        output.append(signal[i] - baseline)
    plt.step(signal,'.-')
    plt.step(output,'.-')
    plt.grid()
    plt.show()

def check_if_sample_belong_to_curr_load(E_diffs,i,E_threshold,prev_E_diff):
    sample_belong_to_curr_load = 0
    if E_diffs[i] >= E_threshold:  # some load is ON
        if E_diffs[i] >= prev_E_diff:  # the energy dose grow
            if E_diffs[i]*0.4 < prev_E_diff:  # the energy dose doesnt change more than 60% than last dose
                sample_belong_to_curr_load = 1
        else: # E_diffs[i] < prev_E_diff
            if prev_E_diff*0.4 < E_diffs[i]: # the energy dose doesnt change more than 60% than last dose
                sample_belong_to_curr_load = 1
    return sample_belong_to_curr_load

def get_detected_loads(Ts,data_dict,phase,E_threshold):

    ###################################################
    ####### PART A - Find working load pattern ########
    ###################################################
    power = list(map(float, data_dict[f'kW L{phase}'][:]))
    Power_diff = np.diff(power)
    E_diffs = list(map(float, data_dict[f'dE{phase}'][:]))
    Loads = get_phase_loads(phase)
    found_loads_list = []
    time_of_last_load_found = 0
    results = []
    i = 1 #idx of E_diffs sample
    while i < len(E_diffs) - 1:
        plt.plot(E_diffs[:i],'o')
        ## PART A - find general monitoring pattern
        if E_diffs[i] < E_threshold:
            i += 1 #no activity. move to next sample.
        else:
            plt.axvline(x=i, color='g', linestyle='-')
            ON_idx = i
            ON_idx_count = 1
            Start_time = data_dict['StringTime'][ON_idx]
            double_time_start = data_dict['DoubleTime'][ON_idx + 1].astype(np.float64)
            power_diff = abs(Power_diff[i - 1])

            if E_diffs[i - 1] < E_threshold:
                noise_energy = E_diffs[i - 1] # update the noise level
            else: # E_diffs[i - 1] >= E_threshold
                noise_energy = E_threshold # define the noise level as the threshold

            prev_E_diff= E_diffs[i]
            Energy_jump = E_diffs[i] - noise_energy #change name!

            i += 1
            while (i < len(E_diffs)-1): #run over entier ON period

                sample_belong_to_curr_load = check_if_sample_belong_to_curr_load(E_diffs, i, E_threshold, prev_E_diff)
                if sample_belong_to_curr_load:
                    ON_idx_count += 1
                    OFF_idx = i
                    End_time = data_dict['StringTime'][OFF_idx]
                    double_time_end = data_dict['DoubleTime'][OFF_idx + 1].astype(np.float64)
                    power_diff = abs(Power_diff[i - 1])
                    prev_E_diff = E_diffs[i]
                    Energy_jump = Energy_jump + (E_diffs[i] - noise_energy)
                    i += 1
                else: #sample dosent belong to curr loads.
                    if (ON_idx_count == 1):
                        OFF_idx = i - 1
                        End_time = data_dict['StringTime'][OFF_idx]
                        double_time_end = data_dict['DoubleTime'][OFF_idx+1].astype(np.float64)
                    plt.axvline(x=i, color='black', linestyle='-')
                    break
            #OFF detected.
            if (i == len(E_diffs) - 1):
                # update manually end time of last sample
                OFF_idx = i
                End_time = data_dict['StringTime'][i]
            action_time = (double_time_end - double_time_start) / 1000.0

            ########################################################################
            ########## PART B - Match pattern to a specific load/loads #############
            ########################################################################

            # -------------------------------------------------------------------------------------#
            ######## Part B.1 - check if the energy diff we found matches one load only #######
            # -------------------------------------------------------------------------------------#

            possible_loads_list = []  #will include all the loads that might be active.

            for load in [l for l in Loads if Loads[l]["phase"] == phase]:
                # get load data - P and E limits
                Pmin = Loads[load]["Pmin"]
                Pmax = Loads[load]["Pmax"]
                Emin = Loads[load]["Emin"]
                Emax = Loads[load]["Emax"]


                # check the most important condition - energy diff:
                if (Emin > Energy_jump or Emax < Energy_jump):
                    continue
                if (phase == 2):
                    if (time_of_last_load_found != 0):
                        # check if we have 2 tami4 auto samples in less then 6 minutes
                        time_diff_between_last_load_to_current_load = (double_time_start - time_of_last_load_found) / 1000.0
                        if (load == "Tami4_auto" and time_diff_between_last_load_to_current_load < 360 and
                                found_loads_list[-1] == "Tami4_auto"):
                            continue
                        # check if we have 2 tami4 manual in less then 2 minutes
                        if (load == "Tami4_auto" and time_diff_between_last_load_to_current_load < 120 and found_loads_list[-1] == "Tami4_manual"):
                            continue
                    # for dishwasher - the modes have to be in the next order: 1,2,3,4
                    if ("Dishwasher_mode" in load):
                        if (check_chronological_condition(found_loads_list, load) == 0):
                            continue
                elif (phase == 3):
                    # for washing machine  - the modes have to be in the next order: 1, 2, 3, 4 ,5, 6
                    if ('washing_mode' in load):
                        if (check_chronological_condition(found_loads_list, load) == 0):
                            continue

                # if we reached here, we found load that is align with conditions - we will add him to possible loads list and decide later who is the best match
                possible_loads_list.append({'Load': load,
                                            "Start time": Start_time,
                                            "End time": End_time,
                                            "double_time_start": double_time_start,
                                            "double_time_end": double_time_end,
                                            "Emin": "{}".format("%.3f" % Emin),
                                            "Emax": "{}".format("%.3f" % Emax),
                                            "Energy_jump": "{}".format("%.3f" % Energy_jump),
                                            "Pmin": "{}".format("%.3f" % Pmin),
                                            "Pmax": "{}".format("%.3f" % Pmax),
                                            "Pdiff": "{}".format("%.3f" % power_diff),
                                            "ON_idx": ON_idx,
                                            "OFF_idx": OFF_idx,
                                            "overlapping_load": 0})

            # the decision:
            if (len(possible_loads_list) > 1):
                # case1 : washing machine mode4 & mode5 have the same properties but mode 4 comes before mode 5 always
                if ("washing_mode4" in possible_loads_list[0]['Load']  and "washing_mode5" in possible_loads_list[1]['Load']):
                    # remove list[1] and then we will have len == 1 for possible_loads_list
                    possible_loads_list.remove(possible_loads_list[1])

            if (len(possible_loads_list) == 1):
                last_load_found, time_of_last_load_found = update_loads_list(possible_loads_list[0]["Load"],
                                                                             found_loads_list, time_of_last_load_found,
                                                                             possible_loads_list[0][
                                                                                 "double_time_start"],
                                                                             possible_loads_list[0]["double_time_end"],
                                                                             results,
                                                                             possible_loads_list[0]["Start time"],
                                                                             possible_loads_list[0]["End time"],
                                                                             float(
                                                                                 possible_loads_list[0]["Energy_jump"]),
                                                                             float(possible_loads_list[0]["Emin"]),
                                                                             float(possible_loads_list[0]["Emax"]),
                                                                             float(possible_loads_list[0]["Pmin"]),
                                                                             float(possible_loads_list[0]["Pmax"]),
                                                                             float(possible_loads_list[0]["Pdiff"]),
                                                                             possible_loads_list[0]["ON_idx"],
                                                                             possible_loads_list[0]["OFF_idx"],
                                                                             possible_loads_list[0]["overlapping_load"])

            if (len(possible_loads_list) == 0):

                # ------------------------------------------------------------------------------------------------------------------------#
                ######## Part B.2 -  If we reached here, it is approximated that more than one load is working - overlapping loads #######
                # ------------------------------------------------------------------------------------------------------------------------#

                # we will check only the specific possible overlapping options.
                main_load, overlapping_loads = check_overlapping_options(found_loads_list, Energy_jump, phase, Loads)
                if (main_load != 0 and len(overlapping_loads) > 0):
                    if ("Dishwasher_mode" in main_load or "washing_mode" in main_load):
                        if (check_chronological_condition(found_loads_list, main_load) == 0):
                            continue

                    print(bcolors.BOLD + "Start Overlapping:" + bcolors.RESET)
                    last_load_found, time_of_last_load_found = update_loads_list(main_load, found_loads_list,
                                                                                 time_of_last_load_found,
                                                                                 double_time_start, double_time_end,
                                                                                 results, Start_time, End_time,
                                                                                 Loads[main_load]["Emin"],
                                                                                 Loads[main_load]["Emax"], Energy_jump,
                                                                                 Loads[main_load]["Pmin"],
                                                                                 Loads[main_load]["Pmax"], power_diff,
                                                                                 ON_idx, OFF_idx, 0)
                    middle_index_of_main_load = int((ON_idx + OFF_idx) / 2)
                    last_load_found, time_of_last_load_found = update_loads_list(overlapping_loads[0], found_loads_list,
                                                                                 time_of_last_load_found,
                                                                                 double_time_start, double_time_end,
                                                                                 results, Start_time, End_time,
                                                                                 Loads[overlapping_loads[0]]["Emin"],
                                                                                 Loads[overlapping_loads[0]]["Emax"],
                                                                                 Energy_jump,
                                                                                 Loads[overlapping_loads[0]]["Pmin"],
                                                                                 Loads[overlapping_loads[0]]["Pmax"], 0,
                                                                                 middle_index_of_main_load,
                                                                                 middle_index_of_main_load, 1)
                    if (len(overlapping_loads) > 1):
                        update_loads_list(overlapping_loads[1], found_loads_list,
                                          time_of_last_load_found,
                                          double_time_start,
                                          double_time_end, results,
                                          Start_time, End_time, Emin,
                                          Emax, Energy_jump, Pmin, Pmax,
                                          power_diff, ON_idx,
                                          OFF_idx, 0)
                    print(bcolors.BOLD + "End Overlapping" + bcolors.RESET)
    plt.figure()
    return found_loads_list, results

def check_overlapping_options(found_loads_list,Energy_jump,phase,Loads):
    overlapping_loads = []
    main_load = 0
    check_mode = 0
    if (phase == 1):
        if ( Loads["Toaster"]["Emax"] + Loads["Microwave"]["Emax"] >= Energy_jump):
            main_load = "Toaster"
            overlapping_loads.append("Microwave")

    elif (phase == 2):
        if (Energy_jump > Loads["Dishwasher_mode2"]["Emax"] and Energy_jump < Loads["Dishwasher_mode1"]["Emin"] and check_chronological_condition(found_loads_list, "Dishwasher_mode1") == 1):
            check_mode = 2
        elif (Energy_jump > Loads["Dishwasher_mode1"]["Emax"] and Energy_jump < Loads["Dishwasher_mode4"]["Emin"] and check_chronological_condition(found_loads_list, "Dishwasher_mode2") == 1):
            check_mode = 1
        elif (Energy_jump > Loads["Dishwasher_mode3"]["Emax"] and Energy_jump < Loads["Dishwasher_mode4"]["Emin"] and check_chronological_condition(found_loads_list, "Dishwasher_mode3") == 1):
            check_mode = 3
        elif (Energy_jump > Loads["Dishwasher_mode4"]["Emax"] and check_chronological_condition(found_loads_list,"Dishwasher_mode4") == 1):
            check_mode = 4
        if (check_mode != 0 ):
            if (Loads[f"Dishwasher_mode{check_mode}"]["Emax"] + Loads["Tami4_auto"]["Emax"] >= Energy_jump):
                main_load = "Dishwasher_mode{}".format(check_mode)
                overlapping_loads.append("Tami4_auto")
            elif (Loads[f"Dishwasher_mode{check_mode}"]["Emax"] + Loads["Tami4_manual"]["Emax"] >= Energy_jump):
                main_load = "Dishwasher_mode{}".format(check_mode)
                overlapping_loads.append("Tami4_manual")

    elif (phase == 3):
        if (Energy_jump > (Loads["washing_mode1"]["Emax"] + Loads["washing_mode2"]["Emax"]) and check_chronological_condition(found_loads_list, "Dishwasher_mode1") == 1):
            main_load = "washing_mode1"
            overlapping_loads.append("washing_mode2")
            overlapping_loads.append("washing_mode3")
        elif (Energy_jump > Loads["washing_mode1"]["Emax"] and check_chronological_condition(found_loads_list, "Dishwasher_mode1") == 1):
            if (Loads["washing_mode1"]["Emax"] + Loads["washing_mode2"]["Emax"] >= Energy_jump):
                main_load = "washing_mode1"
                overlapping_loads.append("washing_mode2")
        elif ((Energy_jump > Loads["washing_mode2"]["Emax"]) and (Loads["washing_mode2"]["Emax"] + Loads["washing_mode3"]["Emax"] > Energy_jump) and check_chronological_condition(found_loads_list, "Dwashing_mode2") == 1 ):
            if (Loads["washing_mode2"]["Emax"] + Loads["washing_mode3"]["Emax"] > Energy_jump):
                main_load = "washing_mode2"
                overlapping_loads.append("washing_mode3")


    return main_load, overlapping_loads

def check_chronological_condition(found_loads_list,load):
    # this function will check that loads that have several modes will have chronological order, i.e. Dishwasher mode 1 will be first and then mode 2 , mode 3, ....
    if (load in found_loads_list):
        return 0

    operation_mode_of_current_load = int(load[-1])

    for tested_load in found_loads_list:
        if tested_load[:-1] in load:
            operation_mode_of_tested_load = int(tested_load[-1])
            if operation_mode_of_tested_load > operation_mode_of_current_load:
                return 0
    return 1

def update_loads_list(load,found_loads_list, time_of_last_load_found,double_time_start,double_time_end, results, Start_time, End_time, Energy_jump,Emin, Emax, Pmin, Pmax, power_diff,ON_idx,OFF_idx,overlapping_load):
    last_load_found = load
    if (load == "Tami4_auto" or load == "Tami4_manual"):
        time_of_last_load_found = double_time_start
    found_loads_list.append(load)
    results.append({'Load': load,
                    "Start time": Start_time,
                    "End time": End_time,
                    "double_time_start": double_time_start,
                    "double_time_end": double_time_end,
                    "Emin": "{}".format("%.3f" % Emin),
                    "Emax": "{}".format("%.3f" % Emax),
                    "Energy_jump": "{}".format("%.3f" % Energy_jump),
                    "Pmin": "{}".format("%.3f" % Pmin),
                    "Pmax": "{}".format("%.3f" % Pmax),
                    "Pdiff": "{}".format("%.3f" % power_diff),
                    "ON_idx": ON_idx,
                    "OFF_idx":OFF_idx,
                    "overlapping_load":overlapping_load})

    print(bcolors.OKBLUE + load + bcolors.RESET, "start time: {}".format(Start_time),
          "end time: {}".format(End_time), "Emin: {}".format("%.3f" % Emin),
          "Emax: {}".format("%.3f" % Emax),
          "Energy_jump: {}".format(bcolors.FAIL + "%.3f" % Energy_jump + bcolors.RESET),
          "Pmin: {}".format("%.3f" % Pmin), "Pmax: {}".format("%.3f" % Pmax),
          "Pdiff: {}".format(bcolors.FAIL + "%.3f" % power_diff + bcolors.RESET))

    return (last_load_found ,time_of_last_load_found)

def unique(list):
    output = []
    for x in list:
        if x not in output:
            output.append(x)
    return output


def detection_summary(file_name,time_for_one_sec,data_dict,Ts,found_loads_list,results,phase):
    # list for visualisation of results:
    file_length = len(time_for_one_sec)
    visual_results_all_loads = [np.nan] * file_length
    visual_results_per_load = [np.nan] * file_length
    loads_unique_list = unique(found_loads_list)
    colors = ["magenta","lime","blue","deepskyblue","darkorange","blueviolet"]
    k = 0
    for idx in range(len(loads_unique_list)):
        load = loads_unique_list[idx]
    #for load in loads_unique_list:
        for i in range(len(results)):
            if (results[i]["Load"] == load):
                Pmin = float (results[i]["Pmin"])
                Pmax = float (results[i]["Pmax"])
                ON_idx = int(results[i]["ON_idx"] * Ts/2)
                OFF_idx = int(results[i]["OFF_idx"] * Ts/2)
                if (results[i]["overlapping_load"] == 1):
                    # fix index for overlapping load
                    ON_idx = ON_idx
                    OFF_idx = OFF_idx

                power_for_print = (Pmax + Pmin)/2.0
                if (visual_results_all_loads[ON_idx-1] != np.nan and visual_results_all_loads[ON_idx-1] != 0 and  results[i]["overlapping_load"] == 1):
                    visual_results_per_load[ON_idx-2] = visual_results_all_loads[ON_idx-2]
                    visual_results_per_load[OFF_idx] = visual_results_all_loads[OFF_idx]
                else:
                    visual_results_per_load[ON_idx - 2] = 0
                    visual_results_per_load[OFF_idx] = 0
                for j in range(ON_idx-1,OFF_idx):

                    visual_results_per_load[j] = 0
                    if (visual_results_all_loads[j] != np.nan and visual_results_all_loads[j] != 0 and results[i]["overlapping_load"] == 1):
                        visual_results_per_load[j] += visual_results_all_loads[j]
                    visual_results_per_load[j] += power_for_print

                    visual_results_all_loads[j] = 0
                    visual_results_all_loads[j] += visual_results_per_load[j]

        update_visual_results(visual_results_per_load,colors[k],load,time_for_one_sec)
        visual_results_per_load = [np.nan] * file_length

        k += 1

    update_visual_results([0] * file_length,"white","none",time_for_one_sec)



def update_visual_results(visual_results_per_load, color, load, time_for_one_sec):
    # ---Time---#
    time = time_for_one_sec
    time = [time[i][10:18] for i in range(len(time))]  # keep the '%H:%M:%S' only.
    time = [dateutil.parser.parse(s) for s in time]
    plt.step(time, visual_results_per_load,'.-', color=color,label = load)  # 'step' is the zero order interpolation plot function.  # 'step' is the zero order interpolation plot function.
    plt.gcf()
    if (load != "none"):
        plt.legend(loc="upper right", prop={'size': 8})



