import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KPortalBackend.settings")
django.setup()

from portal.models import Language
import random
from faker import Faker
from django.utils import timezone
from datetime import timedelta

fake = Faker()

import random
from django.utils import timezone
from portal.models import Resource, CustomUser, Like


def populate_random_likes(num_likes):
    # Get all resources and users
    resources = Resource.objects.all()
    users = CustomUser.objects.all()

    # Calculate the total number of resources and users
    num_resources = len(resources)
    num_users = len(users)

    # Iterate to create random likes
    for _ in range(num_likes):
        # Randomly select a resource and user
        random_resource = random.choice(resources)
        random_user = random.choice(users)

        # Check if the user has already liked the resource
        if not Like.objects.filter(resource=random_resource, user=random_user).exists():
            # Create a like object
            like = Like.objects.create(
                resource=random_resource,
                user=random_user,
                date_liked=timezone.now()
            )
            # Optionally, you can print the created like object
            print(f"Created like: {like}")


# Example usage: Populate 100 random likes
# populate_random_likes(50)
