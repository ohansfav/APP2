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
print("Logged in successfully")

# Now try analytics
try:
    response = opener.open('http://localhost:8000/analytics', timeout=5)
    content = response.read().decode('utf-8')
    print(f'Status: {response.status}')
    print(f'Content length: {len(content)}')
    print(f'First 1000 chars:')
    print(content[:1000])
except urllib.error.HTTPError as e:
    print(f'HTTP Error: {e.code}')
    content = e.read().decode('utf-8')
    print('Error content (500 chars):')
    print(content[:500])
