from django.shortcuts import render
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect

class rfcProposal(FormView):
    template_name = 'rfc_proposal.html'
    form_class = rfcProposal
    success_url = '/Thanks for Submitting your RFC Proposal/'
# Create your views here.

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super(rfcProposal, self).form_valid(form)
        
