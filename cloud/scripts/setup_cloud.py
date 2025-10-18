#!/usr/bin/env python3
"""
SentinelDF Cloud Setup Script

Automates:
- Database initialization
- Redis configuration
- S3 bucket setup
- Initial admin user creation
"""
import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "S3_BUCKET",
        "AWS_REGION"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nSet them in your environment or .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True

def init_database():
    """Initialize database tables."""
    print("\n📦 Initializing database...")
    
    try:
        from cloud.config.database import init_db, get_db_context
        from cloud.config.database import Organization, User, APIKey
        
        # Create tables
        init_db()
        print("✅ Database tables created")
        
        # Create default organization
        with get_db_context() as db:
            # Check if default org exists
            org = db.query(Organization).filter_by(id="org_default").first()
            if not org:
                org = Organization(
                    id="org_default",
                    name="Default Organization",
                    plan="free",
                    quota_monthly=1000
                )
                db.add(org)
                print("✅ Default organization created")
            else:
                print("ℹ️  Default organization already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_redis():
    """Test Redis connection."""
    print("\n🔴 Testing Redis connection...")
    
    try:
        from cloud.config.cache import health_check
        
        result = health_check()
        
        if result["status"] == "healthy":
            print("✅ Redis connection successful")
            print(f"   Cache keys: {result.get('total_keys', 0)}")
            return True
        else:
            print(f"❌ Redis unhealthy: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_s3():
    """Test S3 connection."""
    print("\n☁️  Testing S3 connection...")
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        bucket = os.getenv("S3_BUCKET")
        region = os.getenv("AWS_REGION", "us-east-1")
        
        s3 = boto3.client('s3', region_name=region)
        
        # Try to list objects (should fail if bucket doesn't exist)
        try:
            s3.head_bucket(Bucket=bucket)
            print(f"✅ S3 bucket '{bucket}' exists and is accessible")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"ℹ️  Bucket '{bucket}' doesn't exist. Creating...")
                try:
                    s3.create_bucket(
                        Bucket=bucket,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                    print(f"✅ S3 bucket '{bucket}' created")
                    return True
                except Exception as create_error:
                    print(f"❌ Failed to create bucket: {create_error}")
                    return False
            else:
                print(f"❌ S3 access error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ S3 test failed: {e}")
        print("ℹ️  S3 is optional for initial setup")
        return False

def create_admin_user(email: str):
    """Create admin user with API key."""
    print(f"\n👤 Creating admin user: {email}")
    
    try:
        from cloud.config.database import get_db_context, User, APIKey, Organization
        import secrets
        import bcrypt
        
        with get_db_context() as db:
            # Check if user exists
            user = db.query(User).filter_by(email=email).first()
            
            if user:
                print(f"ℹ️  User {email} already exists")
                user_id = user.id
            else:
                # Create user
                user_id = f"user_{secrets.token_hex(8)}"
                user = User(
                    id=user_id,
                    org_id="org_default",
                    email=email
                )
                db.add(user)
                print(f"✅ User created with ID: {user_id}")
            
            # Create API key
            api_key = f"sk_live_{secrets.token_urlsafe(32)}"
            key_hash = bcrypt.hashpw(api_key.encode(), bcrypt.gensalt()).decode()
            
            api_key_obj = APIKey(
                key_hash=key_hash,
                key_prefix=api_key[:15] + "...",
                user_id=user_id,
                org_id="org_default",
                name="Admin Key",
                scopes=["scan", "mbom", "admin"]
            )
            db.add(api_key_obj)
            
            db.commit()
            
            print("✅ API key created")
            print(f"\n{'='*60}")
            print(f"🔑 SAVE THIS API KEY (shown only once):")
            print(f"   {api_key}")
            print(f"{'='*60}\n")
            
            return True
            
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return False

def run_health_checks():
    """Run comprehensive health checks."""
    print("\n🏥 Running health checks...")
    
    checks = {
        "Database": init_database,
        "Redis": test_redis,
        "S3": test_s3
    }
    
    results = {}
    for name, check_func in checks.items():
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            results[name] = False
    
    print("\n📊 Health Check Summary:")
    for name, status in results.items():
        status_emoji = "✅" if status else "❌"
        print(f"   {status_emoji} {name}")
    
    return all(results.values())

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup SentinelDF Cloud")
    parser.add_argument("--admin-email", help="Admin user email")
    parser.add_argument("--skip-checks", action="store_true", help="Skip health checks")
    parser.add_argument("--db-only", action="store_true", help="Only initialize database")
    
    args = parser.parse_args()
    
    print("🚀 SentinelDF Cloud Setup")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Run setup
    if args.db_only:
        success = init_database()
    elif args.skip_checks:
        success = init_database()
        if args.admin_email:
            create_admin_user(args.admin_email)
    else:
        success = run_health_checks()
        if success and args.admin_email:
            create_admin_user(args.admin_email)
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Deploy Control Plane API to Render")
        print("   2. Deploy Data Plane Workers to Render")
        print("   3. Configure auto-scaling")
        print("   4. Set up monitoring")
        print("\n📖 See DEPLOYMENT_GUIDE.md for details")
    else:
        print("\n❌ Setup encountered errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
