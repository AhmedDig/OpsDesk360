import psycopg2
import secrets
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth.hashers import make_password

def create_tenant_database(db_name):
    """Create a new PostgreSQL database and run core migrations."""
    default = settings.DATABASES['default']
    # Connect to 'postgres' database to create the new DB
    conn = psycopg2.connect(
        dbname='postgres',
        user=default['USER'],
        password=default['PASSWORD'],
        host=default['HOST'],
        port=default.get('PORT', '5432')
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE {db_name} OWNER {default['USER']}")
    cursor.close()
    conn.close()

    # Dynamically add the new database connection
    settings.DATABASES[db_name] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,
        'USER': default['USER'],
        'PASSWORD': default['PASSWORD'],
        'HOST': default['HOST'],
        'PORT': default.get('PORT', '5432'),
    }

    # Run migrations on the new database
    call_command('migrate', database=db_name, verbosity=0)

def create_default_admin(db_name, username='admin'):
    """Create a default superuser in the client's database. Returns the generated password."""
    from core.models import User
    password = secrets.token_urlsafe(12)
    User.objects.using(db_name).create_superuser(
        username=username,
        email=f'{username}@{db_name}.local',
        password=password
    )
    return password