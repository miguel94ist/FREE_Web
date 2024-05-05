import pandas as pd
from scipy.signal import find_peaks
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import curve_fit
import math
import json
import random as rd 
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='/home/elab/elab-dev-lti/FREE_quizes/quizes_code/langmuir.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')
logger.debug("test")

def exexecution_parameters_random_langmuir(*args):
    
    gas_label = ["Helium (He)","Nitrogen (N)","Argon (Ar)"]
    gas_type = [1,2,3]     
    index_gas = rd.randint(0, len(gas_type)-1)


    injection = [35, 50, 80, 100, 120, 150]
    index_injection = rd.randint(0, len(injection)-1)

    
    return [{'name': 'pressure', 
             'description': 'Gas Injection Time [ms]',
              'value': injection[index_injection]},
             {'name': 'gas_selector',
              'description': 'Gas Selection',
              'value': gas_type[index_gas],
              'label': gas_label[index_gas]}
            ]



def configured_execution(JSON_config):
     #JSON_config["f_start"] =  3400
     #JSON_config["f_end"] =  3700
     #JSON_config["f_step"] = 0.4
     #JSON_config["n_iteration"] = 5
     #JSON_config["back_pressure"] = 25
     #JSON_config["pressure"] = 20
     #JSON_config["gas_selector"] = 3
     #JSON_config["magnetic_field"] = 0
     #JSON_config["discharge"] = 1

     #return JSON_config 
      return JSON_config

def constanst(working_gas):
    error = 15 #%
    elementary_charge = -1.6e-19
    me=9.1093837e-31
    radius = 1e-4
    length = 1e-2
    atomic_mass_unit = 1.66e-27
    boltzmann = 1.38e-23
    atom = 1
    t_k = 11604.5  # temperature conversion between eV and K
    epsilon = 8.85e-12

    if working_gas == 1:
        atom = 4 
    elif working_gas == 2:
        atom = 14
    elif working_gas == 3:
        atom = 39.95

    return error, elementary_charge, me, radius, length, atomic_mass_unit, boltzmann, atom, t_k, epsilon, atom


def transition_guess(y_v, x_v):
    y_value = np.array(y_v)
    x_value = np.array(x_v)
    # Fit a linear function to the data
    cut_data = 0
    initial_fit = 20
    no_check = 10
    data_error = y_value[cut_data:initial_fit].std() # Standard Deviation of the dataset
    # data_error = 0
    slope_fit, intercept_fit = np.polyfit(x_value[cut_data:initial_fit], y_value[cut_data:initial_fit], 1)
    for i in range(initial_fit, len(y_value)-cut_data):
        j = 0
        if y_value[i] < slope_fit * x_value[i] + intercept_fit + data_error:
            slope_fit, intercept_fit = np.polyfit(x_value[cut_data:i], y_value[cut_data:i], 1)
            pass
        else:
            for j in range(1, no_check):
                if y_value[i+j] < slope_fit * x_value[i+j] + intercept_fit + data_error:
                    break
                else:
                    pass
        if j == no_check - 1:
            idx_tr = i
            return x_value[idx_tr]
    return None

def objective_function(x,temp, i_sat, v_float,g, i_e, v_p, b):
    def newfunction(x):        
        return np.piecewise(x, [x <= v_p, x > v_p],\
               [lambda x: (i_sat * (x - v_float) + b + g*(np.exp((x - v_float) / temp) - 1)),\
                lambda x: (i_e * (x - v_p) + i_sat * (v_p - v_float) + b + g*(np.exp((v_p - v_float) / temp) - 1))])
    
    
    y =  np.piecewise(x, [x < v_float, x >= v_float], [lambda x: (i_sat * (x - v_float) + b),lambda x: newfunction(x)])    
    return y

