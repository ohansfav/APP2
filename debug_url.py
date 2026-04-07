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

# Get events page with debug info
req = urllib.request.Request('http://localhost:8000/events')
try:
    response = opener.open(req, timeout=5)
    print(f"URL: {response.url}")
    print(f"Status Code: {response.status}")
    print(f"Headers: {dict(response.headers)}")
    content = response.read().decode('utf-8')
    print(f"Content length: {len(content)}")
    print(f"Content starts with: {content[:100]}")
except Exception as e:
    print(f"Error: {e}")
