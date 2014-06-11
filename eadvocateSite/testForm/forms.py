from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Fieldset, HTML, Layout, MultiField, Submit
from crispy_forms.bootstrap import (
    AppendedText, FormActions, InlineCheckboxes, InlineField, InlineRadios, PrependedAppendedText, PrependedText
)

from locations.models import Location
from needs.models import Need
from patients.models import Patient
from skills.models import Skill

from .models import RequestForCare, RequestForCareProposal


class RequestForCareForm(forms.ModelForm):
    need = forms.ModelChoiceField(queryset=Need.objects.all(), label='Define Need Area')
    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), label='Skill Sets Required')
    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(), label='Location', widget=forms.CheckboxSelectMultiple
    )
    open_ended = forms.BooleanField(label='...or make it open ended', required=False)
    time = forms.TimeField(input_formats=('%H:%M', '%I:%M %p'))

    class Meta:
        model = RequestForCare
        fields = (
            'patient',
            'name',
            'need',
            'services',
            'skills',
            'locations',  # TODO: Revise this functionality to match wires 1.0
            'street_address_1',
            'street_address_2',
            'city',
            'province',
            'postal_code',
            'frequency',
            'start_date',
            'end_date',
            'time',
            'min_pay',
            'max_pay',
            'languages',
            'gender',
            'criminal_check_required',
            'evaluation_criteria',
            'description',
            'deadline_to_respond'
        )

    def __init__(self, *args, **kwargs):
        super(RequestForCareForm, self).__init__(*args, **kwargs)

        self.fields['patient'].label = u'1. Patient Name'
        self.fields['patient'].help_text = u'Select the name of the person requiring care.'

        self.fields['name'].label = u'2. Care Request Name (optional)'
        self.fields['name'].help_text = u'Create a file name for this RFC.'
        self.fields['name'].required = False

        self.fields['need'].label = u'3. Select Need Area'
        self.fields['need'].help_text = u'Choose a Need Area that this care fits into.'

        self.fields['services'].label = u'4. Description of the Care services you need'
        self.fields['services'].help_text = u"Identify the services you need to support the patient's care."

        self.fields['skills'].label = u'5. Credentials / Professional Skills required'
        self.fields['skills'].help_text = u'Describe the credentials or professional skills you need the Caring Professional to have.'

        self.fields['locations'].label = u'6. Location'
        self.fields['locations'].help_text = u'Tell us the location of where you need the care.'

        self.fields['frequency'].label = u'7. Frequency'
        self.fields['frequency'].help_text = u'How often do you need care? At what time of day?'

        self.fields['street_address_1'].label = False
        self.fields['street_address_2'].label = False
        self.fields['city'].label = False
        self.fields['province'].label = False
        self.fields['postal_code'].label = False

        self.fields['time'].label = False

        self.fields['start_date'].label = u'Desired Start Date'

        self.fields['languages'].label = u'10. Language Requirements'
        self.fields['languages'].help_text = u'What Language(s) do you require the Caring Professional to speak?'

        self.fields['gender'].label = u'11. Gender Preferences'
        self.fields['gender'].help_text = u'Do you have a preference for the gender of the Caring Professional?'

        self.fields['criminal_check_required'].label = u'12. Police & Criminal Background'
        self.fields['criminal_check_required'].help_text = u'Do you require the Caring Professional to have a police and background check.'

        self.fields['evaluation_criteria'].label = u'13. Other Evaluation Criteria'
        self.fields['evaluation_criteria'].help_text = u"Is there any other evaluation criteria you'd like to include in selecting the right Caring Professional."

        self.fields['description'].label = u'14. Other Care Details'
        self.fields['description'].help_text = u"Are there any other details about the Care request you'd like to share with the Caring Professionals reading this RFC?"

        self.fields['deadline_to_respond'].label = u'15. Deadline to Respond'
        self.fields['deadline_to_respond'].help_text = u'When do you require responses to be submitted by.'

        self.helper = FormHelper()
        self.helper.form_class = 'form'
        self.helper.form_method = 'post'
        self.helper.field_template = 'requests_for_care/layout/help_text_above_field.html'  # Puts the help text before the field, following the label
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('patient', css_class='col-md-4'),
                    Div(
                        HTML('<a href={% url "patients-create" %}><span class="glyphicon glyphicon-plus"></span> Add new Patient Profile</a>'),
                        css_class='col-md-4',
                        style='margin-top: 68px;'  # HACK: Forcing the button alignment.
                    ),                             #       Consider a custom template if further layout changes are needed
                    css_class='row'
                ),
                Field(
                    'name',
                    placeholder='Create a name for this RFC. e.g., Nurse for Mom.',
                    template='requests_for_care/layout/help_text_above_field.html'
                ),
                'need',
                'services',
                'skills',
                InlineCheckboxes(
                    'locations',
                    template='requests_for_care/layout/help_text_above_checkboxselectmultiple_inline.html'
                ),
                Field(
                    'street_address_1',
                    placeholder='Street Address 1'
                ),
                Field(
                    'street_address_2',
                    placeholder='Street Address 2'
                ),
                Div(
                    Div(
                        Field('city',placeholder='City'),
                        css_class='col-md-5'
                    ),
                    Div(
                        Field('province', placeholder='Province'),
                        css_class='col-md-5'
                    ),
                    Div(
                        Field('postal_code', placeholder='Postal Code'),
                        css_class='col-md-2'
                    ),
                    css_class='row'
                ),
                PrependedText(
                    'frequency',
                    '<span class="glyphicon glyphicon-calendar"></span>',
                    placeholder='Daily / Weekly / Select Hours',
                    template='requests_for_care/layout/help_text_above_prepended_appended_text.html'
                ),
                PrependedText(
                    'time',
                    '<span class="glyphicon glyphicon-time"></span>',
                    placeholder='Daily / Weekly / Select Hours',
                ),
                HTML('<label class="control-label">8. Contract Duration</label>'),
                HTML('<div class="controls><p class="help-block">When would you like the care to begin and for how long?</p></div>'),
                Div(
                    Div(
                        PrependedText('start_date', '<span class="glyphicon glyphicon-calendar"></span>'),
                        css_class='col-md-4'
                    ),
                    Div(
                        PrependedText('end_date',  '<span class="glyphicon glyphicon-calendar"></span>'),
                        css_class='col-md-4'
                    ),
                    Div('open_ended', css_class='col-md-4', style='margin-top: 20px;'),
                    css_class='row'
                ),
                HTML('<label class="control-label">9. Set Pay Range</label>'),
                HTML('''
                    <div class="controls><p class="help-block">
                    Define the range of pay you are willing to offer for the position.
                    Note we have recommended a range based on the current pay standards
                    for the professionals you have requested. We recommend using the
                    broadest range possible.
                    </p></div>
                '''),
                Div(
                    Div(
                        PrependedAppendedText('min_pay', '$', '/hr'),
                        css_class='col-md-4'
                    ),
                    Div(
                        PrependedAppendedText('max_pay', '$', '/hr'),
                        css_class='col-md-4'
                    ),
                    css_class='row',
                    id='id_pay_range'
                ),
                'languages',
                InlineRadios(
                    'gender',
                    template='requests_for_care/layout/help_text_above_radioselect_inline.html'
                ),
                InlineRadios(
                    'criminal_check_required',
                    template='requests_for_care/layout/help_text_above_radioselect_inline.html'
                ),
                Field(
                    'evaluation_criteria',
                    placeholder='Describe any other evaluation criteria',
                    template='requests_for_care/layout/help_text_above_field.html'
                ),
                Field(
                    'description',
                    placeholder='Describe how a caring professional can help',
                    template='requests_for_care/layout/help_text_above_field.html'
                ),
                PrependedText(
                    'deadline_to_respond',
                    '<i class="glyphicon glyphicon-calendar"></i>',
                    template='requests_for_care/layout/help_text_above_prepended_appended_text.html'
                )
            ),
            FormActions(
                Submit('_publish', 'Continue'),
                Submit('_draft', 'Save & Post Later')
            )
        )


