from config import settings

print(settings.get_db_url())
# → sqlite+aiosqlite:///./database.db
