import numpy as np
from Preparations import *
from Utilities import *
from Data import *


def remove_baseline(signal,thresh=1):
    baseline=0.16
    output = []
    Noise = []
    for i in range(len(signal)):
        if signal[i] < thresh:
            baseline = signal[i]
        output.append(signal[i] - baseline)
        Noise.append(baseline)
    # plt.figure()
    # plt.step(signal,'.-')
    # plt.step(Noise,'.-',color= 'red')
    # plt.grid()
    # plt.title("Power Noise Level")
    # plt.ylabel('Power [kW]')
    # plt.xlabel('Sample index')
    # plt.axhline(y=thresh, color='g', linestyle="--")
    # plt.legend(['Total Power','Noise Level','threshold'])
    return output ,Noise

def get_consecutive_result(vec, prev_vec, penalty_4_consecutive,phase):
    if phase == 1:
        if prev_vec == ([0,0,1]):
            return np.sum(np.multiply(vec, penalty_4_consecutive))
    elif phase == 2:
        if prev_vec == ([0,0,1,0,0,0,0,0] or [0,0,0,1,0,0,0,0] or [0,0,0,0,1,0,0,0] or [0,0,0,0,0,1,0,0]):
            return np.sum(np.multiply(vec, penalty_4_consecutive))
    if vec == prev_vec:
        return np.sum(np.multiply(vec, penalty_4_consecutive))
    return 0

def get_ddE_vec_result(vec,prev_vec,ddE_sample):
    penalty = abs(ddE_sample)+50
    no_Change_thresh = 6
    thresh = no_Change_thresh
    if ddE_sample > thresh: #some new load is turned on.
        if np.sum(abs(np.subtract(vec,prev_vec))) >=1:
            return 0 #no penalty.
        else:
            return penalty

    elif abs(ddE_sample) < no_Change_thresh:
        if np.sum(np.abs(np.subtract(vec, prev_vec))) != 0:
            return penalty

    elif ddE_sample < -thresh:
        if np.sum((np.subtract(vec,prev_vec))) >= 0:
            return penalty
    return 0

def calc_penalty_vec(vec,prev_vec, P_sample,P_N_sample, idx_2_P_av,dE_sample,ddE_sample,dt_sample, idx_2_T_av,phase, penalty_4_consecutive):
    penalty_vec = [0, 0, 0, 0]
    penalty_vec[0] = get_vec_P_result(vec, P_sample, P_Noise=P_N_sample, idx_2_P_av=idx_2_P_av)
    penalty_vec[1] = get_vec_dE_result(vec=vec, dE_sample=dE_sample, dt_sample=dt_sample,
                                 idx_2_P_av=idx_2_P_av,
                                 P_noise_sample=P_N_sample, idx_2_T_av=idx_2_T_av)
    penalty_vec[2] = get_ddE_vec_result(vec, prev_vec, ddE_sample)
    penalty_vec[3] = get_consecutive_result(vec, prev_vec, penalty_4_consecutive, phase)

    return penalty_vec

def get_weights(P_sample,P_N_sample,phase,ddE_sample):
    if phase ==1:
        Weights = [50, 1, 0.5, 50]
        if P_sample - P_N_sample == 0:
            Weights[0] = 5
        if abs(ddE_sample) < 5: #Power is relaible during mid activity (No load changes)
            Weights[0] = 1000
    elif phase == 2:
        Weights = [150, 1, 1, 100]
        if P_sample - P_N_sample == 0:
            Weights[0]= 15
    return Weights

