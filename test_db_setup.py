#!/usr/bin/env python3
"""
Test script to verify database setup for PR Campaign System.
This script tests both main and test database connectivity.
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Load environment variables
load_dotenv()

async def test_database_connection(db_url: str, db_name: str) -> bool:
    """Test connection to a specific database."""
    try:
        print(f"\n🔍 Testing {db_name} database connection...")
        print(f"   URL: {db_url.replace('postgres:postgres', 'postgres:***')}")
        
        # Create async engine
        engine = create_async_engine(db_url, echo=False)
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"   ✅ Connected! PostgreSQL version: {version[:50]}...")
            
            # Check if our extensions are installed
            result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm')"))
            extensions = [row[0] for row in result.fetchall()]
            print(f"   ✅ Extensions installed: {extensions}")
            
            # Test basic operations
            await conn.execute(text("CREATE TABLE IF NOT EXISTS test_connection (id SERIAL PRIMARY KEY, created_at TIMESTAMP DEFAULT NOW())"))
            await conn.execute(text("INSERT INTO test_connection DEFAULT VALUES"))
            result = await conn.execute(text("SELECT COUNT(*) FROM test_connection"))
            count = result.scalar()
            print(f"   ✅ Test table operations successful (records: {count})")
            
            # Cleanup
            await conn.execute(text("DROP TABLE IF EXISTS test_connection"))
        
        await engine.dispose()
        print(f"   ✅ {db_name} database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ {db_name} database test failed: {e}")
        return False

async def test_redis_connection() -> bool:
    """Test Redis connection."""
    try:
        import redis.asyncio as redis
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        print(f"\n🔍 Testing Redis connection...")
        print(f"   URL: {redis_url}")
        
        redis_client = redis.from_url(redis_url)
        
        # Test basic operations
        await redis_client.set("test_key", "test_value")
        value = await redis_client.get("test_key")
        await redis_client.delete("test_key")
        
        info = await redis_client.info()
        print(f"   ✅ Redis connected! Version: {info.get('redis_version', 'unknown')}")
        
        await redis_client.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Redis test failed: {e}")
        return False

async def test_elasticsearch_connection() -> bool:
    """Test Elasticsearch connection."""
    try:
        import aiohttp
        
        es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        print(f"\n🔍 Testing Elasticsearch connection...")
        print(f"   URL: {es_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{es_url}/_cluster/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Elasticsearch connected! Status: {data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"   ❌ Elasticsearch returned status: {response.status}")
                    return False
        
    except Exception as e:
        print(f"   ❌ Elasticsearch test failed: {e}")
        return False

async def main():
    """Run all database and service connectivity tests."""
    print("🧪 PR Campaign System - Database & Services Test")
    print("=" * 60)
    
    # Test databases
    main_db_url = os.getenv("DATABASE_URL")
    test_db_url = os.getenv("TEST_DATABASE_URL")
    
    if not main_db_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    if not test_db_url:
        print("❌ TEST_DATABASE_URL not found in environment")
        return
    
    # Run tests
    results = []
    results.append(await test_database_connection(main_db_url, "Main"))
    results.append(await test_database_connection(test_db_url, "Test"))
    results.append(await test_redis_connection())
    results.append(await test_elasticsearch_connection())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    services = ["Main Database", "Test Database", "Redis", "Elasticsearch"]
    for service, result in zip(services, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {service}: {status}")
    
    all_passed = all(results)
    if all_passed:
        print("\n🎉 All tests passed! Your environment is ready for development.")
    else:
        print("\n⚠️  Some tests failed. Check your configuration and ensure services are running.")
        print("   Try: docker-compose up -d")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 