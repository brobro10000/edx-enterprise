"""
Tests for enterprise.filters.support pipeline steps.
"""
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from enterprise.filters.support import SupportContactEnterpriseTagStep
from test_utils.factories import UserFactory

CONTACT_FILTER_TYPE = "org.openedx.learning.support.contact.context.requested.v1"


class TestSupportContactEnterpriseTagStep(TestCase):
    """
    Tests for SupportContactEnterpriseTagStep pipeline step.
    """

    def _make_step(self):
        return SupportContactEnterpriseTagStep(CONTACT_FILTER_TYPE, [])

    def _make_request(self):
        return RequestFactory().get('/')

    @patch('enterprise.filters.support.enterprise_customer_for_request')
    @patch('enterprise.filters.support.get_current_request')
    def test_appends_tag_for_linked_customer_request(self, mock_get_current_request, mock_customer_for_request):
        """
        When the request is associated with a linked customer account, 'enterprise_learner'
        is appended to the tags list.
        """
        mock_customer_for_request.return_value = {'uuid': 'some-uuid', 'name': 'Test Customer'}
        request = self._make_request()
        mock_get_current_request.return_value = request
        user = UserFactory()
        tags = ['some_tag']

        step = self._make_step()
        result = step.run_filter(tags=tags, user=user)

        assert result['tags'] == ['some_tag', 'enterprise_learner']
        assert result['user'] is user
        mock_customer_for_request.assert_called_once_with(request)

    @patch('enterprise.filters.support.enterprise_customer_for_request')
    @patch('enterprise.filters.support.get_current_request')
    def test_does_not_duplicate_tag(self, mock_get_current_request, mock_customer_for_request):
        """
        When 'enterprise_learner' is already in the tags list, it is not duplicated.
        """
        mock_customer_for_request.return_value = {'uuid': 'some-uuid', 'name': 'Test Customer'}
        mock_get_current_request.return_value = self._make_request()
        user = UserFactory()
        tags = ['enterprise_learner']

        step = self._make_step()
        result = step.run_filter(tags=tags, user=user)

        assert result['tags'].count('enterprise_learner') == 1

    @patch('enterprise.filters.support.enterprise_customer_for_request')
    @patch('enterprise.filters.support.get_current_request')
    def test_does_not_append_tag_for_unlinked_request(self, mock_get_current_request, mock_customer_for_request):
        """
        When the request is not associated with a linked customer account, tags are unchanged.
        """
        mock_customer_for_request.return_value = None
        mock_get_current_request.return_value = self._make_request()
        user = UserFactory()
        tags = ['some_tag']

        step = self._make_step()
        result = step.run_filter(tags=tags, user=user)

        assert result['tags'] == ['some_tag']