class RequestForCarePublishForm(forms.Form):
    all_caring_professionals = forms.BooleanField(label='Include all on watch list', required=False)
    caring_professionals = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')

        super(RequestForCarePublishForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                '',
                HTML('<p>Send to full e-advocate Community?</p>'),
                Submit('_all', 'Get Started'),
                HTML('<p>OR</p>'),
                HTML('<p>Send to only to CP\'s On My Watch List?</p>'),
                Div('all_caring_professionals', css_class='pull-right'),
                Field('caring_professionals', template='requests_for_care/watch_list.html'),
                Submit('_watched', 'Specified Watch List')
            )
        )

        if hasattr(user, 'watch_list'):
            self.fields['caring_professionals'].queryset = user.watch_list.watched_users.all()


class RequestForCareProposalForm(forms.ModelForm):
    services = forms.ChoiceField(
        label=u'Services Needed',
        help_text=u'Do you provide these services?',
        required=False,
        choices=((True, 'Yes'), (False, 'No')),
        widget=forms.RadioSelect
    )
    skills = forms.ChoiceField(
        label=u'Professional Skills / Credentials',
        help_text=u'Do you have these credentials?',
        required=False,
        choices=((True, 'Yes'), (False, 'No')),
        widget=forms.RadioSelect
    )
    locations = forms.ChoiceField(
        label=u'Location',
        help_text=u'Can you offer care at this location?',
        required=False,
        choices=((True, 'Yes'), (False, 'No')),
        widget=forms.RadioSelect
    )
    frequency = forms.ChoiceField(
        label=u'Frequency',
        help_text=u'Are you available at these times?',
        required=False,
        choices=((True, 'Yes'), (False, 'No')),
        widget=forms.RadioSelect
    )
    duration = forms.ChoiceField(
        label=u'Contract Duration',
        help_text=u'Are you available for these dates?',
        required=False,
        choices=((True, 'Yes'), (False, 'No')),
        widget=forms.RadioSelect
    )
    pay_range = forms.CharField(
        label=u'Pay Range Desired',
        help_text=u'What is the hourly rate you are willing to work for?',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'State your rate'})
    )
    languages = forms.ChoiceField(
        label=u'Language',
        help_text=u'Do you speak these languages?',
        required=False,
        choices=((True, 'Yes'), (False, 'No')),
        widget=forms.RadioSelect
    )
    criminal_check_required = forms.ChoiceField(
        label=u'Police and Criminal Background',
        help_text=u'Are you able to provide the appropriate documents to meet this request?',
        required=False,
        choices=((True, 'Yes'), (False, 'No')),
        widget=forms.RadioSelect
    )
    evaluation_criteria = forms.CharField(
        label=u'Other Evaluation Criteria',
        help_text=u'Respond to this request.',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': u'Add Response'})
    )
    description = forms.CharField(
        label=u'Other Care Details',
        help_text=u'Respond to this request.',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': u'Add Response'})
    )
    extra = forms.CharField(
        label=None,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': u'Add Response'})
    )

    class Meta:
        model = RequestForCareProposal
        fields = (
            'services',
            'skills',
            'locations',
            'frequency',
            'duration',
            'pay_range',
            'languages',
            'criminal_check_required',
            'evaluation_criteria',
            'description',
            'extra'
        )


class RequestForCareReviewFilterForm(forms.Form):
    ORDER_BY_CHOICES = (
        ('user__first_name', 'Name'),
        ('submitted', 'Response Date'),
        ('accepted', 'Shortlist'),
        ('pay_range', 'Pay - Lowest to Highest')
    )

    request_for_care = forms.ChoiceField(required=True)
    order_by = forms.ChoiceField(choices=ORDER_BY_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super(RequestForCareReviewFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.form_id = 'id_rfc_filter'
        self.helper.layout = Layout(
            'request_for_care',
            'order_by'
        )
