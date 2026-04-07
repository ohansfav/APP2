"""
Main Application Runner
Run: python run.py
"""
from app import create_app
import os
import socket

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # This works on most systems
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

if __name__ == '__main__':
    app = create_app()
    
    # Detect environment
    is_replit = os.getenv('REPLIT_DB_URL') is not None or 'replit' in os.getenv('HOSTNAME', '').lower()
    
    if is_replit:
        # Replit environment - use provided PORT
        host = '0.0.0.0'
        port = int(os.getenv('PORT', 5000))
        replit_url = os.getenv('REPLIT_URL', 'https://your-replit-url.replit.dev')
        
        print("\n" + "="*70)
        print("🎯 ATHLETE PERFORMANCE PREDICTOR - REPLIT")
        print("="*70)
        print(f"\n🌐 Cloud Access: {replit_url}")
        print(f"📊 Dashboard: {replit_url}/")
        print(f"🏃 Athletes: {replit_url}/athletes")
        print(f"📈 Analytics: {replit_url}/analytics")
        print(f"📅 Events: {replit_url}/events")
        print(f"\n✅ Share the URL above with your friends!")
        print(f"🚀 Server running on Replit...")
        print("="*70)
    else:
        # Local environment
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        local_ip = get_local_ip()
        
        print("\n" + "="*70)
        print("🎯 ATHLETE PERFORMANCE PREDICTOR")
        print("="*70)
        print(f"\n📱 Local Access: http://localhost:{port}")
        print(f"🌐 Network Access: http://{local_ip}:{port}")
        print(f"\n📊 Dashboard: http://{local_ip}:{port}")
        print(f"🏃 Athletes: http://{local_ip}:{port}/athletes")
        print(f"📈 Analytics: http://{local_ip}:{port}/analytics")
        print(f"📅 Events: http://{local_ip}:{port}/events")
        print(f"\n✅ Share the network URL with your friends!")
        print(f"🚀 Server running - accessible from other devices...")
        print("="*70)
    
    app.run(host=host, port=port, debug=False)
