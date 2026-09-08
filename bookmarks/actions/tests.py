from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from actions.models import Action
from actions.utils import create_action

User = get_user_model()


class ActionActivityStreamTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='dan',
            email='dan@example.com',
            password='TestPassword123!'
        )
        self.user2 = User.objects.create_user(
            username='eva',
            email='eva@example.com',
            password='TestPassword123!'
        )

    def test_create_action_with_target(self):
        result = create_action(self.user1, 'is following', self.user2)
        self.assertTrue(result)
        self.assertEqual(Action.objects.count(), 1)
        action = Action.objects.first()
        self.assertEqual(action.user, self.user1)
        self.assertEqual(action.verb, 'is following')
        self.assertEqual(action.target, self.user2)

    def test_duplicate_action_throttled_within_60_seconds(self):
        # First action succeeds
        first = create_action(self.user1, 'bookmarked image')
        self.assertTrue(first)
        self.assertEqual(Action.objects.count(), 1)

        # Immediate duplicate action is blocked / throttled
        duplicate = create_action(self.user1, 'bookmarked image')
        self.assertFalse(duplicate)
        self.assertEqual(Action.objects.count(), 1)

    def test_dashboard_shows_followed_users_actions(self):
        # User 1 follows User 2
        self.user1.following.add(self.user2)

        # User 2 performs an action
        create_action(self.user2, 'shared a photo')

        # User 1 logs in and views dashboard
        self.client.login(username='dan', password='TestPassword123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'shared a photo')
        self.assertContains(response, 'eva')
