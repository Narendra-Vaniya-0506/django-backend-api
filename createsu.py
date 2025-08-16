# createsu.py

import os
import django

# !!! IMPORTANT: Change 'myyoutubebackendd.settings' to your project's settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myyoutubebackendd.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# --- Your Superuser Details ---
USERNAME = 'Narendra'
EMAIL = 'narendravaniya99@gmail.com'
# !!! IMPORTANT: Change this password to something secure!
PASSWORD = 'CodeYatra@0605' 
# --------------------------

if not User.objects.filter(username=USERNAME).exists():
    print(f"Creating a new superuser: {USERNAME}")
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
else:
    print(f"Superuser {USERNAME} already exists. Changing password.")
    user = User.objects.get(username=USERNAME)
    user.set_password(PASSWORD)
    user.save()

print("Superuser is ready.")