def fit_lang(voltage,current):
    try:
        #trans = transition_guess(current,voltage)
        #if trans  == None:
        #   trans =0
        x_volt = voltage
        # Initial guess for the variables
        
        #  T_ev , a , v_float , g , i_e , v_p , b
        
        initial_guess = [10.97780527,0.121274678,-1,0,2.619943203,37.98112605,-16.19512549]
    
        fit_min=0
        fit_max=-1

        #excel_result = [10.97780527,0.121274678,0.371662125,0,2.619943203,37.98112605,-16.19512549]
        
        bounds_mine =  ([   0,      0,    -50,   -10,   0,   -20,   -50],\
                        [12.5,     15,  -0.01,    10,  10,    40,    -5])
        result, covariance = curve_fit(objective_function, voltage[fit_min:fit_max], current[fit_min:fit_max],\
                                   p0 = initial_guess,\
                                   bounds = bounds_mine)

        result_i = result

        print(result)

        fit_y = objective_function(x_volt,result[0],result[1],result[2],result[3],result[4],result[5],result[6])
        # print(fit_y)

        #plt.plot(result[2],objective_function(result[2],result[0],result[1],result[2],result[3],result[4],result[5],result[6]),".g",markersize=15,label="VFloat")
        #plt.plot(result[-2],objective_function(result[-2],result[0],result[1],result[2],result[3],result[4],result[5],result[6]),".",markersize=15,color="orange",label="Vp")
              
        return True,result[0],result[1],result[2],result[3],result[4],result[5],result[6]
    except:
    #else:
        return False,0,0,0,0,0,0,0

def GetCurrentVolts(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):

    skip_peaks  = 5

    print(current_question)
    print(user_answer)
    print(decimal_places) 
    print(current_quiz)
    print(execution)
    print(len(execution.result_set.all()))

    print(execution.config)    
    print(execution.config["gas_selector"])
    dados = execution.result_set.all()
    dados_rev = dados[::-1]
    #print(dados_rev[0].value)
    dados_final = []
    voltage = []
    voltage_not_working = -0.07482399999999245
    
    current = []
    for i in range(len(dados_rev)-1):
        if dados_rev[i].result_type!= "f":
            #print(len(dados_rev[i].value))
            for ll in range(len(dados_rev[i].value)):
                if abs(float(dados_rev[i].value[ll]["adc_value1"])-voltage_not_working) > 0.1 or float(dados_rev[i].value[ll]["adc_value3"]) <0.01:
                    voltage.append(float(dados_rev[i].value[ll]["adc_value1"]))
                    current.append(float(dados_rev[i].value[ll]["adc_value2"]))
                dados_final.append(dados_rev[i].value[ll])
                #print(dados_rev[i].value[ll])
                #print(type(dados_rev[i].value[ll]))
    #dados_final = json.loads(dados_final)
    #print(json.dumps(dados_final, indent=4))
    #print(len(dados_final))    
    peaks_min, _ = find_peaks(np.array(voltage), prominence=2)
    peaks_max, _ = find_peaks(-1*(np.array(voltage)), prominence=2)

    voltage_d = []
    current_d = []

    voltage_i = []
    current_i = []
    if len(peaks_max) < len(peaks_min):
        max_size = len(peaks_max)
    else:
        max_size = len(peaks_min)
    for i in range(skip_peaks,max_size):
        #print(i)
        if peaks_max[i] < peaks_min[i]:
            voltage_i.extend(voltage[peaks_max[i]:peaks_min[i]])
            current_i.extend(current[peaks_max[i]:peaks_min[i]])
            voltage_d.extend(voltage[peaks_min[i-1]:peaks_max[i]])
            current_d.extend(current[peaks_min[i-1]:peaks_max[i]])

        else:
            
            voltage_d.extend(voltage[peaks_min[i]:peaks_max[i]])
            current_d.extend(current[peaks_min[i]:peaks_max[i]])
            voltage_i.extend(voltage[peaks_max[i-1]:peaks_min[i]])
            current_i.extend(current[peaks_max[i-1]:peaks_min[i]])

    #print(current_i)
    if peaks_max[-1] < peaks_min[-1] and peaks_min[-1] < len(voltage):
        voltage_d.extend(voltage[peaks_min[-1]:-1])
        current_d.extend(current[peaks_min[-1]:-1])

    elif peaks_max[-1] > peaks_min[-1] and peaks_max[-1] < len(voltage):
        voltage_i.extend(voltage[peaks_max[-1]:-1])
        current_i.extend(current[peaks_max[-1]:-1])
    
    #print(voltage_d)  
    #print(current_d)
    #print(voltage_i)  
    #print(current_i) 
 

    df_i = pd.DataFrame(list(zip(voltage_i, current_i)),columns =['volt', 'current'])
    df_i = df_i.sort_values('volt', ascending=True)
    
    df_d = pd.DataFrame(list(zip(voltage_d, current_d)),columns =['volt', 'current'])
    df_d = df_d.sort_values('volt', ascending=True)

    v_i = df_i['volt'].values  
    c_i = df_i['current'].values
    v_d = df_d['volt'].values
    c_d = df_d['current'].values   

    return v_i,c_i,v_d,c_d


