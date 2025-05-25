#!/usr/bin/env python3
"""
Simple script to start the JobBot development server
"""
import os
import sys
from pathlib import Path

def setup_environment():
    """Set up environment for development"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set environment variable for SQLite if PostgreSQL not configured
    if not os.getenv('POSTGRES_HOST'):
        os.environ['DATABASE_URL'] = 'sqlite:///./jobbot.db'
        print("🗃️ Using SQLite database for development")
    
    # Set debug mode
    os.environ['DEBUG'] = 'True'

def main():
    """Start the development server"""
    setup_environment()
    
    print("🚀 Starting JobBot Development Server")
    print("=" * 40)
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("⚡ Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed. Run: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure requirements are installed: pip install -r requirements.txt")
        print("2. Check that port 8000 is not already in use")
        print("3. Verify Python path includes the project directory")
        sys.exit(1)

if __name__ == "__main__":
    main()