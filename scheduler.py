from apscheduler.schedulers.background import BackgroundScheduler
from app import create_app
from app.tasks.scheduled_tasks import sync_accounts, last_connection

# Fichier qui permet de lancer les tâches planifiées (sync_accounts et last_connection) à intervalle régulier,
# en utilisant le module APScheduler en arrrière-plan

# Init app
app = create_app()
app.app_context().push()

# Init scheduler
scheduler = BackgroundScheduler()

# Ajout des tâches planifiées
scheduler.add_job(sync_accounts, 'cron', minute='*/15', kwargs={'app': app})
scheduler.add_job(last_connection, 'cron', hour='*', kwargs={'app': app})

# Lancement du scheduler
scheduler.start()
print("Scheduler started!")

# Maintenir le processus en vie
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