def Langmuir_temp(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):

    v_i,c_i,v_d,c_d = GetCurrentVolts(current_question, user_answer, decimal_places, current_quiz, execution, all_executions)
    
    error, elementary_charge, me, radius, length, atomic_mass_unit, boltzmann, atom, t_k, epsilon, atom = constanst(execution.config["gas_selector"])

    Fit_state_i, T_ev_i, a_i, v_float_i, g_i, i_e_i, v_p_i, b_i = fit_lang(v_i,c_i)
    Fit_state_d, T_ev_d, a_d, v_float_d, g_d, i_e_d, v_p_d, b_d = fit_lang(v_d,c_d)
    
    if Fit_state_i == True and Fit_state_d == True:
        if T_ev_i < T_ev_d:
             T_ev = T_ev_i 
        else:
             T_ev = T_ev_d
        if abs((T_ev - float(user_answer["T_plasma"]))/T_ev) * 100 < error:
             logger.debug("You are Correct!! Correct response: "+str(T_ev)+" eV")
             return True
        else:
             logger.debug("Incorrect... Correct response: "+str(T_ev)+" eV")
             return False

    elif Fit_state_i == True:
         logger.debug("problem with the Fit of d")
         return False
    elif Fit_state_d == True:
         logger.debug("problem with the Fit of i")
         return False
    else:
         logger.debug("problem with the Fits")
         return False



def Langmuir_i_sat(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):

    v_i,c_i,v_d,c_d = GetCurrentVolts(current_question, user_answer, decimal_places, current_quiz, execution, all_executions)

    error, elementary_charge, me, radius, length, atomic_mass_unit, boltzmann, atom, t_k, epsilon, atom = constanst(execution.config["gas_selector"])
    
    Fit_state_i, T_ev_i, a_i, v_float_i, g_i, i_e_i, v_p_i, b_i = fit_lang(v_i,c_i)
    i_sat_i = objective_function(v_float_i, T_ev_i,a_i, v_float_i, g_i, i_e_i, v_p_i, b_i)

    Fit_state_d, T_ev_d, a_d, v_float_d, g_d, i_e_d, v_p_d, b_d = fit_lang(v_d,c_d)
    i_sat_d = objective_function(v_float_d, T_ev_d,a_d, v_float_d, g_d, i_e_d, v_p_d, b_d)

    if Fit_state_i == True and Fit_state_d == True:
        if T_ev_i < T_ev_d:
             i_sat = i_sat_i
             T_ev = T_ev_i
        else:
             i_sat = i_sat_d
             T_ev = T_ev_d

        if abs((i_sat - float(user_answer["i_sat"]))/i_sat) * 100 < error:
             print("You are Correct!! Correct response: "+str(i_sat)+" uA")
             return True
        else:
             print("Incorrect... Correct response: "+str(i_sat)+" uA")
             return False

    elif Fit_state_i == True:
         print("problem with the Fit of d")
         return False
    elif Fit_state_d == True:
         print("problem with the Fit of i")
         return False
    else:
         print("problem with the Fits")
         return False

