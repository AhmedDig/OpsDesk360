from django.db import connections
from django.core.management import call_command
from django.conf import settings

def create_tenant_database(db_name, db_user=settings.DATABASES['default']['USER'], db_password=settings.DATABASES['default']['PASSWORD'], db_host=settings.DATABASES['default']['HOST']):
    """Creates a new PostgreSQL database and runs migrations."""
    import psycopg2
    # Connect to default 'postgres' database to create new DB
    conn = psycopg2.connect(
        dbname='postgres',
        user=db_user,
        password=db_password,
        host=db_host
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE {db_name}")
    cursor.close()
    conn.close()

    # Add a new connection in Django settings dynamically (or use a separate DB router)
    settings.DATABASES[db_name] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,
        'USER': db_user,
        'PASSWORD': db_password,
        'HOST': db_host,
        'PORT': '5432',
    }
    # Run migrations using the new connection alias
    call_command('migrate', database=db_name)