from django.shortcuts import render

import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, RedirectView, TemplateView, View
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.utils.decorators import method_decorator

from braces.views import LoginRequiredMixin
from extra_views import InlineFormSetView

from caring_professionals.models import CaringProfessional
from jobs.utils import get_or_create_job_from_proposal
from patients.models import Patient

from .forms import (RequestForCareForm, RequestForCareProposalForm,
    RequestForCarePublishForm, RequestForCareReviewFilterForm)
from .models import RequestForCare, RequestForCareProposal, RequestForCareStatus


class RequestForCareCreate(LoginRequiredMixin, CreateView):
    model = RequestForCare
    form_class = RequestForCareForm

    def get_form(self, form_class):
        form = super(RequestForCareCreate, self).get_form(form_class)
        form.helper.form_action = reverse('requests_for_care-create')

        form.fields['patient'].queryset = Patient.objects.filter(user=self.request.user)

        return form

    def form_valid(self, form):
        form.instance.client = self.request.user

        response = super(RequestForCareCreate, self).form_valid(form)

        if '_publish' in self.request.POST:
            self.success_url = reverse('requests_for_care-publish', kwargs={'pk': self.object.pk})

        return response


class RequestForCareUpdate(LoginRequiredMixin, UpdateView):
    model = RequestForCare
    form_class = RequestForCareForm

    def get_form(self, form_class):
        form = super(RequestForCareUpdate, self).get_form(form_class)
        form.helper.form_action = reverse('requests_for_care-update', kwargs={'pk': self.object.pk})

        return form

    def form_valid(self, form):
        form.instance.client = self.request.user

        response = super(RequestForCareUpdate, self).form_valid(form)

        if '_publish' in self.request.POST:
            self.success_url = reverse('requests_for_care-publish', kwargs={'pk': self.object.pk})

        return response


