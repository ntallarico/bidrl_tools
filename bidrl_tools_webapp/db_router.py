# A router to control all database operations on models in the application to use the 'bidrl_db'.
class AppDBRouter:
    def db_for_read(self, model, **hints):
        # Attempts to read models go to bidrl_db.
        return 'bidrl_db'

    def db_for_write(self, model, **hints):
        # Attempts to write models go to bidrl_db.
        return 'bidrl_db'

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations if a model in the app is involved.
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Ensure that the app's models get created on the right database.
        if app_label == 'auto_bid':
            return db == 'bidrl_db'
        return db == 'default'