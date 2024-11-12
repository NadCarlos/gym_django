from django.core.management import call_command


def daily_database_backup():
    try:
        call_command("dbbackup")
    except:
        pass
