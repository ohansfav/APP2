#!/usr/bin/env python
"""
Debug test to see actual content
"""
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar

# Cookie jar to maintain session
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

def test_login(username="admin", password="admin123"):
    """Test login"""
    try:
        url = 'http://localhost:8000/login'
        data = urllib.parse.urlencode({'username': username, 'password': password}).encode('utf-8')
        response = urllib.request.urlopen(url, data, timeout=5)
        if response.status == 200:
            print(f"  ✓ Login: Successful")
            return True
    except Exception as e:
        print(f"  ✗ Login: {e}")
        return False

if test_login():
    # Try events
    try:
        response = urllib.request.urlopen('http://localhost:8000/events', timeout=5)
        content = response.read().decode('utf-8')
        
        # Check for code blocks
        if '```' in content:
            print("✗ EVENTS: Code blocks found!")
            # Find where the code blocks are
            idx = content.find('```')
            print(f"Code blocks start at position {idx}")
            print(f"Context around code blocks:")
            print(content[max(0, idx-200):min(len(content), idx+500)])
        else:
            print("✓ EVENTS: No code blocks found")
            print(f"Content length: {len(content)}")
            print(f"First 300 chars:")
            print(content[:300])
            
    except urllib.error.HTTPError as e:
        print(f"✗ EVENTS Error: {e.code}")
    except Exception as e:
        print(f"✗ EVENTS Exception: {e}")
    
    # Try analytics
    try:
        response = urllib.request.urlopen('http://localhost:8000/analytics', timeout=5)
        content = response.read().decode('utf-8')
        print("✓ ANALYTICS: Success")
    except urllib.error.HTTPError as e:
        print(f"✗ ANALYTICS Error: HTTP {e.code}")
    except Exception as e:
        print(f"✗ ANALYTICS Exception: {e}")
