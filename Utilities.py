import matplotlib.pyplot as plt
import pandas as pd
import dateutil
import matplotlib.dates as dates
import numpy as np
from datetime import datetime

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR



def get_param_values(param, data_dict, Ts):
    if (param == "P"):
        data = [data_dict['kW L1'], data_dict['kW L2'], data_dict['kW L3']]
        suptitle = ("Power(t)")
        title = 'P'
        units = '[kW]'
    elif (param == "E"):
        data = [data_dict['E1'], data_dict['E2'], data_dict['E3']]
        suptitle = ("Energy(t)")
        title = 'E'
        if (Ts == 1):
            units = '[Kw/sec]'
        else:
            if Ts == 60:
                units = f'[Kw/min]'
            else:
                units = f'[Kw/{int(Ts / 60)}min]'
    elif (param == "dE"):
        columns = ["StringTime", "dE1", "dE2", "dE3"]
        df = pd.read_csv("data.csv", usecols=columns)
        data = [data_dict['dE1'], data_dict['dE2'], data_dict['dE3']]
        suptitle = ("Energy Dose(t)")
        title = '\u0394Energy'
        if (Ts == 1):
            units = '[Kw/sec]'
        else:
            if Ts == 60:
                units = f'[Kw/min]'
            else:
                units = f'[Kw/{int(Ts / 60)}min]'
    elif (param == "ddE"):
        columns = ["StringTime", "dE1", "dE2", "dE3"]
        df = pd.read_csv("data.csv", usecols=columns)
        data = [data_dict['dE1'], data_dict['dE2'], data_dict['dE3']]
        suptitle = ("Energy Acceleration(t)")
        title = '\u0394\u0394E'
        if (Ts == 1):
            units = '[Kw/sec]'
        else:
            if Ts == 60:
                units = f'[Kw/min]'
            else:
                units = f'[Kw/{int(Ts / 60)}min]'

    elif (param == "dP"):
        columns = ["StringTime", "kW L1", "kW L2", "kW L3"]
        df = pd.read_csv("data.csv", usecols=columns)
        data = [data_dict['kW L1'], data_dict['kW L2'], data_dict['kW L3']]
        suptitle = ("\u0394Power(t)")
        title = '\u0394P'
        units = '[Kw]'
    return data,suptitle, title, units


def plot_param(param,data_dict,Ts,phase, xticks=''):
    data, suptitle, title, units = get_param_values(param, data_dict, Ts)
    if (Ts>=30):
        if(Ts %60 == 0):
            s_Ts= '{}[min]'.format(int(Ts/60))
        else:
            s_Ts = '{}[min]'.format(Ts / 60)
    else:
        s_Ts = '{}[sec]'.format(int(Ts))
    dfs = [list(map(float, data[i])) for i in range(len(data))]
    if param == "dP" or param == "ddE" :
        dfs = [np.diff(dfs[i]) for i in range(len(dfs))]

    plt.title(f'{suptitle}')
    plt.ylabel(f'{title} {units}')
    plt.grid()

    #---Time---#
    time = data_dict['StringTime']
    # time= df.StringTime
    time = [time[i][10:18] for i in range(len(time))]   # keep the '%H:%M:%S' only.
    time = [dateutil.parser.parse(s) for s in time]
    if param == "dP" or param == "ddE":
        time = time[1:]
    ############
    for i in range(3):
        if phase != "All":
            if i != phase - 1:
                continue
                plt.plot(2)
        else:
            plt.subplot(3, 1, i+1)

        if len(time) != len(dfs[i]):
            print("")
        if (Ts == 1):
            plt.step(time, dfs[i], '.-', color="black",label='Original Samples')  # 'step' is the zero order interpolation plot function.
        else:
            # plt.step(time, dfs[i], '.-', color="black", label='Diluted Samples')
            plt.step(time, dfs[i], '.-', label='Diluted Samples')
        plt.legend([f'Ts= {s_Ts}'], loc='upper right')
        plt.xlabel("t [h:m]")
        # plt.ylabel("{}".format(units))
        if xticks=='':
            plt.xticks(time[0:len(time):max(int(len(time)/8),1)])  # how many x values to display
        else:
            plt.xticks(xticks[0],xticks[1])  # how many x values to display
        plt.gcf()
        myFmt = dates.DateFormatter('%H:%M')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.tight_layout()

def gen_plots(params, data_dict, phase, Ts=1, xticks=''):
    for x in params:
        if len(params)>1:
            plt.figure(figsize=(7, 4))
        plot_param(param=x,data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)


