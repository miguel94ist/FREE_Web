import json
import math
from scipy.stats import linregress
import numpy as np
from scipy.odr import *
# import matplotlib.pyplot as plt


def pend_execution_parameters(user_answers):

    #make sure the input is between 8 and 16 cm

    delta_x = int(user_answers[0]["answer"]["DeltaX 1"])
    if delta_x < 8 or delta_x > 16:
        delta_x = np.random.randint(8, 16)

    return [
        {
            "name": "deltaX",
            "description": "Initial displacement (cm)",
            "value": delta_x,
        },
        {
            "name": "samples",
            "description": "Number of Samples",
            "value": np.random.randint(13, 30),
        },
    ]


def pend_execution_parameters_2(user_answers):
    print(user_answers)
    # print(user_answers[0]["answer"]["DeltaX 1"])
    return [
        {
            "name": "deltaX",
            "description": "Initial displacement (cm)",
            "value": int(user_answers[-1]["answer"]["DeltaX 2"]),
        },
        {
            "name": "samples",
            "description": "Number of Samples",
            "value": 10,
        },
    ]

def pend_execution_parameters_3(user_answers):
    print(user_answers)
    # print(user_answers[0]["answer"]["DeltaX 1"])
    return [
        {
            "name": "deltaX",
            "description": "Initial displacement (cm)",
            "value": int(user_answers[-2]["answer"]["DeltaX 3"]),
        },
        {
            "name": "samples",
            "description": "Number of Samples",
            "value": 10,
        },
    ]

def pend_execution_parameters_4(user_answers):
    print(user_answers)
    # print(user_answers[0]["answer"]["DeltaX 1"])
    return [
        {
            "name": "deltaX",
            "description": "Initial displacement (cm)",
            "value": int(user_answers[-3]["answer"]["DeltaX 4"]),
        },
        {
            "name": "samples",
            "description": "Number of Samples",
            "value": 10,
        },
    ]

def execution_parameters_8_16_cm(
    current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,):
    delta_x = int(user_answer["DeltaX 1"])
    if delta_x < 8 or delta_x > 16:
        return False
    
    else:
        return True




def execution_parameters_one_cm_appart(current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,):

    deltaX = []
    deltaX.append(execution.config["deltaX"])
    deltaX.append(user_answer["DeltaX 2"])
    deltaX.append(user_answer["DeltaX 3"])
    deltaX.append(user_answer["DeltaX 4"])  

    if len(set(deltaX)) < 4:
        return False
    
    else:
        for delta in deltaX:
            if delta < 7 or delta > 22:
                return False
        return True



def initial_height_single(
    current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,
):
    L = (execution.apparatus.parameters['L'] + execution.apparatus.parameters["d_sphere"]/2)/1000
    displacement = execution.config["deltaX"] / 100
    initial_height = (L - math.sqrt(L**2 - displacement**2)) * 100

    initial_height_answer = user_answer['Initial Height']
    print(f"The initial_height is {initial_height}")
    if abs(initial_height - initial_height_answer) < 0.05*initial_height:
        return True

    else:
        return False


def g_constant_single(
    current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,
):
    L = (execution.apparatus.parameters['L'] + execution.apparatus.parameters["d_sphere"]/2)/1000

    print(execution.result_set)
    data = execution.result_set.all()
    data_len = len(data) - 1
    T_average = 0
    for entry in data[1:]:
        T_average += float(entry.value["Val1"]) / float(data_len)

    g = 4 * math.pi**2 * L / T_average**2
    print(f"The average T is {T_average}")
    print(f"The correct answer is g = {g}")
    if abs(g - user_answer['g']) < g*0.002:
        return True
    else:
        return False


    
def std_deviation_period(current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,
):

    data = execution.result_set.all()
    T = []
    for entry in data[1:]:
        T.append(float(entry.value["Val1"]))
    
    T_std = np.std(T, ddof=1)

    if abs(T_std*1000 - user_answer['Standard Deviation of Period']) < T_std*1000 * 0.05:
        return True
    else:
        return False




def g_error_propagation_single(
    current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,
):
    L = (execution.apparatus.parameters['L'] + execution.apparatus.parameters["d_sphere"]/2)/1000
    T = []
    delta_L = (execution.apparatus.parameters['delta_L']+execution.apparatus.parameters['delta_d_sphere']/2)/1000
    data = execution.result_set.all()
    data_len = len(data) - 1
    T_average = 0
    for entry in data[1:]:
        T_average += float(entry.value["Val1"]) / float(data_len)
        T.append(float(entry.value["Val1"]))
    
    delta_T = np.std(T, ddof=1)

    delta_g = (
        abs(4 * math.pi**2 / T_average**2) * delta_L
        + abs(8 * math.pi**2 * L / T_average**3) * delta_T
    )

    print(f"The error of g is {delta_g}")
    if abs(delta_g - user_answer['Error of g']) < 0.05*delta_g:
        return True
    else:
        return False