def Langmuir_density(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):

    v_i,c_i,v_d,c_d = GetCurrentVolts(current_question, user_answer, decimal_places, current_quiz, execution, all_executions)
    
    error, elementary_charge, me, radius, length, atomic_mass_unit, boltzmann, atom, t_k, epsilon, atom = constanst(execution.config["gas_selector"])

    Fit_state_i, T_ev_i,a_i, v_float_i, g_i, i_e_i, v_p_i, b_i = fit_lang(v_i,c_i)
    i_sat_i = objective_function(v_float_i, T_ev_i,a_i, v_float_i, g_i, i_e_i, v_p_i, b_i)

    Fit_state_d, T_ev_d,a_d, v_float_d, g_d, i_e_d, v_p_d, b_d = fit_lang(v_d,c_d)
    i_sat_d = objective_function(v_float_d, T_ev_d,a_d, v_float_d, g_d, i_e_d, v_p_d, b_d)

    if Fit_state_i == True and Fit_state_d == True:
        if T_ev_i < T_ev_d:
             i_sat = i_sat_i
             T_ev = T_ev_i 
        else:
             i_sat = i_sat_d
             T_ev = T_ev_d
        speed_sound = math.sqrt(boltzmann * T_ev * t_k / (atom * atomic_mass_unit))
        area_probe = math.pi * radius * radius + 2 * math.pi * radius * length
        ion_density = (2 * i_sat * 1e-6) / (elementary_charge * speed_sound * area_probe)
        
        ion_density_10_15 = ion_density*10**(-15)
        
        if abs((ion_density_10_15 - float(user_answer["ion_density"]))/ion_density_10_15) * 100 < error:
             print("You are Correct!! Correct response: "+str(ion_density_10_15)+" x10^15 m^3")
             return True
        else:
             print("Incorrect... Correct response: "+str(ion_density_10_15)+" x10^15 m^3")
             return False


    elif Fit_state_i == True:
         print("problem with the Fit of d")
         return False

    elif Fit_state_d == True:
         print("problem with the Fit of i")
         return False

    else:
         print("problem with the Fits")
         return False



def Langmuir_radius(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):

    v_i,c_i,v_d,c_d = GetCurrentVolts(current_question, user_answer, decimal_places, current_quiz, execution, all_executions)
    
    error, elementary_charge, me, radius, length, atomic_mass_unit, boltzmann, atom, t_k, epsilon, atom = constanst(execution.config["gas_selector"])

    Fit_state_i, T_ev_i,a_i, v_float_i, g_i, i_e_i, v_p_i, b_i = fit_lang(v_i,c_i)
    i_sat_i = objective_function(v_float_i, T_ev_i,a_i, v_float_i, g_i, i_e_i, v_p_i, b_i)

    Fit_state_d, T_ev_d,a_d, v_float_d, g_d, i_e_d, v_p_d, b_d = fit_lang(v_d,c_d)
    i_sat_d = objective_function(v_float_d, T_ev_d,a_d, v_float_d, g_d, i_e_d, v_p_d, b_d)

    if Fit_state_i == True and Fit_state_d == True:
        if T_ev_i < T_ev_d:
             i_sat = i_sat_i
             T_ev = T_ev_i 
        else:
             i_sat = i_sat_d
             T_ev = T_ev_d

        speed_sound = math.sqrt(boltzmann * T_ev * t_k / (atom * atomic_mass_unit))
        area_probe = math.pi * radius * radius + 2 * math.pi * radius * length
        ion_density = (2 * i_sat * 1e-6) / (elementary_charge * speed_sound * area_probe)
        d_length = np.sqrt((epsilon * boltzmann * T_ev * t_k) / (ion_density * elementary_charge * elementary_charge))        
        
        d_length_mm = d_length *1000
        
        if abs((d_length_mm - float(user_answer["d_length"]))/d_length_mm) * 100 < error:
             print("You are Correct!! Correct response: "+str(d_length)+" mm")
             return True
        else:
             print("Incorrect... Correct response: "+str(d_length)+" mm")
             return False


    elif Fit_state_i == True:
         print("problem with the Fit of d")
         return False

    elif Fit_state_d == True:
         print("problem with the Fit of i")
         return False

    else:
         print("problem with the Fits")
         return False




