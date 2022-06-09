import csv, pyodbc
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import dateutil
import queue
from Utilities import *
from Data import *
from Preparations import *

def on_off_fifo(data_dict,phase,treshold, param):
    power_dict1 = list(map(float, data_dict['kW L1'][:]))
    power_dict2 = list(map(float, data_dict['kW L2'][:]))
    power_dict3 = list(map(float, data_dict['kW L3'][:]))
    dP = [np.diff(power_dict1), np.diff(power_dict2), np.diff(power_dict3)]
    dEnergy_dict1 = list(map(float, data_dict['dE1'][:]))
    dEnergy_dict2 = list(map(float, data_dict['dE2'][:]))
    dEnergy_dict3 = list(map(float, data_dict['dE3'][:]))
    dE = [dEnergy_dict1, dEnergy_dict2, dEnergy_dict3]
    ddE = [np.diff(dEnergy_dict1), np.diff(dEnergy_dict2), np.diff(dEnergy_dict3)]

    # for correct phase
    phase = phase - 1
    on_off_fifo_calc(ddE=ddE[phase],dE=dE[phase],data_dict=data_dict,dP=dP[phase],treshold=treshold,phase=phase, param=param)

def on_off_fifo_calc(ddE,dE,data_dict,dP,treshold,phase,param):
    on_off_samples = {}
    on_off_samples["q_on"] = []
    on_off_samples["q_off"] = []
    on_off_samples["q_on_suspect"] = []
    on_off_samples["q_off_suspect"] = []
    i = 1 #index for Energy
    while ( i < len(ddE) ):
        #check for ON
        if (ddE[i] > 0 and ddE[i] >= treshold):
            if (i+1 < len(ddE)):
                if (ddE[i+1] > 0 and ddE[i+1] >= treshold):
                    on_off_samples["q_on_suspect"].append({"index": i,"time": data_dict['StringTime'][i+1],"Dtime": data_dict['DoubleTime'][i+1],"dE":dE[i],"ddE":ddE[i], "Diff Power Value": dP[i]})
                    i+=1
            on_off_samples["q_on"].append({"index": i, "time": data_dict['StringTime'][i + 1],"Dtime": data_dict['DoubleTime'][i+1], "dE": dE[i+1],"ddE": ddE[i], "Diff Power Value": dP[i]})
        # check for OFF
        elif (ddE[i] < 0 and abs(ddE[i]) >= treshold and (len(on_off_samples["q_on"]) > 0)):
            if (i+1 < len(ddE)):
                if(ddE[i+1] < 0 and abs(ddE[i+1]) >= treshold and (len(on_off_samples["q_on"]) > 0)):
                    on_off_samples["q_off_suspect"].append({"index": i,"time": data_dict['StringTime'][i+1],"Dtime": data_dict['DoubleTime'][i+1],"dE":dE[i],"ddE":ddE[i], "Diff Power Value": dP[i]})
                    if ( len(on_off_samples["q_on"]) >= len(on_off_samples["q_off"]) +2 ):
                        on_off_samples["q_off"].append({"index": i, "time": data_dict['StringTime'][i + 1],"Dtime": data_dict['DoubleTime'][i + 1],"dE": dE[i + 1],"ddE": ddE[i],"Diff Power Value": dP[i]})
                    i += 1
            on_off_samples["q_off"].append({"index": i, "time": data_dict['StringTime'][i + 1],"Dtime": data_dict['DoubleTime'][i+1], "dE": dE[i+1],"ddE": ddE[i], "Diff Power Value": dP[i]})
        i += 1

    # for testing E:
    sorted(on_off_samples, key=lambda x: x[0])
    print("The on value is ", on_off_samples["q_on"])
    print("The off value is ", on_off_samples["q_off"])
    print("The suspect on value is ", on_off_samples["q_on_suspect"])
    print("The suspect off value is ", on_off_samples["q_off_suspect"])

    plot_detected_ON_OFF(on_off_samples, param=param)
    PP_load_monitoring(on_off_samples=on_off_samples,dE=dE,phase=phase+1)

