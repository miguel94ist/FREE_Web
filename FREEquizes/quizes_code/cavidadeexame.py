import numpy as np
import pandas as pd
from scipy import pi,sqrt,exp
from scipy.special import erf
from scipy import signal
from scipy.optimize import curve_fit
from scipy import stats
from scipy.stats import norm, anderson
from scipy.stats import skewnorm
from scipy.stats import kurtosis
import random as rd 

#def exec2_parameters():
#    return [{'name': 'R', 
#             'description': 'radius',
#              'value': 5}
#            ]


def execution_parameters_random_cavidade(user_answers):

    injection = [15,35, 50, 80, 100, 120, 150]
    index_ijection  =rd.randint(0, len(injection)-1)

    gas_label = ["Helium (He)", "Nitrogen (N)","Argon (Ar)"]
    gas_type = [1,2,3]
    index_gas = rd.randint(0, len(gas_type)-1)

    magnetic_field_label = [12,14,17,22]
    magnetic_field = [1,2,3,4]
    index_magnetic = rd.randint(0, len(magnetic_field)-1)
    
    discharge_label = [2.5,3.5]
    discharge = [1,2]
    index_discharge = rd.randint(0, len(discharge)-1)
    
    return [{'name': 'pressure', 
             'description': 'Gas Injection Time [ms]',
              'value': injection[index_ijection]},
             {'name': 'gas_selector',
              'description': 'Gas Selection',
              'value': gas_type[index_gas],
              'label': gas_label[index_gas]},
             {'name': 'discharge',
              'description': 'Power of Discharge [W]',
              'value': discharge[index_discharge],
              'label': discharge_label[index_discharge]},
             {'name': 'magnetic_field',
              'description': 'Magnetic Field [mT]',
              'value': magnetic_field[index_magnetic],
              'label': magnetic_field_label[index_magnetic]}
            ]


def configured_execution(JSON_config):
     JSON_config["f_start"] =  3400
     JSON_config["f_end"] =  3700
     JSON_config["f_step"] = 0.4
     JSON_config["n_iteration"] = 5
     JSON_config["back_pressure"] = 25
     JSON_config["pressure"] = 20
     JSON_config["gas_selector"] = 3
     JSON_config["magnetic_field"] = 0
     JSON_config["discharge"] = 1

     return JSON_config 



# Function to reject outliers
# Returns filtered list and list of indices of removed elements

