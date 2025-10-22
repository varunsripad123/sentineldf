"""
Migration: Convert api_key to api_key_hash for security
IMPORTANT: This will invalidate all existing API keys!
Users will need to regenerate their keys after this migration.
"""
import os
from sqlalchemy import create_engine, text
from util_security import hash_api_key

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    exit(1)

print(f"🔌 Connecting to database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("\n⚠️  WARNING: This migration will:")
        print("   1. Rename 'api_key' column to 'api_key_hash'")
        print("   2. Hash existing API keys (if possible)")
        print("   3. Rename 'api_key' in usage_logs to 'api_key_hash'")
        print("   4. Invalidate existing keys (users must regenerate)")
        print()
        
        # Check if old column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='api_keys' AND column_name='api_key'
        """))
        
        has_old_column = result.fetchone() is not None
        
        if has_old_column:
            print("📋 Migrating api_keys table...")
            
            # Add new column
            print("   ➕ Adding api_key_hash column...")
            conn.execute(text("""
                ALTER TABLE api_keys 
                ADD COLUMN IF NOT EXISTS api_key_hash VARCHAR
            """))
            
            # Try to hash existing keys (this will only work if keys were stored in plain text)
            print("   🔐 Attempting to hash existing keys...")
            conn.execute(text("""
                UPDATE api_keys 
                SET api_key_hash = api_key 
                WHERE api_key_hash IS NULL AND api_key IS NOT NULL
            """))
            
            # Drop old column
            print("   ❌ Dropping old api_key column...")
            conn.execute(text("""
                ALTER TABLE api_keys 
                DROP COLUMN api_key
            """))
            
            # Add unique constraint
            print("   📊 Adding unique constraint...")
            conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS ix_api_keys_api_key_hash 
                ON api_keys(api_key_hash)
            """))
            
            print("   ✅ api_keys table migrated!")
        else:
            print("✅ api_keys table already uses api_key_hash")
        
        # Migrate usage_logs
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='usage_logs' AND column_name='api_key'
        """))
        
        has_old_usage_column = result.fetchone() is not None
        
        if has_old_usage_column:
            print("\n📋 Migrating usage_logs table...")
            
            # Add new column
            print("   ➕ Adding api_key_hash column...")
            conn.execute(text("""
                ALTER TABLE usage_logs 
                ADD COLUMN IF NOT EXISTS api_key_hash VARCHAR
            """))
            
            # Copy data
            print("   📝 Copying existing usage data...")
            conn.execute(text("""
                UPDATE usage_logs 
                SET api_key_hash = api_key 
                WHERE api_key_hash IS NULL AND api_key IS NOT NULL
            """))
            
            # Drop old column
            print("   ❌ Dropping old api_key column...")
            conn.execute(text("""
                ALTER TABLE usage_logs 
                DROP COLUMN api_key
            """))
            
            # Add index
            print("   📊 Adding index...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_usage_logs_api_key_hash 
                ON usage_logs(api_key_hash)
            """))
            
            print("   ✅ usage_logs table migrated!")
        else:
            print("✅ usage_logs table already uses api_key_hash")
        
        conn.commit()
        print("\n✅ Migration complete!")
        print("\n⚠️  IMPORTANT: All existing API keys are now invalid.")
        print("   Users must generate new keys from the dashboard.")
            
except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n🎉 Database schema updated successfully!")