###-Summary table for monitoring loads-###
def printTable(myDict, colList=None):
    if not colList:
        colList = list(myDict[0].keys() if myDict else [])
    myList = [colList] # 1st row = header
    for item in myDict:
        myList.append([str(item[col] or '') for col in colList])
    #maximum size of the col for each element
    colSize = [max(map(len,col)) for col in zip(*myList)]
    #insert separating line before every line, and extra one for ending.
    for i in  range(0, len(myList)+1)[::-1]:
         myList.insert(i, ['-' * i for i in colSize])
    #two format for each content line and each separating line
    formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
    formatSep = '-+-'.join(["{{:<{}}}".format(i) for i in colSize])
    for item in myList:
        if item[0][0] == '-':
            print(formatSep.format(*item))
        else:
            print(formatStr.format(*item))



def plot_with_time_as_x(data, time,label, color='', plot_type='step' ):
    time = [time[i][10:18] for i in range(len(time))]  # keep the '%H:%M:%S' only.
    time = [dateutil.parser.parse(s) for s in time]
    if plot_type == 'step':
        if color== '':
            plt.step(time, data, '.-',zorder=1,label=label)
        else:
            plt.step(time, data, '.-',label=label, color=color,zorder=1)
        myFmt = dates.DateFormatter('%H:%M')
        plt.gca().xaxis.set_major_formatter(myFmt)

    else:
        plt.scatter(time, data, color='black', zorder=2,label=label)


def plot_energy_showing_missing_power():
    #####-ORIGINAL DATA-#####
    data = load_data(path, file_name)
    params = ['P']
    phase = 2
    high_freq_data_dict = update_data(data)
    plt.figure(figsize=(5, 4))
    plt.subplot(3, 1, 1)

    # gen_plots(params=params, data_dict=high_freq_data_dict, phase=phase)

    xticks = plt.xticks()
    time_for_one_sec = high_freq_data_dict['StringTime']
    #####-Diluted Data-######
    Ts = 1*60   # [sec]
    data_dict = update_data(data, Ts)
    plt.subplot(3, 1, 2)
    params = ['P']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    plt.subplot(3, 1, 3)
    params = ['dE']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    #####
    plt.show()

def plot_E_dE_onesec():
    #####-ORIGINAL DATA-#####
    data = load_data(path, file_name)
    high_freq_data_dict = update_data(data)
    plt.figure(figsize=(7, 4))
    phase = 2
    # plt.subplot(2, 1, 1)
    params = ['E']
    gen_plots(params=params, data_dict=high_freq_data_dict, phase=phase)
    plt.gca().get_lines()[0].set_color("blue")
    plt.legend(['Ts = 1sec'])

    xticks = plt.xticks()
    # plt.subplot(2, 1, 2)
    plt.figure(figsize=(7, 4))
    params = ['dE']
    gen_plots(params=params, data_dict=high_freq_data_dict,phase=phase, xticks=xticks)
    plt.gca().get_lines()[0].set_color("blue")
    plt.legend(['Ts = 1sec'])
    #####
    plt.show()

def plot_P_1sec():
    #####-ORIGINAL DATA-#####
    data = load_data(path, file_name)
    high_freq_data_dict = update_data(data)
    plt.figure(figsize=(7, 4))
    phase = 2
    # plt.subplot(2, 1, 1)
    params = ['P', 'dE']
    gen_plots(params=params, data_dict=high_freq_data_dict, phase=phase)
    plt.gca().get_lines()[0].set_color("blue")
    plt.legend(['Ts = 1sec'])
    plt.show()

def E_subplots(param):
    #####-ORIGINAL DATA-#####
    data = load_data(path, file_name)
    high_freq_data_dict = update_data(data)
    plt.figure(figsize=(7, 4))
    phase = 2
    colors = ['b','green','red','c','orange']
    T= [1,3,5]
    for i in range(3):
        Ts = T[i]*60
        data_dict = update_data(data, Ts)
        plt.subplot(3, 1, i+1)
        params = [f'{param}']
        if i == 0:
            gen_plots(params=params, data_dict=high_freq_data_dict,Ts = Ts, phase=phase)
            xticks = plt.xticks()
        else:
            gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
        plt.gca().get_lines()[0].set_color(colors[i])
        plt.legend([f'Ts = {T[i]}min'])
    # plt.tight_layout()
    plt.show()

def run_old_algo():
    data = load_data(path, file_name)
    Subplots_ED_Vs_Ts(data=data)
    ####-Original Data-######
    # params = ['P']
    phase = 2
    plt.figure()
    # gen_plots(params, data, phase=phase)
    # #####-Diluted Data-######
    params = ['ddE']

    Ts = 15  # [sec]
    data_dict = update_data(data, Ts)
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase)

    #### FIFO CALC  ####

    # params = 'ddE'
    # if (params == 'dP'):
    #    treshold = 0.6
    # elif (params == 'ddE'):
    treshold = 5.8 #thresh for ddE

    param = params[0]
    # th 0.7 is good for stream_1 & stream_2
    on_off_fifo(data_dict=data_dict, phase=phase, treshold=treshold, param=param)
    plt.show()

