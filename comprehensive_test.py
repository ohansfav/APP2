#!/usr/bin/env python
"""
Comprehensive test of all functionality
"""
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar

# Cookie jar to maintain session
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

def test_get(url, name):
    """Test GET request"""
    try:
        response = urllib.request.urlopen(url, timeout=5)
        content = response.read().decode('utf-8')
        
        # Check for code blocks
        if '```' in content:
            print(f"  ✗ {name}: Code blocks found")
            return False
        
        # Check for HTML structure
        if '<html' in content and '</html>' in content:
            print(f"  ✓ {name}: Loaded successfully")
            return True
        else:
            print(f"  ? {name}: Questionable HTML structure")
            return False
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        return False

def test_login(username="admin", password="admin123"):
    """Test login"""
    try:
        url = 'http://localhost:8000/login'
        data = urllib.parse.urlencode({'username': username, 'password': password}).encode('utf-8')
        response = urllib.request.urlopen(url, data, timeout=5)
        content = response.read().decode('utf-8')
        
        if response.status == 200:
            print(f"  ✓ Login: Successful")
            return True
        else:
            print(f"  ✗ Login: Failed with status {response.status}")
            return False
    except Exception as e:
        print(f"  ✗ Login: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE APP TEST - Athlete Performance Predictor")
    print("="*70 + "\n")
    
    results = {}
    
    # Test 1: Login Page
    print("1. LOGIN PAGE")
    results['login_page'] = test_get('http://localhost:8000/login', 'Login page')
    
    # Test 2: Login  
    print("\n2. AUTHENTICATION")
    results['login_auth'] = test_login()
    
    if results['login_auth']:
        # Test 3: Dashboard
        print("\n3. DASHBOARD")
        results['dashboard'] = test_get('http://localhost:8000/', 'Dashboard')
        
        # Test 4: Athletes
        print("\n4. ATHLETES")
        results['athletes'] = test_get('http://localhost:8000/athletes', 'Athletes list')
        
        # Test 5: Analytics
        print("\n5. ANALYTICS")
        results['analytics'] = test_get('http://localhost:8000/analytics', 'Analytics')
        
        # Test 6: Events
        print("\n6. EVENTS")
        results['events'] = test_get('http://localhost:8000/events', 'Events')
    else:
        print("\n⚠️  SKIPPING: Could not authenticate - remaining tests skipped")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print("\nResults:")
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n" + "="*70)
    if passed == total:
        print("✓ ALL TESTS PASSED - App is working correctly!")
    else:
        print(f"⚠️  {total - passed} test(s) failed - Fix needed")
    print("="*70 + "\n")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
