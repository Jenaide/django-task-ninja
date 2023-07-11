from django import forms

# Reordering Form and View

"""" sets up a form called PositionForm with a single field called 
"position" where users can input the positions of tasks for reordering """
class PositionForm(forms.Form):
    position = forms.CharField()