def run_semi_RT_detection():
    start = timeit.default_timer()
    #####-ORIGINAL DATA-#####
    data = load_data(path, file_name)
    params = ['P']

    high_freq_data_dict = update_data(data)
    plt.figure(figsize=(7, 4))
    #
    plt.subplot(4, 1, 1)
    #
    gen_plots(params=params, data_dict=high_freq_data_dict, phase=phase)
    xticks = plt.xticks()
    # # labels  = [item.get_text() for item in ax1.get_xticklabels()]
    time_for_one_sec = high_freq_data_dict['StringTime']  # fixme: tiem for one sec
    # #####-Diluted Data-######
    #
    # # dilution rate: 1 - 5 minutes
    Ts = 2*60   # [sec]
    data_dict = update_data(data, Ts)

    # get_quasi_P(data_dict,phase,Ts)
    plt.subplot(4, 1, 2)
    params = ['P']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    plt.subplot(4, 1, 3)
    params = ['dE']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    plt.subplot(4, 1, 4)
    params = ['ddE']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    #
    # #####
    #
    # plt.show()
    plt.figure()
    P_threshold, E_threshold = get_thresholds(phase=phase, Ts=Ts)  # fixme: move to right place
    # plt.figure()
    found_loads_list, results = get_detected_loads(Ts, data_dict, phase, E_threshold)
    # load_monitoring(Ts=Ts,data_dict=data_dict,phase=phase, E_threshold=E_threshold)
    gen_plots(params=['P'], data_dict=high_freq_data_dict, phase=phase)
    detection_summary(file_name=file_name, time_for_one_sec=time_for_one_sec, Ts=Ts, data_dict=data_dict,
                      found_loads_list=found_loads_list, results=results, phase=phase)
    ####
    stop = timeit.default_timer()
    print('Time: ', stop - start)

    plt.show()

def get_padded_results(Result,high_freq_data_dict,diluted_data_dict):
    P_orig = high_freq_data_dict[f'kW L{phase}']
    T_orig = high_freq_data_dict["StringTime"]
    T_diluted = diluted_data_dict["StringTime"]
    res_i = 0
    padded_res = []
    for i in range(len(T_orig)):
        if T_orig[i] == T_diluted[res_i]:
            padded_res.append(Result[res_i])
            res_i += 1
        else:
            if res_i !=0: #and res_i != len(T_diluted)-1:
                # if Result[i] == Result[i-1]:
                padded_res.append(Result[res_i-1]*float(P_orig[i]))
            else:
                padded_res.append(Result[res_i]*float(P_orig[i]))
    padded_res = np.array(padded_res)
    return padded_res

def plot_power_penalty_importance():
    data = load_data(path, file_name)

    high_freq_data_dict = update_data(data)
    plt.figure(figsize=(7, 4))
    plt.subplot(3, 1, 1)
    params = ['P']
    gen_plots(params=params, data_dict=high_freq_data_dict, phase=phase)
    plt.xlim([19149.301166550926, 19149.323000578704])

    xticks = plt.xticks()

    data_dict = update_data(data, Ts)

    plt.subplot(3, 1, 2)
    params = ['P']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    plt.gca().get_lines()[0].set_color("blue")
    plt.legend([f'Ts = {int(Ts / 60)}[min]'])
    plt.xlim([19149.301166550926, 19149.323000578704])

    plt.subplot(3, 1, 3)
    params = ['ddE']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    plt.gca().get_lines()[0].set_color("red")
    plt.legend([f'Ts = {int(Ts / 60)}[min]'])
    plt.xlim([19149.301166550926, 19149.323000578704])
    plt.subplot_tool()
    plt.show()

def plot_dE_penalty_importance():
    data = load_data(path, file_name)

    high_freq_data_dict = update_data(data)
    plt.figure(figsize=(7, 4))
    plt.subplot(2, 1, 1)
    params = ['P']
    gen_plots(params=params, data_dict=high_freq_data_dict, phase=phase)
    plt.xlim([19149.355566550926, 19149.378000578704])
    xticks = plt.xticks()

    data_dict = update_data(data, Ts)

    plt.subplot(2, 1, 2)
    params = ['dE']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    plt.gca().get_lines()[0].set_color("green")
    plt.legend([f'Ts = {int(Ts / 60)}[min]'])
    plt.xlim([19149.355566550926, 19149.378000578704])
    plt.subplot_tool()
    plt.show()

