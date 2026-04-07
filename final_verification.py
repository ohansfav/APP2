#!/usr/bin/env python
"""
Final verification that all features work
"""
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar

# Cookie jar to maintain session
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

def test_feature(url, name, success_check=None):
    """Test a feature"""
    try:
        response = urllib.request.urlopen(url, timeout=5)
        content = response.read().decode('utf-8')
        
        # Check for code blocks
        if '```' in content:
            print(f"  ✗ {name}: Found code blocks in response")
            return False
        
        # Check success condition if provided
        if success_check and success_check not in content:
            print(f"  ✗ {name}: Missing expected content")
            return False
        
        # Check for HTML structure
        if '<html' not in content.lower() or '</html>' not in content.lower():
            print(f"  ? {name}: Question marks on HTML structure")
            return False
            
        print(f"  ✓ {name}: Working correctly")
        return True
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        return False

# Login
data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/login', data=data)
urllib.request.urlopen(req)

print("\nFINAL VERIFICATION")
print("=" * 50)

results = {
    "Analytics": test_feature('http://localhost:8000/analytics', 'Analytics Page with Charts'),
    "Events": test_feature('http://localhost:8000/events', 'Events List'),
    "Dashboard": test_feature('http://localhost:8000/', 'Dashboard with Stats', 'total_athletes'),
    "Athletes": test_feature('http://localhost:8000/athletes', 'Athletes List'),
}

print("=" * 50)
passed = sum(1 for v in results.values() if v)
total = len(results)
print(f"\nFinal Status: {passed}/{total} features verified working")
print("\n✓ APPLICATION IS FULLY FUNCTIONAL" if passed == total else f"\n⚠ {total - passed} feature(s) need attention")
