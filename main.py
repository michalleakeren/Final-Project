import matplotlib.pyplot as plt
import timeit
from Data import *
from Utilities import *
#from Semi_RT_Detection.py import *
from RT_Detection import *
#from Post_process_detection import *
from Preparations import *
from Results import *
import time

###-USER FOLDER PATH (CHANGE TO FILE'S DIR BEFORE RUNNING)-###

path = 'C:\\Users\micha\Desktop\Michal&Aviran_PROJECT' # insert Michal&Aviran_PROJECT folder path


###-SELECT A FILE-###
file_names = ['stream_1', '240921_gener_1']

file_name = '240921_gener_1'
phase = 2
Ts = 1*60 #[sec]


def main():
    #####-ORIGINAL DATA-#####
    high_freq_data = load_data(path, file_name)
    high_freq_data_dict = update_data(high_freq_data, file_name)
    plt.figure(figsize=(7, 4))
    plt.subplot(4, 1, 1)
    params = ['P']
    gen_plots(params=params, data_dict=high_freq_data_dict, phase=phase)
    xticks = plt.xticks()

    #####-DILUTED DATA-#####
    data_dict = update_data(high_freq_data,file_name, Ts)
    plt.subplot(4, 1, 2)
    params = ['P']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    plt.gca().get_lines()[0].set_color("blue")
    plt.legend([f'Ts = {int(Ts / 60)}[min]'])
    plt.subplot(4, 1, 3)
    params = ['dE']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts,phase=phase, xticks=xticks)
    plt.gca().get_lines()[0].set_color("green")
    plt.legend([f'Ts = {int(Ts / 60)}[min]'])
    plt.subplot(4, 1, 4)
    params = ['ddE']
    gen_plots(params=params, data_dict=data_dict, Ts=Ts, phase=phase, xticks=xticks)
    plt.gca().get_lines()[0].set_color("red")
    plt.legend([f'Ts = {int(Ts/60)}[min]'])
    plt.subplot_tool()


    Result = RT_detection(data_dict, phase)
    if (file_name == '240921_gener_1' and phase == 2 and Ts ==1*60) or (file_name == 'stream_1' and phase == 1) :
        GT_Result = get_GT_result(file_name,Result,Ts)
        plot_results_with_GT(Result, GT_Result, high_freq_data_dict, diluted_data_dict=data_dict, phase=phase, Ts=Ts)
    else:
        plot_results(Result, high_freq_data_dict, diluted_data_dict=data_dict, phase=phase)
    plt.show()

main()



