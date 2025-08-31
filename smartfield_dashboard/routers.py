class ODKXReadOnlyRouter:
    """
    No-op router. Everything uses 'default'.
    Safe drop-in to satisfy DATABASE_ROUTERS without changing behavior.
    """
    def db_for_read(self, model, **hints): return None
    def db_for_write(self, model, **hints): return None
    def allow_relation(self, obj1, obj2, **hints): return True
    def allow_migrate(self, db, app_label, model_name=None, **hints): return True
