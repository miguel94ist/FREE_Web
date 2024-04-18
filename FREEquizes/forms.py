from django import forms
from django.forms.widgets import RadioSelect, Textarea


class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if question is not False:
            choice_list = [x for x in question.get_answers_list()]
            self.fields["answer"] = forms.ChoiceField(choices=choice_list,
                                                        widget=RadioSelect)


class EssayForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(EssayForm, self).__init__(*args, **kwargs)
        #if question.sub_category != None:
        #    self.fields["answers"] = forms.FloatField(required=False)
        #else:
        for f in question.multiple_answer_fields.keys():    
            self.fields[f] = forms.FloatField()
            self.fields[f].label = f+" (%s)"%(question.multiple_answer_fields[f]['unit'],)
        
        
class Experiment_ExectionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(Experiment_ExectionForm, self).__init__(*args, **kwargs)
        
