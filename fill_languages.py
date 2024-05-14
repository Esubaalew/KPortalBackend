import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KPortalBackend.settings")
django.setup()

from portal.models import Language, Follow
import random
from faker import Faker
from django.utils import timezone
from datetime import timedelta

fake = Faker()

import random
from django.utils import timezone
from portal.models import Resource, CustomUser, Like


def populate_random_follows(num_follows):
    # Get all users
    users = CustomUser.objects.all()

    # Calculate the total number of users
    num_users = len(users)

    # Iterate to create random follows
    for _ in range(num_follows):
        # Randomly select a follower and a followed user
        random_follower = random.choice(users)
        random_followed_user = random.choice(users.exclude(id=random_follower.id))

        # Check if the follow already exists
        if not Follow.objects.filter(follower=random_follower, followed_user=random_followed_user).exists():
            # Create a follow object
            follow = Follow.objects.create(
                follower=random_follower,
                followed_user=random_followed_user,
                date_followed=timezone.now()
            )
            # Optionally, you can print the created follow object
            print(f"Created follow: {follow}")

# Example usage: Populate 100 random follows
# populate_random_follows(100)
