from django import forms

class rfcProposal(forms.Form):
    names = forms.CharField(max_length=150)
    message = forms.CharField(widget=forms.Textarea)
    select = forms.Select()
    checkbox = forms.CheckboxSelectMultiple()
    sender = forms.EmailField()
    
    def send_eamil(self):
        # send email using the self.cleaned_data dictionary
        pass