class RequestForCarePublish(LoginRequiredMixin, FormView):
    template_name = 'requests_for_care/requestforcare_publish.html'
    form_class = RequestForCarePublishForm

    def get_success_url(self):
        return reverse('requests_for_care-detail', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super(RequestForCarePublish, self).get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def get_form(self, form_class):
        form = super(RequestForCarePublish, self).get_form(form_class)
        form.helper.form_action = reverse('requests_for_care-publish', kwargs={'pk': self.kwargs['pk']})

        return form

    def get_context_data(self, **kwargs):
        context = super(RequestForCarePublish, self).get_context_data(**kwargs)
        context['suggested_caring_professional_list'] = CaringProfessional.objects.all()

        return context

    def form_valid(self, form):
        if '_all' in self.request.POST:
            status = RequestForCareStatus.STATUS_PUBLIC
        else:
            status = RequestForCareStatus.STATUS_PRIVATE

        request_for_care = get_object_or_404(
            RequestForCare, pk=self.kwargs['pk'], client=self.request.user
        )

        RequestForCareStatus.objects.get_or_create(
            request_for_care=request_for_care, status=status
        )

        for user in form.cleaned_data.get('caring_professionals'):
            RequestForCareProposal.objects.get_or_create(
                request_for_care=request_for_care,
                user=user,
                defaults={'active': True}
            )

        return super(RequestForCarePublish, self).form_valid(form)


class RequestForCareCancel(LoginRequiredMixin, TemplateView):
    template_name = 'requests_for_care/cancel.html'

    def post(self, request, *args, **kwargs):
        request_for_care = get_object_or_404(
            RequestForCare, pk=self.kwargs['pk'], client=request.user
        )
        RequestForCareStatus.objects.get_or_create(
            request_for_care=request_for_care, status=RequestForCareStatus.STATUS_CANCELLED
        )
        return HttpResponseRedirect(reverse('requests_for_care-list'))

    def get_context_data(self, **kwargs):
        context = super(RequestForCareCancel, self).get_context_data(**kwargs)
        context['request_for_care'] = get_object_or_404(
            RequestForCare, pk=self.kwargs['pk'], client=self.request.user
        )

        return context


class RequestForCareProposalUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'requests_for_care/requestforcareproposal_form.html'
    form_class = RequestForCareProposalForm
    model = RequestForCareProposal
    success_url = reverse_lazy('requests_for_care-list')

    def get_object(self, queryset=None):
        try:
            request_for_care = RequestForCare.objects.filter(
                Q(statuses__status=RequestForCareStatus.STATUS_PUBLIC) |
                Q(statuses__status=RequestForCareStatus.STATUS_PRIVATE, proposals__user=self.request.user)
            ).distinct().get(
                pk=self.kwargs['pk']
            )
        except RequestForCare.DoesNotExist:
            raise Http404

        obj, _unused = self.model.objects.get_or_create(
            request_for_care=request_for_care,
            user=self.request.user
        )
        obj.viewed = True
        obj.save()

        return obj

    def get_context_data(self, **kwargs):
        context = super(RequestForCareProposalUpdate, self).get_context_data(**kwargs)
        context['request_for_care'] = self.object.request_for_care

        return context

    def form_valid(self, form):
        response = super(RequestForCareProposalUpdate, self).form_valid(form)

        if '_submit' in self.request.POST:
            self.object.submitted = datetime.datetime.now()

        self.object.save()

        return response


class RequestForCareProposalDetail(LoginRequiredMixin, DetailView):
    model = RequestForCareProposal

    def get_queryset(self):
        request_for_care = get_object_or_404(
            RequestForCare, pk=self.kwargs['rfc_pk'], client=self.request.user
        )

        return self.model.objects.filter(
            request_for_care=request_for_care,
            submitted__isnull=False
        )


class RequestForCareProposalAccept(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        request_for_care_proposal = get_object_or_404(
            RequestForCareProposal,
            pk=kwargs['pk'],
            request_for_care__pk=kwargs['rfc_pk'],
            request_for_care__client=self.request.user
        )
        request_for_care_proposal.status = RequestForCareProposal.STATUS_ACCEPTED
        request_for_care_proposal.save()

        url = self.request.GET.get(
            'next',
            self.request.META.get(
                'HTTP_REFERER',
                request_for_care_proposal.get_absolute_url()
            )
        )

        return url


class RequestForCareProposalReject(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        request_for_care_proposal = get_object_or_404(
            RequestForCareProposal,
            pk=kwargs['pk'],
            request_for_care__pk=kwargs['rfc_pk'],
            request_for_care__client=self.request.user
        )
        request_for_care_proposal.status = RequestForCareProposal.STATUS_REJECTED
        request_for_care_proposal.save()

        url = self.request.GET.get(
            'next',
            self.request.META.get(
                'HTTP_REFERER',
                request_for_care_proposal.get_absolute_url()
            )
        )

        return url


class RequestForCareProposalContract(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        request_for_care_proposal = get_object_or_404(
            RequestForCareProposal,
            pk=kwargs['pk'],
            request_for_care__pk=kwargs['rfc_pk'],
            request_for_care__client=self.request.user
        )
        request_for_care_proposal.status = RequestForCareProposal.STATUS_ACCEPTED
        request_for_care_proposal.save()

        job = get_or_create_job_from_proposal(request_for_care_proposal)

        return reverse('jobs-update', kwargs={'pk': job.pk})


class RequestForCareReview(LoginRequiredMixin, DetailView):
    model = RequestForCare
    template_name = 'requests_for_care/requestforcare_review.html'
    short_list = False

    def get_context_data(self, **kwargs):
        context = super(RequestForCareReview, self).get_context_data(**kwargs)
        initial = {'request_for_care': self.object.get_absolute_url()}

        if self.request.GET.get('order_by'):
            order_by = self.request.GET['order_by']
            initial['order_by'] = order_by
        else:
            order_by = '?'

        qs = self.get_object().proposals.exclude(status=RequestForCareProposal.STATUS_REJECTED)

        if self.short_list:
            qs = qs.filter(status=RequestForCareProposal.STATUS_ACCEPTED)

        form = RequestForCareReviewFilterForm(initial)

        form.fields['request_for_care'].choices = (
            (rfc.get_absolute_url(), rfc.name) for rfc in RequestForCare.objects.filter(
                client=self.request.user
            )
        )

        context['form'] = form
        context['request_for_care_proposal_list'] = qs.order_by(order_by)
        context['short_list'] = self.short_list
        context['order_by'] = order_by

        return context


class RequestForCareDetail(LoginRequiredMixin, DetailView):
    model = RequestForCare


class RequestForCareList(LoginRequiredMixin, ListView):
    draft_only = False
    model = RequestForCare
    allow_empty = True

    def get_template_names(self):
        if hasattr(self.request.user, 'caring_professional'):
            return ['requests_for_care/requestforcare_caring_professional_list.html']
        else:
            return ['requests_for_care/requestforcare_client_list.html']

    def get_queryset(self):
        if hasattr(self.request.user, 'caring_professional'):
            qs = self.model.objects.filter(
                Q(statuses__status=RequestForCareStatus.STATUS_PUBLIC) |
                Q(statuses__status=RequestForCareStatus.STATUS_PRIVATE, proposals__user=self.request.user)
            ).distinct()

        else:
            qs = self.model.objects.filter(
                client=self.request.user
            )

            if self.draft_only:
                qs = qs.filter(statuses__status=RequestForCareStatus.STATUS_DRAFT)

        return qs

