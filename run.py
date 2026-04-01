"""
Main Application Runner
Run: python run.py
"""
from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    
    # Get host and port from environment or use defaults
    host = os.getenv('HOST', '0.0.0.0')  # 0.0.0.0 makes it accessible from other devices
    port = int(os.getenv('PORT', 8000))
    
    # Run development server
    print("\n" + "="*60)
    print("🎯 ATHLETE PERFORMANCE PREDICTOR")
    print("="*60)
    print(f"\n📊 Dashboard: http://localhost:{port}")
    print(f"🏃 Athletes: http://localhost:{port}/athletes")
    print(f"📈 Analytics: http://localhost:{port}/analytics")
    print("\n🚀 Server running in offline-first mode...")
    print("="*60 + "\n")
    
    # debug=False in production, True in development
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host=host, port=port)
