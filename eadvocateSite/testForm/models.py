from django.db import models

import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from django_extensions.db.models import TimeStampedModel

from contact_info.models import AddressMixin
from conversations.models import ConversationMixin
from languages.models import Language
from locations.models import Location
from needs.models import Need
from patients.models import Patient
from services.models import Service
from skills.models import Skill


class RequestForCareBase(TimeStampedModel, AddressMixin):
    client = models.ForeignKey(User, verbose_name='Client', related_name='%(class)s')
    patient = models.ForeignKey(Patient, verbose_name='Patient', related_name='%(class)s')
    name = models.CharField('Name', max_length=255)
    description = models.TextField('description')
    need = models.ForeignKey(Need, verbose_name='Need Area', null=True, related_name='%(class)s')
    services = models.ManyToManyField(
        Service, verbose_name='Services', null=True, related_name='%(class)s'
    )
    skills = models.ManyToManyField(
        Skill, verbose_name='Skills', null=True, related_name='%(class)s'
    )
    locations = models.ManyToManyField(
        Location, verbose_name='Locations', related_name='%(class)s'
    )
    start_date = models.DateField('Start Date')
    end_date = models.DateField('End Date', null=True, blank=True)
    frequency = models.CharField('Frequency', max_length=100)
    time = models.TimeField('Time', null=True)
    languages = models.ManyToManyField(Language, verbose_name='Language', related_name='%(class)s')
    gender = models.CharField('Gender', max_length=1, choices=settings.GENDER_CHOICES, default=settings.GENDER_NONE)

    class Meta:
        abstract = True


class RequestForCare(RequestForCareBase):
    min_pay = models.FloatField('Minimum Pay')
    max_pay = models.FloatField('Maximum Pay')
    deadline_to_respond = models.DateField('Deadline to Respond')
    evaluation_criteria = models.TextField('Evaluation Criteria')
    criminal_check_required = models.BooleanField('Criminal Check Required', choices=((True, 'Yes'), (False, 'No')))

    class Meta:
        verbose_name = 'Request For Care'
        verbose_name_plural = 'Requests For Care'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(RequestForCare, self).save(*args, **kwargs)

        if not self.statuses.exists():
            RequestForCareStatus.objects.create(
                request_for_care=self, status=RequestForCareStatus.STATUS_DRAFT
            )

    @models.permalink
    def get_absolute_url(self):
        return ('requests_for_care-detail', (), {
            'pk': self.pk
        })

    @property
    def current_status(self):
        try:
            return self.statuses.latest('created').status
        except RequestForCareStatus.DoesNotExist:
            return None

    def get_current_status_display(self):
        try:
            return self.statuses.latest('created').get_status_display()
        except RequestForCareStatus.DoesNotExist:
            return ''

    @property
    def is_editable(self):
        if self.current_status == RequestForCareStatus.STATUS_DRAFT:
            return True

        return False

    @property
    def is_published(self):
        if self.current_status in (RequestForCareStatus.STATUS_PUBLIC, RequestForCareStatus.STATUS_PRIVATE):
            return True

        return False

    @property
    def is_publishable(self):
        if self.current_status in (
            RequestForCareStatus.STATUS_PUBLIC,
            RequestForCareStatus.STATUS_PRIVATE,
            RequestForCareStatus.STATUS_CANCELLED
        ):
            return False

        return True

    @property
    def is_cancelable(self):
        if self.current_status in (
            RequestForCareStatus.STATUS_PUBLIC,
            RequestForCareStatus.STATUS_PRIVATE,
            RequestForCareStatus.STATUS_DRAFT
        ) and self.deadline_to_respond > datetime.date.today():
            return True

        return False


class RequestForCareProposalManager(models.Manager):
    def submitted(self):
        return self.get_query_set().exclude(submitted__isnull=True)

    def accepted(self):
        return self.get_query_set().filter(accepted=True)


class RequestForCareProposal(TimeStampedModel, ConversationMixin):
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_UNKNOWN = 'unknown'

    STATUS_CHOICES = (
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_UNKNOWN, 'Unknown')
    )

    request_for_care = models.ForeignKey(
        RequestForCare, verbose_name='Request for Care', related_name='proposals'
    )
    user = models.ForeignKey(User, verbose_name='User')
    rating = models.CharField('Rating', max_length=10, blank=True)
    active = models.BooleanField('Active')
    submitted = models.DateTimeField('Submitted', null=True)
    viewed = models.BooleanField('Viewed')
    status = models.CharField('Status', max_length=8, choices=STATUS_CHOICES, default=STATUS_UNKNOWN)

    services = models.NullBooleanField('Services', null=True)
    skills = models.NullBooleanField('Skills', null=True)
    location = models.NullBooleanField('Location', null=True)
    frequency = models.NullBooleanField('Frequency', null=True)
    duration = models.NullBooleanField('Duration', null=True)
    pay_range = models.CharField('Pay Range', max_length=20)
    language = models.NullBooleanField('Language', null=True)
    criminal_check_required = models.NullBooleanField('Criminal Check Required', null=True)
    evaluation_criteria = models.TextField('Evaluation Criteria', blank=True)
    description = models.TextField('Description', blank=True)
    extra = models.TextField('Extra', blank=True)

    objects = RequestForCareProposalManager()

    class Meta:
        verbose_name = 'Request For Care Proposal'
        verbose_name_plural = 'Request For Care Proposals'

    def __unicode__(self):
        return u'%s: %s' % (self.request_for_care.name, self.user.get_full_name())

    @models.permalink
    def get_absolute_url(self):
        return ('requests_for_care-proposal_detail', (), {
            'rfc_pk': self.request_for_care.pk, 'pk': self.pk
        })

    @property
    def current_status(self):
        return self.statuses.latest('created').status

    def get_current_status_display(self):
        return self.statuses.latest('created').get_status_display()


class RequestForCareStatus(TimeStampedModel):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLIC = 'public'
    STATUS_PRIVATE = 'private'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLIC, 'Public'),
        (STATUS_PRIVATE, 'Private'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    request_for_care = models.ForeignKey(RequestForCare, verbose_name='Request for Care', related_name='statuses')
    status = models.CharField('Status', max_length=16, choices=STATUS_CHOICES)

    class Meta:
        verbose_name = 'Request For Care Status'
        verbose_name_plural = 'Request For Care Statuses'
        unique_together = ('request_for_care', 'status')

    def __unicode__(self):
        return u'%s: %s at %s' % (self.request_for_care.name, self.get_status_display(), self.created)