def Langmuir_new_density(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):

    v_i,c_i,v_d,c_d = GetCurrentVolts(current_question, user_answer, decimal_places, current_quiz, execution, all_executions)
    
    error, elementary_charge, me, radius, length, atomic_mass_unit, boltzmann, atom, t_k, epsilon, atom = constanst(execution.config["gas_selector"])

    Fit_state_i, T_ev_i,a_i, v_float_i, g_i, i_e_i, v_p_i, b_i = fit_lang(v_i,c_i)
    i_sat_i = objective_function(v_float_i, T_ev_i,a_i, v_float_i, g_i, i_e_i, v_p_i, b_i)

    Fit_state_d, T_ev_d,a_d, v_float_d, g_d, i_e_d, v_p_d, b_d = fit_lang(v_d,c_d)
    i_sat_d = objective_function(v_float_d, T_ev_d,a_d, v_float_d, g_d, i_e_d, v_p_d, b_d)

    if Fit_state_i == True and Fit_state_d == True:
        if T_ev_i < T_ev_d:
             i_sat = i_sat_i
             T_ev = T_ev_i 
        else:
             i_sat = i_sat_d
             T_ev = T_ev_d
        speed_sound = math.sqrt(boltzmann * T_ev * t_k / (atom * atomic_mass_unit))
        area_probe = math.pi * radius * radius + 2 * math.pi * radius * length
        ion_density = (2 * i_sat * 1e-6) / (elementary_charge * speed_sound * area_probe)
        d_length = np.sqrt((epsilon * boltzmann * T_ev * t_k) / (ion_density * elementary_charge * elementary_charge))
   
        if d_length > radius:
            new_radius = radius + d_length 
            area_probe = math.pi * new_radius * new_radius + 2 * math.pi * new_radius * length
            ion_density_new = (2 * i_sat * 1e-6) / (elementary_charge * speed_sound * area_probe)    
        else:
            ion_density_new = ion_density

        ion_density_new_10_15 = ion_density_new*10**(-15)

        if abs((ion_density_new_10_15 - float(user_answer["new_density"]))/ion_density_new_10_15) * 100 < error:
             print("You are Correct!! Correct response: "+str(ion_density_new_10_15)+" x10^15 m^3")
             return True
        else:
             print("Incorrect... Correct response: "+str(ion_density_new_10_15)+" x10^15 m^3")
             return False


    elif Fit_state_i == True:
         print("problem with the Fit of d")
         return False

    elif Fit_state_d == True:
         print("problem with the Fit of i")
         return False

    else:
         print("problem with the Fits")
         return False


def Langmuir_new_temp(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):
    
    v_i,c_i,v_d,c_d = GetCurrentVolts(current_question, user_answer, decimal_places, current_quiz, execution, all_executions)
   
    error, elementary_charge, me, radius, length, atomic_mass_unit, boltzmann, atom, t_k, epsilon, atom = constanst(execution.config["gas_selector"])


    Fit_state_i, T_ev_i,a_i, v_float_i, g_i, i_e_i, v_p_i, b_i = fit_lang(v_i,c_i)
    i_sat_i = objective_function(v_float_i, T_ev_i,a_i, v_float_i, g_i, i_e_i, v_p_i, b_i)

    Fit_state_d, T_ev_d,a_d, v_float_d, g_d, i_e_d, v_p_d, b_d = fit_lang(v_d,c_d)
    i_sat_d = objective_function(v_float_d, T_ev_d,a_d, v_float_d, g_d, i_e_d, v_p_d, b_d)

    if Fit_state_i == True and Fit_state_d == True:
        if T_ev_i < T_ev_d:
             i_sat = i_sat_i
             T_ev = T_ev_i
             V_Float = v_float_i 
        else:
             i_sat = i_sat_d
             T_ev = T_ev_d
             V_Float = v_float_d
        speed_sound = math.sqrt(boltzmann * T_ev * t_k / (atom * atomic_mass_unit))

        T_ev_new = 2*elementary_charge *V_Float/(np.log(np.sqrt(((atom * atomic_mass_unit)/(4*math.pi*me))))*boltzmann*t_k)    

        if abs((T_ev_new - float(user_answer["T_plasma_bohm"]))/T_ev_new) * 100 < error:
             print("You are Correct!! Correct response: "+str(T_ev_new))
             return True
        else:
             print("Incorrect... Correct response: "+str(T_ev_new))
             return False


    elif Fit_state_i == True:
         print("problem with the Fit of d")
         return False

    elif Fit_state_d == True:
         print("problem with the Fit of i")
         return False

    else:
         print("problem with the Fits")
         return False



