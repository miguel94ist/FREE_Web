def verify_mc(current_question, user_answer, decimal_places, current_quiz, execution):
    print(current_question, user_answer, decimal_places, current_quiz, execution)
    print(execution.result_set.all()[0].result_type)
    print(execution.result_set.all()[0].value)
    if int(user_answer) == 12:
        return True
    else:
        return False

def area_approximation(self, guess, execution,decimal):
    if execution == None:
        return False
    else:
        queryset = ResultSerializer(
            Result.objects.get(result_type='f', execution=execution)).data

        points_in = len(
            [values for values in queryset["value"] if values['circ']=='1'])
        sq_area = (2*execution.config['R'])**2
        area_approx = round(sq_area * points_in/len(queryset["value"]),decimal)
        print("Right answer:",area_approx)
        self.explanation = f"The approximate area of the circle was: {area_approx}"
        self.save()
        
        return not bool(guess - area_approx)
    # if (guess - area_approx) == 0:
    #     return True
    # else:
    #     return False

def number_points(self,guess,execution,decimal):
    if guess < 100:
        return False
    else:  
        return True
    
def validate_points(self,guess,execution,decimal):
    if execution == None:
        return False
    else:
        if execution.config['Iteration'] != int(guess):
            return False
        else:
            return True
