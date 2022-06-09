import csv, pyodbc
import numpy as np
import pandas as pd
from datetime import datetime

#Conver MDB file to CSV
def gen_CSV(MDB):
    # connect to db
    con = pyodbc.connect(
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+MDB+';')
    cur = con.cursor()
    colDesc = list(cur.columns())
    table_names=[]
    for b in colDesc:
        if (b[2] not in table_names):
            table_names.append(b[2])
    c= table_names[-1]
    SQL = f'SELECT StringTime,DoubleTime, [kW L1], [kW L2], [kW L3] FROM [{c}]'
    cur.execute(SQL)
    rows = []
    headers = ['StringTime','DoubleTime', 'kW L1', 'kW L2', 'kW L3']
    rows.append(headers)   #headers
    for row in cur.fetchall():
        rows.append(row)
    del rows[1]                                         #remove first row
    with open('data.csv', 'w', newline='') as fou:
        csv_writer = csv.writer(fou)  # default field-delimiter is ","
        csv_writer.writerows(rows)
    cur.close()
    con.close()

def calc_phase_energy(phase):
    df = pd.read_csv("data.csv")
    E= []
    sum = 0
    for x in range(df.shape[0]):
        sum = sum + df[f'kW L{phase}'][x]
        E.append(sum)
    return(E)

def calc_energy():
    E= []
    for i in range(1,4):
        e = calc_phase_energy(i)
        E.append(e)
    return(np.array(E))

def load_data(path,file_name): #also adds the Energy columns.
    gen_CSV(r'{}\{}.mdb'.format(path,file_name))
    with open('data.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile))
    data = np.array(data)
    # add the energy columns
    E = np.transpose(calc_energy())
    E_titles= np.array(['E1','E2','E3'])
    E_tot= np.vstack( (E_titles , E ))
    data= np.hstack((data,E_tot))
    return(data)

def calc_energy_diffs(data):
    E = data[1:, [-3,-2,-1]]
    E = E.astype(float)
    E = np.transpose(E)
    deltas= np.diff(E)
    E[:,1:E.shape[1]] =deltas
    E[:, 0] = 0
    return(E)

def update_data(data,file_name,Ts=1):   #adds the Energy diff between the samples & dilutes the samples
    if Ts != 1:
        data=dilute_samples(data, Ts)
    data = np.array(data)
    dE = np.transpose(calc_energy_diffs(data))
    if file_name == 'stream_1':
        dE= np.multiply(dE,2) #compensate for sampling mismatch in 'stream_1' file.
    dE_title = np.array(['dE1', 'dE2', 'dE3'])
    dE_tot = np.vstack((dE_title, dE))
    new_data = np.hstack((data, dE_tot))
    with open('data.csv', 'w',newline='') as f:
        write = csv.writer(f)
        write.writerows(new_data)
    #Convert the CSV to dictionary:
    data_dict = {new_data[0][idx]: [new_data[ele][idx] for ele in range(1, len(new_data))] for idx in range(len(new_data[0]))}
    return data_dict

def dilute_samples(data,Ts):
    #Ts[sec]
    data_array = np.array(data)
    diluted_data = []
    diluted_data.insert(0, data[0])

    StringTime = [x.split()[1] for x in data_array[1:,0]]
    Time = [datetime.strptime(x, '%H:%M:%S.%f') for x in StringTime]
    idxs =[1]
    i = 1
    diluted_data.append(data[1])
    while i< len(Time):
        curr_time = Time[i]
        time_gaps = [float(f'{(x- curr_time).seconds}.{(x- curr_time).microseconds}') for x in Time]

        i = np.argmin(abs(np.subtract(time_gaps, Ts))) +1
        if i != len(Time)+1:
            idxs.append(i)
            diluted_data.append(data[i])
    return diluted_data


def get_time_diffs(data_dict):
    StringTime = [x.split()[1] for x in data_dict['StringTime']]
    time = [datetime.strptime(x, '%H:%M:%S.%f') for x in StringTime]
    dTime = [float(f'{x.seconds}.{x.microseconds}') for x in np.diff(time)]
    dTime.insert(0,0)
    return dTime