def reject_outliers_2(data, m=2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    
    indices=[]
    data_n = []
    
    for i in range(len(s)):
        if s[i] < m:
            data_n.append(data[i])
        else:
            indices.append(i) 
    return data_n,indices

# Define the Gaussian function
def Gauss(x, A, B,C,mu):
    y = A*np.exp(-((x-mu)**2)/(2*B**2)) + C
    return y


def pdf(x):
    return 1/np.sqrt(2*pi) * np.exp(-x**2/2)

def cdf(x):
    return (1 + erf(x/np.sqrt(2))) / 2

def skew(x,e=0,w=1,a=0):
    t = (x-e) / w
    return 2 / w * pdf(t) * cdf(a*t)
    # You can of course use the scipy.stats.norm versions
    # return 2 * norm.pdf(t) * norm.cdf(a*t)

def fit_skew (x,e,w,a,amp,b):
    return amp*skew(x,e,w,a)+b







def analyze_spectrum(freq,amp,skew=False,debug=False):

    # Find peaks
    # Use scipy signal.find_peaks
    # We need to paramters to optimize search for peaks: minimum distance between peaks allowed, minimum height of the peak
    # I chose these with some arbitrary criteria

    h = np.mean(amp) # height - mean of the data
    d = len(amp)/4 # minimum distance - 1/4 of the data

    peaks = signal.find_peaks(amp,distance=d,height = h)
    centroid_guess = peaks[0][0]

    if amp[centroid_guess] < amp[amp.argmax()]:
        centroid_guess = amp.argmax()

    # Creates a copy of the amplitude list with zeros in the place of elements which have values less than the threshold desired.
    # This threshold is defined in relation to the amplitude of the centroid

    a_threshold = 5.5  # we allow values 5 dB smaller than the maximum amplitude


    new_amp = []
    amp_max = amp[centroid_guess]

    for i in range(len(amp)):
        a = amp[i]
        if a>=(amp_max-a_threshold):
            new_amp.append(a)
        else:
            new_amp.append(0)
    
    # Here we find the x limits (frequencies) for our fit
    # The criteria is based on the number of successive zeros we allow

    zeros_crit = 3


    lim_i = centroid_guess
    lim_s = centroid_guess
    #print("size of new_amp: "+str(len(new_amp)))

    zeros_counter = 0

    while zeros_counter < zeros_crit and lim_s < len(new_amp)-1:  # loop to the right until you find zeros_crit succesive zeros
        if new_amp[lim_s] == 0:
            zeros_counter+=1
            lim_s += 1
        else:
            lim_s += 1
            zeros_counter = 0

    #print(lim_s)
    zeros_counter = 0        
    while zeros_counter < zeros_crit and lim_i > 0: # loop to the left until you find zeros_crit succesive zeros
        if new_amp[lim_i] == 0:
            zeros_counter+=1
            lim_i -= 1
        else:
            lim_i -= 1
            zeros_counter = 0
    if debug:
        print(lim_i)
        print(lim_s)
        print(freq[lim_i])
        print(freq[lim_s])
    
    #centroid_guess = peaks[0][0]
    amp_guess = amp[centroid_guess]
    freq_guess = freq[centroid_guess]
    freq_min = freq[lim_i]
    freq_max = freq[lim_s]
    amp_max = amp_guess + 4
    amp_min = amp_guess - 6

    i_list=[]
    x_data=[]
    y_data=[]
    for i in range(len(amp)):
        f = freq[i]
        if f<=freq_max and f>=freq_min:
            i_list.append(i)
            x_data.append(f)
            y_data.append(amp[i])
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    
    # rejects outliers 
    out = reject_outliers_2(y_data, m=4.)
    
    y_data = np.array(out[0])
    x_data = np.delete(x_data,out[1])
   

    left_side = 0
    right_side = 0
    left_frequency = 0
    right_frequency = 0
    print(amp_guess)
    half_size_buff = int(len(y_data)/2)
    #print(half_size_buff)
    #print( y_data)

    max_y_index = y_data.argmax()

    for i in np.arange(max_y_index+2,len(y_data),1):
        a = y_data[i]
        if a<=(amp_guess-3) and right_side == 0 and abs(a-y_data[i-1])<1:
            print( a-y_data[i-1])
            right_frequency = x_data[i]
            right_amp = a
            right_side += 1
        else:
            #right_side = 0
            pass

    for i in np.arange(max_y_index-1,0,-1):
        a = y_data[i]
        if a<=(amp_guess-3) and left_side == 0 and abs(a-y_data[i+1])<1:
            left_frequency = x_data[i]
            left_amp = a
            left_side += 1
        else:
            #left_side = 0
            pass


    #print ("freq: "+str(left_frequency)+" "+str(right_frequency))
    #print ("amp: "+str(left_amp)+" "+str(right_amp))
    #print ("FWHM: "+str(right_frequency-left_frequency))
    #FWHM=(right_frequency-left_frequency)
    #if left_frequency == 0 or right_frequency == 0:
    #    guess_sgm = 0
    #else:
    #    guess_sgm = 1/(FWHM/2)**2 


    # Fit gaussian

    parameters, covariance = curve_fit(Gauss, x_data, y_data, bounds = (([0,0.1,-1000,freq_min],[80,500,0,freq_max])), maxfev=5000)

    fit_A = parameters[0]  # amplitude
    fit_B = parameters[1]  # width
    fit_C = parameters[2]  # vertical location
    fit_mu = parameters[3] # centroid location
    
    if debug:
        print(fit_A)
        print(fit_B)
        print(fit_C)
        print(fit_mu)
    
    
    fit_y = Gauss(x_data, fit_A, fit_B,fit_C, fit_mu)
    
    
    SE = np.sqrt(np.diag(covariance))
    SE_A = SE[0]
    SE_B = SE[1]
    SE_C = SE[2]
    SE_mu = SE[3]
    



    if skew:
        pass
    else:
        indices = [i for i, x in enumerate(fit_y) if x > max(fit_y)-3]
        FHWM_3d = x_data[indices[-1]]-x_data[indices[0]]
        return x_data[fit_y.argmax()], FHWM_3d
    # FIT to a skewed gaussian

    parameters_s, covariance_s = curve_fit(fit_skew, x_data, y_data, bounds = ([freq_min,0,-50,0,-30],[freq_max,300,500,800,30]), maxfev=5000)

    fit_mu = parameters_s[0]  # centroid / location
    fit_w = parameters_s[1]   # width
    fit_a = parameters_s[2]   # skewness parameter (a>0 right-skewed a<0 left-skewed)
    fit_amp = parameters_s[3] # amplitude
    fit_b = parameters_s[4]   # vertical location
    
    if debug:
        print(fit_mu)
        print(fit_w)
        print(fit_a)
        print(fit_amp)
        print(fit_b)
    
    
    fit_s = fit_skew(x_data,fit_mu,fit_w,fit_a,fit_amp,fit_b)
    
    
    
    SE_s = np.sqrt(np.diag(covariance_s))
    SE_s_mu = SE_s[0]
    SE_s_w = SE_s[1]
    SE_s_a = SE_s[2]
    SE_s_amp = SE_s[3]
    SE_s_b = SE_s[4]
    
    return x_data[fit_s.argmax()]



def analyze_mult_iteration(dados,skew,execution,debug=False):
    spctrm_frequency = []
    FHWM_3d_arr = []
    detect_miss_plasma = 3
    iteration_number = 1
    no_plasma_frequency = 3589.6
    for line in dados:
        if "frequency" in line.keys():
            #print(pd.to_numeric(line["magnitude"]))
            try:
                if skew:
                    spctrm_frequency.append(analyze_spectrum(pd.to_numeric(line["frequency"])/1000000,pd.to_numeric(line["magnitude"]),skew,debug))
                else:
                    frequency, FHWM_3d = analyze_spectrum(pd.to_numeric(line["frequency"])/1000000,pd.to_numeric(line["magnitude"]),skew,debug)
                    spctrm_frequency.append(frequency)
                    FHWM_3d_arr.append(FHWM_3d)
                iteration_number = iteration_number + 1
            except:
                print("error on the analyze_spectrum of the # "+str(iteration_number))
    
    i = 0 
    mean = 0
    mean_FHWM_3d = 0
    for data in range(len(spctrm_frequency)):
        if abs(data-no_plasma_frequency) < detect_miss_plasma and execution.config["discharge"] != 0:
            pass
        else:
            mean += spctrm_frequency[data]
            if not skew:
                mean_FHWM_3d += FHWM_3d_arr[data]
            i +=1
    if mean == 0:
        print("The user asked for plasma but didn't make plasma\n\r What to do ????")
        # Eu fazia com que o aluno tive-se esta pregunta errada
        mean = no_plasma_frequency
    else:
        mean = mean/i

    if skew:
        return mean
    else:
        if i != 0:
            mean_FHWM_3d = mean_FHWM_3d/i
        else:
            print("Erro no ajuste provavel nao ter plasma")
            mean_FHWM_3d = -1
        return mean, mean_FHWM_3d


def ressonat_frequency_shift(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):
    f0 = 3589.6
    debug = False
    skew = False
    error = 15 #%

    dados = execution.result_set.all()[0].value

    mean, FHWM_3d = analyze_mult_iteration(dados,skew,execution,debug)
    
    delta_f = mean - f0


    if abs(delta_f - float(user_answer))/delta_f * 100 < error:
        print("You are Correct!! Correct response: "+str(delta_f))
        return True
    else:
        print("Wrong. The correct response: "+str(delta_f))
        return False

def plasma_density_gauss(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):
    debug = False
    error = 15 #% de desvio relativo
    skew = False

    ne=0
    f0 = 3589.6
    me = 9.109*10**(-31)
    e_0 = 8.854187 *10**(-12)
    e = 1.602176634*10**(-19)
    
    dados = execution.result_set.all()[0].value
    mean, FHWM_3d = analyze_mult_iteration(dados,skew,execution,debug)

    if execution.config["discharge"] == 1:
        ne = (8*np.pi**2)*me*e_0/(e**2)*f0*(mean-f0)*(10**6*10**6)*10**(-15)
    else:
        print("nao fez plasma pregunta nao faz sentido")
        return False

    if abs(ne - float(user_answer))/ne * 100 < error:
        print("You are Correct!! Correct response: "+str(ne)) 
        return True
    else:
        print("Wrong. The correct response: "+str(ne))
        return False



def FWHM_gauss(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):
    debug = False
    skew = False

    error = 15 #% de desvio relativo
    dados = execution.result_set.all()[0].value
  
    mean, FHWM_3d = analyze_mult_iteration(dados,skew,execution,debug)
    print(FHWM_3d)
    FWHM = FHWM_3d 
    
    #FWHM = (1/np.sqrt(wid))*2 
    #FWHM = wid*2

    if abs(FWHM  - float(user_answer))/FWHM*100 < error:
        print("You are Correct!! Correct response: "+str(FWHM )) 
        return True
    else:
        print("Wrong. The correct response: "+str(FWHM))
        return False



def plasma_density_skew(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):
    debug = False
    error = 15 #% de desvio relativo
    skew = True

    ne=0
    f0 = 3589.6
    me = 9.109*10**(-31)
    e_0 = 8.854187 *10**(-12)
    e = 1.602176634*10**(-19)

    dados = execution.result_set.all()[0].value
    mean = analyze_mult_iteration(dados,skew,execution,debug)

    if execution.config["discharge"] == 1:
        ne = (8*np.pi**2)*me*e_0/(e**2)*f0*(mean-f0)*(10**6*10**6)*10**(-15)
    else:
        print("nao fez plasma pregunta nao faz sentido")
        return False

    if abs(ne - float(user_answer))/ne*100 < error:
        print("You are Correct!! Correct response: "+str(ne)+" and the new frequency is "+str(mean)) 
        return True
    else:
        print("Wrong. The correct response: "+str(ne)+" and the new frequency is "+str(mean))
        return False



def ressonat_frequency(current_question, user_answer, decimal_places, current_quiz, execution, all_executions):
    debug = False
    error  = 15 #% de desvio relativo
    skew = True    

    print(current_question)
    print(user_answer)
    print(decimal_places) 
    print(current_quiz)
    print(execution)
    #print(execution.result_set.all()[0].result_type)
    print(execution.config)
    dados = execution.result_set.all()[0].value
  
    mean = analyze_mult_iteration(dados,skew,execution,debug)

    
    if abs(mean - float(user_answer))/mean*100 < error:
        print("You are Correct!! Correct response: "+str(mean)) 
        return True
    else:
        print("Wrong. The correct response: "+str(mean))
        return False


