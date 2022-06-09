import matplotlib.pyplot as plt
import timeit
from Data import *
from Utilities import *
from RT_Detection import *
from Preparations import *
import time


#padd the Results vector to have the number of sampels as the original (before dilution).
def get_padded_results(Result,high_freq_data_dict,diluted_data_dict, phase):
    T_orig = high_freq_data_dict["StringTime"]
    T_diluted = diluted_data_dict["StringTime"]
    res_i = 0
    padded_res = []
    for i in range(len(T_orig)):
        if T_orig[i] == T_diluted[res_i]:

            padded_res.append(Result[res_i])
            res_i += 1
        else:
            if res_i != 0:
                padded_res.append(Result[res_i-1])
            else:
                padded_res.append(Result[res_i])
    padded_res = np.array(padded_res)
    return padded_res


#unite all the dishwasher modes.
def prep_results(Results, phase, idx_2_load,idx_2_P_av):
    if phase == 2:
        legend = [idx_2_load[0],idx_2_load[1],'Dishwasher', 'AC']
        new_idx_2_P_av = [idx_2_P_av[0], idx_2_P_av[1], idx_2_P_av[3], idx_2_P_av[6]]
        output = np.zeros((len(Results),4))
        output[:,0:2] = Results[:,0:2] #Tami 4
        output[:,2] = np.sum(Results[:,2:6],1) #Dishwasher
        output[:,3] = Results[:,6] #AC
        return output, legend, new_idx_2_P_av
    else:
        return Results, idx_2_load, idx_2_P_av


def plot_results(Result,high_freq_data_dict,diluted_data_dict,phase):
    idx_2_load, idx_2_P_av = get_loads_options_in_vectors(phase)[1:3]
    Results, legend,P_av = prep_results(Result, phase, idx_2_load, idx_2_P_av)
    padded_Result = get_padded_results(Results,high_freq_data_dict,diluted_data_dict, phase)

    plt.figure()
    str_P_orig = high_freq_data_dict[f'kW L{phase}']
    P_orig = [float(x) for x in str_P_orig]
    time = high_freq_data_dict['StringTime']

    plt.subplot(2,1,1)
    plot_with_time_as_x(data=P_orig , time=time, color= "black", label="Ts= 1sec")
    plt.grid()
    plt.legend()
    plt.subplot(2, 1, 2)

    for i in range(len(padded_Result[0])):
        scaled_res = padded_Result[:, i]*P_av[i]
        plot_with_time_as_x(data=scaled_res, time=time,label=legend[i])
    plt.grid()
    plt.legend()


def get_GT_result(file_name, Results, Ts):
    output = Results.copy()
    if file_name == '240921_gener_1':
        output[4] = [0,0,1,0,0,0,0,0]
        output[22] = [0, 0, 1, 0, 0, 0, 0, 0]
        output[91] = [0, 1, 0, 0, 0, 0, 0, 0]
        output[104] = [0, 1, 0, 0, 0, 0, 0, 0]
        output[112] = [0, 0, 1, 0, 0, 0, 0, 0]
    elif file_name == 'stream_1':
        if Ts == 3*60:
            output[48] = [1,0,0]
        elif Ts == 1*60:
            output[1:44] = [0,0,1]
            output[81] = [1, 0, 0]
            output[82] = [0, 0, 0]
            output[83:85] = [0, 1, 0]
            output[85:119] = [0, 0, 0]
            output[119] = [1, 0, 0]
            output[140] = [1, 0, 0]
    return output