def plot_detected_ON_OFF(on_off_samples,param='dE'):
    ON_samples = on_off_samples["q_on"]
    ON_idxes = [x['index'] for x in ON_samples]
    ax = plt.gca()
    line = ax.lines[0]
    line.get_xdata()
    ON_time = line.get_xdata()[ON_idxes]
    ON_values = [x[f'{param}'] for x in ON_samples]
    ON_series = pd.Series(ON_values, index=ON_time)
    plt.scatter(ON_series.index, ON_series, color='lime')

    OFF_samples = on_off_samples["q_off"]
    OFF_idxes = [x['index'] for x in OFF_samples]
    OFF_time = line.get_xdata()[OFF_idxes]
    OFF_values = [x[f'{param}'] for x in OFF_samples]
    OFF_series = pd.Series(OFF_values, index=OFF_time)
    plt.scatter(OFF_series.index, OFF_series, color='red')
    plt.legend(['_nolegend_','ON','OFF']) # fixme
    plt.gca().get_lines()[0].set_color("black")

def PP_load_monitoring(on_off_samples,dE,phase):
    Loads = get_phase_loads(phase)
    for load in [l for l in Loads if Loads[l]["phase"] == phase]:
        # sort by priority
        on_idx = 0
        while (on_idx != len(on_off_samples["q_on"])):
            flag = 0
            #convert str to float
            on_off_samples["q_on"][on_idx]["Dtime"] = on_off_samples["q_on"][on_idx]["Dtime"].astype(np.float64)
            on_smpl_index = on_off_samples["q_on"][on_idx]["index"]
            on_time = on_off_samples["q_on"][on_idx]["Dtime"]
            for off_idx in range(len(on_off_samples["q_off"])):
                off_smpl_index = on_off_samples["q_off"][off_idx]["index"]
                if (on_smpl_index < off_smpl_index):
                    # convert str to float
                    on_off_samples["q_off"][off_idx]["Dtime"] = on_off_samples["q_off"][off_idx]["Dtime"].astype(np.float64)
                    off_time = on_off_samples["q_off"][off_idx]["Dtime"]
                    action_time = (off_time - on_time) / 1000.0
                    # we don't expect for device with action_time greater than 1300.
                    if (action_time > 2000):
                        break
                        print(action_time)
                    Emin = Loads[load]["Emin"]
                    Emax = Loads[load]["Emax"]
                    Energy_sum = np.sum(dE[on_smpl_index + 1:off_smpl_index + 2])
                    if (Emin <= Energy_sum and Emax >= Energy_sum):
                        print('on:', on_off_samples["q_on"][on_idx])
                        print('off:', on_off_samples["q_off"][off_idx])
                        print(Emin,Emax,Energy_sum, load)
                        del on_off_samples["q_on"][on_idx]
                        del on_off_samples["q_off"][off_idx]
                        flag = 1
                        break
            if flag == 0:
                on_idx += 1

def Subplots_ED_Vs_Ts(data):
    phase = 2
    Ts = [30,60,2*60]
    plt.figure()
    for i in range(len(Ts)):
        data_dict = update_data(data, Ts[i])
        plt.subplot(len(Ts),2,2*i+1)
        param = 'dE'
        if i==0:
            gen_plots(params=[param], data_dict=data_dict, Ts=Ts[i], phase=phase)
            xticks = plt.xticks()
        else:
            gen_plots(params=[param], data_dict=data_dict, Ts=Ts[i], phase=phase, xticks=xticks)
        #### FIFO CALC  ####
        treshold = 5.8
        on_off_fifo(data_dict=data_dict, phase=phase, treshold=treshold, param=param)
        plt.title(f'Ts = {Ts[i]}[sec]')

        plt.subplot(len(Ts), 2, 2*i+2)
        param = 'ddE'
        gen_plots(params=[param], data_dict=data_dict, Ts=Ts[i], phase=phase, xticks=xticks)
        on_off_fifo(data_dict=data_dict, phase=phase, treshold=treshold, param=param)
        plt.title(f'Ts = {Ts[i]}[sec]')

    plt.subplot_tool()
    plt.show()