def RT_detection(data_dict,phase):
    power = list(map(float, data_dict[f'kW L{phase}']))
    E_diffs = list(map(float, data_dict[f'dE{phase}']))
    ddE = list(np.diff(E_diffs))
    ddE.insert(0,0)
    ddE[0:3] = [0,0,0] #init
    T_diffs = get_time_diffs(data_dict)

    noiseless_power, P_noise = remove_baseline(power, thresh=0.5)
    Loads_vectors, idx_2_load, idx_2_P_av, idx_2_T_av,penalty_4_consecutive\
        = get_loads_options_in_vectors(phase)
    Results = []

    for i in range(len(noiseless_power)):
        vec_results = []
        for vec in Loads_vectors:
            if i==0:
                prev_vec = Loads_vectors[0]
            else:
                prev_vec = Results[i-1]
            P_sample = power[i]
            P_N_sample = P_noise[i]
            dE_sample = E_diffs[i]
            ddE_sample = ddE[i]
            dt_sample = T_diffs[i]

            penalty_vec = calc_penalty_vec(vec, prev_vec, P_sample, P_N_sample, idx_2_P_av, dE_sample, ddE_sample, dt_sample, idx_2_T_av,
                       phase, penalty_4_consecutive)
            Weights =get_weights(P_sample=power[i], P_N_sample=P_noise[i], phase=phase, ddE_sample=ddE_sample)
            wighted_penalty_vec = np.multiply(penalty_vec, Weights)
            vec_result = np.sum(wighted_penalty_vec)
            vec_results.append(vec_result)
        winning_vec = Loads_vectors[np.argmin(vec_results)]
        Results.append(winning_vec)
    Result = np.array(Results)
    return Result

#showing how use of ddE helps!
def RT_detection_by_dE(Ts,data_dict,phase,E_threshold):
    power = list(map(float, data_dict[f'kW L{phase}']))
    E_diffs = list(map(float, data_dict[f'dE{phase}']))
    T_diffs = get_time_diffs(data_dict)
    plt.figure()
    plt.plot(range(len(E_diffs)), E_diffs, 'o')
    plt.grid()
    noiseless_power, P_noise = remove_baseline(power, thresh=0.5)
    Loads_vectors, idx_2_load, idx_2_P_av, idx_2_T_av = get_loads_options_in_vectors(phase)
    Result = []
    for i in range(len(noiseless_power)):
        min = 10**6
        winning_vec = Loads_vectors[0]
        print("-----------")
        winning_vec = Loads_vectors[0]
        if noiseless_power[i] ==0:
            for vec in Loads_vectors:
                vec_dE_result = get_vec_dE_result(vec=vec, dE_sample=E_diffs[i], dt_sample=T_diffs[i],idx_2_P_av=idx_2_P_av,P_noise_sample= P_noise[i], idx_2_T_av=idx_2_T_av)
                print(vec_dE_result)
                if vec_dE_result < min:
                    min = vec_dE_result
                    winning_vec = vec
        Result.append(winning_vec)
    Result = np.array(Result)
    plt.figure()
    plt.subplot(3, 1, 1)
    plt.step(E_diffs, '.-')
    plt.subplot(3,1,2)
    for i in range(len(Result[0])):
        plt.step(range(len(Result[:,i])), Result[:,i] ,'.-')
    plt.legend(idx_2_load)
    plt.subplot(3, 1, 3)
    ddE = list(np.diff(E_diffs))
    ddE.insert(0,0)
    intr_a = np.multiply(ddE, [1 if x == 0 else 0 for x in noiseless_power])
    plt.plot(intr_a ,'o')
    return Result

def get_vec_dE_result(vec, dE_sample,dt_sample,P_noise_sample, idx_2_P_av, idx_2_T_av):
    vec_p = np.multiply(vec, idx_2_P_av)
    vec_activity_time = [min(x,dt_sample) for x in idx_2_T_av]
    vec_dE = np.sum(np.multiply(vec_p, vec_activity_time))
    total_dE = vec_dE + P_noise_sample*dt_sample
    output = abs(dE_sample - total_dE)
    return output

#P_sample including noise
def get_vec_P_result(vec, P_sample,P_Noise, idx_2_P_av):
    vec_P = np.sum(np.multiply(vec,idx_2_P_av))
    output = abs(P_sample - (vec_P + P_Noise))
    return output

#works_perfect for Ts= 2*60, stream_1, Phase1
def EXAMPLE_get_ddE_vec_penalty(vec,prev_vec,ddE_sample,Ts):
    thresh = 8 #10*(Ts/60)
    penalty = 10**3
    no_Change_thresh = 6
    if ddE_sample > thresh: #some new load is turned on.
        if np.sum(abs(np.subtract(vec,prev_vec))) >=1:
            return 0
        else:
            return penalty
    elif abs(ddE_sample) < no_Change_thresh:
        if np.sum(np.abs(np.subtract(vec, prev_vec))) != 0:
            return penalty

    elif ddE_sample < -thresh:
        if np.sum((np.subtract(vec,prev_vec))) >= 0:
            return penalty
    return 0
