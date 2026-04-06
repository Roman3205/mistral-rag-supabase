from supabase import create_async_client, AsyncClient
from dotenv import load_dotenv
from os import getenv

load_dotenv()

supabase: AsyncClient | None = None

async def init_db():
    global supabase

    supabase = await create_async_client(supabase_key=getenv('SUPABASE_SECRET_KEY'), supabase_url=getenv('SUPABASE_URL'))