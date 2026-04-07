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

# Get events page
response = opener.open('http://localhost:8000/events', timeout=5)
content = response.read().decode('utf-8')

# Save to file
with open('events_response.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Saved events response to events_response.html ({len(content)} bytes)")
print(f"First 300 chars:")
print(content[:300])
