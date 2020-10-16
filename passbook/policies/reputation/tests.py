"""test reputation signals and policy"""
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.test import TestCase

from passbook.core.models import User
from passbook.policies.reputation.models import (
    CACHE_KEY_IP_PREFIX,
    CACHE_KEY_USER_PREFIX,
    IPReputation,
    ReputationPolicy,
    UserReputation,
)
from passbook.policies.reputation.tasks import save_ip_reputation, save_user_reputation
from passbook.policies.types import PolicyRequest


class TestReputationPolicy(TestCase):
    """test reputation signals and policy"""

    def setUp(self):
        self.test_ip = "255.255.255.255"
        self.test_username = "test"
        cache.delete(CACHE_KEY_IP_PREFIX + self.test_ip)
        cache.delete(CACHE_KEY_USER_PREFIX + self.test_username)
        # We need a user for the one-to-one in userreputation
        self.user = User.objects.create(username=self.test_username)

    def test_ip_reputation(self):
        """test IP reputation"""
        # Trigger negative reputation
        authenticate(None, username=self.test_username, password=self.test_username)
        # Test value in cache
        self.assertEqual(cache.get(CACHE_KEY_IP_PREFIX + self.test_ip), -1)
        # Save cache and check db values
        save_ip_reputation.delay().get()
        self.assertEqual(IPReputation.objects.get(ip=self.test_ip).score, -1)

    def test_user_reputation(self):
        """test User reputation"""
        # Trigger negative reputation
        authenticate(None, username=self.test_username, password=self.test_username)
        # Test value in cache
        self.assertEqual(cache.get(CACHE_KEY_USER_PREFIX + self.test_username), -1)
        # Save cache and check db values
        save_user_reputation.delay().get()
        self.assertEqual(UserReputation.objects.get(user=self.user).score, -1)

    def test_policy(self):
        """Test Policy"""
        request = PolicyRequest(user=self.user)
        policy: ReputationPolicy = ReputationPolicy.objects.create(
            name="reputation-test", threshold=0
        )
        self.assertTrue(policy.passes(request).passing)
