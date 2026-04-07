#!/usr/bin/env python
import urllib.request, urllib.error, urllib.parse, http.cookiejar

# Login first
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

# Login
data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/login', data=data)
response = opener.open(req)

# Get analytics page
try:
    response = opener.open('http://localhost:8000/analytics', timeout=5)
    content = response.read().decode('utf-8')
    # Check if it has code blocks
    if '```' in content:
        print("Analytics has code blocks")
    else:
        print("Analytics does NOT have code blocks")
        # Check what base it uses
        if 'modern.html' in content or 'css/modern.css' in content:
            print("Analytics uses modern template")
        elif 'base.html' in content:
            print("Analytics uses base.html")
        else:
            print("Analytics uses unknown basis")
    
    # Show first 200 chars
    print(f"First 200 chars: {content[:200]}")
except Exception as e:
    print(f"Error: {e}")
