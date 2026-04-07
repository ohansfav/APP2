#!/usr/bin/env python
"""
Test new features: Add athlete and add event
"""
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar

# Setup
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

print("\n" + "="*70)
print("TESTING NEW FEATURES")
print("="*70 + "\n")

# Login
print("1. Logging in...")
data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/login', data=data)
response = opener.open(req)
print("   ✓ Login successful\n")

# Test add athlete
print("2. Testing Add Athlete...")
try:
    data = urllib.parse.urlencode({
        'name': 'Test Athlete',
        'sport': 'Football',
        'age': '25',
        'performance_score': '85'
    }).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/athlete/add', data=data)
    response = opener.open(req)
    print("   ✓ Add athlete form submitted successfully\n")
except urllib.error.HTTPError as e:
    print(f"   ✗ HTTP Error {e.code}: {e.reason}\n")
except Exception as e:
    print(f"   ✗ Error: {e}\n")

# Test add event
print("3. Testing Add Event...")
try:
    data = urllib.parse.urlencode({
        'event_name': 'Test Event',
        'event_type': 'Training',
        'location': 'Main Stadium',
        'event_date': '2026-04-15T15:00',
        'description': 'Test event description'
    }).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/event/add', data=data)
    response = opener.open(req)
    print("   ✓ Add event form submitted successfully\n")
except urllib.error.HTTPError as e:
    print(f"   ✗ HTTP Error {e.code}: {e.reason}\n")
except Exception as e:
    print(f"   ✗ Error: {e}\n")

# Verify athletes page loads and shows limited athletes
print("4. Verifying Athletes Page...")
try:
    response = opener.open('http://localhost:8000/athletes', timeout=5)
    content = response.read().decode('utf-8')
    
    # Count athlete rows
    athlete_rows = content.count('<tr class="athlete-row">')
    print(f"   ✓ Athletes page loaded with {athlete_rows} athletes shown\n")
    
    if athlete_rows <= 15:
        print("   ✓ Athletes correctly limited to 15 or fewer\n")
    else:
        print(f"   ? More than 15 athletes showing ({athlete_rows})\n")
        
except Exception as e:
    print(f"   ✗ Error: {e}\n")

# Verify events page has add button
print("5. Verifying Events Page...")
try:
    response = opener.open('http://localhost:8000/events', timeout=5)
    content = response.read().decode('utf-8')
    
    if 'Add Event' in content or 'add_btn' in content:
        print("   ✓ Events page has 'Add Event' button\n")
    else:
        print("   ? Add Event button not clearly visible\n")
        
    if 'eventModal' in content:
        print("   ✓ Events page has event modal form\n")
    else:
        print("   ? Event modal not found\n")
except Exception as e:
    print(f"   ✗ Error: {e}\n")

print("="*70)
print("FEATURE TESTING COMPLETE")
print("="*70)