def plot_results_with_GT(Result, GT_Result, high_freq_data_dict,diluted_data_dict,phase,Ts):
    plt.figure()
    if phase == 2:
        colors = ["aqua", "orange", "magenta", "blue"]
    elif phase == 1:
        colors = ["lime", "salmon", "mediumorchid"]
    idx_2_load, idx_2_P_av = get_loads_options_in_vectors(phase)[1:3]

    Results, legend,P_av = prep_results(Result, phase, idx_2_load, idx_2_P_av)
    padded_Result = get_padded_results(Results, high_freq_data_dict, diluted_data_dict, phase)

    GT_Results, legend,P_av = prep_results(GT_Result, phase, idx_2_load, idx_2_P_av)
    padded_GT_Result = get_padded_results(GT_Results,high_freq_data_dict,diluted_data_dict, phase)

    str_P_orig = high_freq_data_dict[f'kW L{phase}']
    P_orig = [float(x) for x in str_P_orig]
    time = high_freq_data_dict['StringTime']

    str_P_dill = diluted_data_dict[f'kW L{phase}']
    P_dill = [float(x) for x in str_P_dill]
    dill_time = diluted_data_dict['StringTime']

    plt.subplot(3,1,1)
    plot_with_time_as_x(data=P_dill, time=dill_time, color='', plot_type='scater',label=f"Ts = {int(Ts / 60)}min")
    plot_with_time_as_x(data=P_orig, time=time, color="gray", label="Ts = 1sec")
    plt.grid()
    plt.legend()
    plt.title("(a) Total Power Samples")

    plt.subplot(3, 1, 2)
    for i in range(len(padded_Result[0])):
        scaled_res = padded_Result[:, i]*P_av[i]
        plot_with_time_as_x(data=scaled_res, time=time,
                      color=colors[i], label=legend[i] )
    plt.grid()
    plt.legend(bbox_to_anchor=(1.01, 1.05))
    plt.title('(b) Estimated Disaggregated Power Consumption')
    plt.ylabel("Power [kW]")

    plt.subplot(3, 1, 3)
    for i in range(len(padded_GT_Result[0])):
        scaled_res = padded_GT_Result[:, i]*P_av[i]
        plot_with_time_as_x(data=scaled_res, time=time,label=legend[i], color=colors[i])
    plt.grid()
    plt.legend(bbox_to_anchor=(1.01, 1.05))
    plt.title('(C) True Disaggregated Power Consumption')
    plt.xlabel("t [h:m]")
    plt.subplot_tool()






def plot_results_analysis(Result, high_freq_data_dict,diluted_data_dict,phase,Ts):
    plt.figure()
    idx_2_load, idx_2_P_av = get_loads_options_in_vectors(phase)[1:3]
    Results, legend,P_av = prep_results(Result, phase, idx_2_load, idx_2_P_av)
    str_P_dill = diluted_data_dict[f'kW L{phase}']
    P_dill = [float(x) for x in str_P_dill]
    dill_time = diluted_data_dict['StringTime']
    E_diffs = list(map(float, diluted_data_dict[f'dE{phase}']))
    ddE = list(np.diff(E_diffs))
    ddE.insert(0, 0)
    n= -50
    P_dill= P_dill[n:]
    dill_time = dill_time[n:]
    E_diffs= E_diffs[n:]
    ddE = ddE[n:]
    Results= Results[n:]
    colors = ["aqua", "orange", "magenta", "blue"]
    plt.subplot(4,1,1)
    for i in range(len(Results[0])):
        scaled_res = Results[:, i]*P_av[i]
        plot_with_time_as_x(data=scaled_res, time=dill_time,
                            color=colors[i], label=legend[i])
    plt.grid()
    plt.legend(bbox_to_anchor=(1.01, 1.05))
    plt.ylabel("P [kW]")
    plt.title('(a) Estimated Disaggregated Power Consumption')

    plt.subplot(4, 1, 2)
    plot_with_time_as_x(data=P_dill, time=dill_time, color='', label=f"Ts = {int(Ts / 60)}min")
    plt.legend()
    plt.title("(b) Power(t)")
    plt.ylabel("P [kW]")
    plt.grid()


    plt.subplot(4, 1, 3)
    plot_with_time_as_x(data=E_diffs, time=dill_time, color='', label=f"Ts = {int(Ts / 60)}min")
    plt.legend()
    plt.title("(c) Energy Dose(t)")
    plt.ylabel("\u0394E [kW/min]")
    plt.grid()

    plt.subplot(4, 1, 4)
    plot_with_time_as_x(data=ddE, time=dill_time, color='', label=f"Ts = {int(Ts / 60)}min")
    plt.legend()
    plt.title("(d) Energy Acceleration (t)")
    plt.ylabel("\u0394\u0394E [kW/min]")
    plt.grid()
    plt.xlabel("t [h:m]")

    plt.subplot_tool()