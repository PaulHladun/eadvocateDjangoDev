from django.conf.urls import patterns, url

from .views import (
    RequestForCareCreate, RequestForCareCancel, RequestForCareDetail,
    RequestForCareList, RequestForCareReview, RequestForCareProposalAccept,
    RequestForCareProposalContract, RequestForCareProposalDetail, RequestForCareProposalReject,
    RequestForCareProposalUpdate, RequestForCarePublish, RequestForCareUpdate
)


urlpatterns = patterns('',
    url(
        r'^create/$',
        RequestForCareCreate.as_view(),
        name='requests_for_care-create'
    ),
    url(
        r'^draft/$',
        RequestForCareList.as_view(draft_only=True),
        name='requests_for_care-list_draft_only'
    ),
    url(
        r'^(?P<pk>\d+)/publish/$',
        RequestForCarePublish.as_view(),
        name='requests_for_care-publish'
    ),
    url(
        r'^(?P<pk>\d+)/edit/$',
        RequestForCareUpdate.as_view(),
        name='requests_for_care-update'
    ),
    url(
        r'^(?P<pk>\d+)/cancel/$',
        RequestForCareCancel.as_view(),
        name='requests_for_care-cancel'
    ),
    url(
        r'^(?P<pk>\d+)/review/all/$',
        RequestForCareReview.as_view(),
        name='requests_for_care-review_all'
    ),
    url(
        r'^(?P<pk>\d+)/review/short-list/$',
        RequestForCareReview.as_view(short_list=True),
        name='requests_for_care-review_short_list'
    ),
    url(
        r'^(?P<pk>\d+)/$',
        RequestForCareDetail.as_view(),
        name='requests_for_care-detail'
    ),
    url(
        r'^(?P<pk>\d+)/proposal/$',
        RequestForCareProposalUpdate.as_view(),
        name='requests_for_care-proposal_update'
    ),
    url(
        r'^(?P<rfc_pk>\d+)/proposal/(?P<pk>\d+)$',
        RequestForCareProposalDetail.as_view(),
        name='requests_for_care-proposal_detail'
    ),
    url(
        r'^(?P<rfc_pk>\d+)/proposal/(?P<pk>\d+)/accept/$',
        RequestForCareProposalAccept.as_view(),
        name='requests_for_care-accept'
    ),
    url(
        r'^(?P<rfc_pk>\d+)/proposal/(?P<pk>\d+)/reject/$',
        RequestForCareProposalReject.as_view(),
        name='requests_for_care-reject'
    ),
    url(
        r'^(?P<rfc_pk>\d+)/proposal/(?P<pk>\d+)/contract/$',
        RequestForCareProposalContract.as_view(),
        name='requests_for_care-contract'
    ),
    url(
        r'^$',
        RequestForCareList.as_view(),
        name='requests_for_care-list'
    ),
)