def g_single_energy(
    current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,
):
    L = (execution.apparatus.parameters['L'] + execution.apparatus.parameters["d_sphere"]/2)/1000
    displacement = execution.config["deltaX"] / 100
    height = L - math.sqrt(L**2 - displacement**2)
    m_speeds = []
    for reading in execution.result_set.all()[1 :]:
            #print(reading.value["Val3"])
            m_speeds.append(float(reading.value["Val3"])/100)

    max_speed_squared = np.average(m_speeds) ** 2
    g = 1/2 * max_speed_squared / height
    if abs(g - float(user_answer["g"])) < 0.01:
        return True
    else:
        return False


def g_constant_fit(
    current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,
):
    L = (execution.apparatus.parameters['L'] + execution.apparatus.parameters["d_sphere"]/2) / 1000

    # Get the data from all executions
    num_entries = 10
    initial_height = []
    max_speed_squared = []

    for exect in all_executions:
        displacement = exect.config["deltaX"] / 100
        i_height = L - math.sqrt(L**2 - displacement**2)

        readings = exect.result_set.all()[0].value
        num_readings = len(readings)
        # Adjust the number of readings to consider
        num_to_consider = min(num_entries, num_readings)
        for reading in readings[:num_to_consider]:
            if float(reading["Val3"]) == 0:
                continue
            max_speed_squared.append((float(reading["Val3"]) / 100)**2)
            initial_height.append(i_height)

    # Check if there are at least 3 different initial heights
    unique_heights = set(initial_height)
    if len(unique_heights) < 3:
        return False

    # Calculate g_fit and compare with user's answer
    g_fit = calculate_g_fit(initial_height, max_speed_squared, L).slope / 2
    print(f"g through fit was: {g_fit}")

    if abs(g_fit - float(user_answer["g"])) < 0.05 * g_fit:
        return True
    else:
        return False

def g_fit_error(
    current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,
):
    
    L = (execution.apparatus.parameters['L'] + execution.apparatus.parameters["d_sphere"]/2) / 1000

    # Get the data from all executions
    num_entries = 10
    initial_height = []
    max_speed_squared = []

    for exect in all_executions:
        displacement = exect.config["deltaX"] / 100
        i_height = L - math.sqrt(L**2 - displacement**2)

        readings = exect.result_set.all()[0].value
        num_readings = len(readings)
        # Adjust the number of readings to consider
        num_to_consider = min(num_entries, num_readings)
        for reading in readings[:num_to_consider]:
            if float(reading["Val3"]) == 0:
                continue
            max_speed_squared.append((float(reading["Val3"]) / 100)**2)
            initial_height.append(i_height)

    #need at least 3 different values for a valid fit
    unique_heights = set(initial_height)

    if len(unique_heights) < 3:
        return False

    regression = calculate_g_fit(initial_height, max_speed_squared, L)
    g_error = regression.stderr / 2
    print(f"g error through fit was: {g_error}")

    if float(user_answer["Error of g fit"]) < 3 * g_error and float(user_answer["Error of g fit"]) > 0.33 * g_error:
        return True
    else:
        return False
    


def systematic_x_error(
    current_question,
    user_answer,
    decimal_places,
    current_quiz,
    execution,
    all_executions,):

    L = (execution.apparatus.parameters['L'] + execution.apparatus.parameters["d_sphere"]/2) / 1000

    # Get the data from all executions
    num_entries = 10
    initial_height = []
    max_speed_squared = []

    for exect in all_executions:
        displacement = exect.config["deltaX"] / 100
        i_height = L - math.sqrt(L**2 - displacement**2)

        readings = exect.result_set.all()[0].value
        num_readings = len(readings)
        # Adjust the number of readings to consider
        num_to_consider = min(num_entries, num_readings)
        for reading in readings[:num_to_consider]:
            if float(reading["Val3"]) == 0:
                continue
            max_speed_squared.append((float(reading["Val3"]) / 100)**2)
            initial_height.append(i_height)

    #need at least 3 different values for a valid fit
    unique_heights = set(initial_height)

    if len(unique_heights) < 3:
        return False

    regression = calculate_g_fit(initial_height, max_speed_squared, L)
    a = regression.slope
    b = regression.intercept
    h0 = -b / a
    x0 = math.sqrt(-(abs(h0)-L)**2 + L**2)
    if abs(x0 - float(user_answer["x_error"])) < x0*0.05:
        return True
    else:
        return False



def calculate_g_fit(initial_height, max_speed_squared, l):
    regression = linregress(initial_height, max_speed_squared)
    # print(regression)

    # Plot the fitted line
    fitted_line = [regression.slope * x + regression.intercept for x in initial_height]

    # Create a scatter plot of (displacement, max_speed) points

    # plt.scatter(initial_height, max_speed_squared, label="Data Points")
    
    # plt.plot(initial_height, fitted_line, color="red", label="Fitted Line")
    
    # plt.xlabel("Displacement")
    # plt.ylabel("Max Speed")
    # plt.title("Displacement vs. Max Speed")
    # plt.legend()
    # plt.grid(True)
    
    # plt.show()
    return regression

