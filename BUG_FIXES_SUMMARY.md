# Bug Fixes - Role-Based Access Control Refinement

## Issues Fixed

### 1. Query Filter Error - "LIMIT or OFFSET applied"
**Problem**: When users were added, they received the error:
```
Query.filter() being called on a Query which already has LIMIT or OFFSET applied.
```

**Root Cause**: Queries were being reused with `.limit()` already applied, then trying to add `.filter()` or `.order_by()` afterward.

**Solution**: Refactored the dashboard route to create fresh queries for each operation instead of reusing a single query with limit applied.

**Code Changes (`app/routes.py`)**:
- Changed from: `athlete_query = Athlete.query.limit(0)` then calling `.filter()` on it
- Changed to: Creating separate fresh queries for each database operation
  - `total_athletes = Athlete.query.filter_by(sport=user_sport).count()`
  - `all_athletes = Athlete.query.filter_by(sport=user_sport).all()`
  - `top_performers = Athlete.query.filter_by(sport=user_sport).order_by(...).limit(4).all()`

### 2. Users Able to Add Events
**Problem**: Users were able to add events, which they shouldn't be able to do.

**Solution**: Added role-based access control to event routes:

**Changes**:
- Protected `/event/add` (POST) route with `@coach_or_admin_required` decorator
- Protected `/events` (GET) route - redirects users to dashboard
- Protected API endpoint `/api/events` (POST) - returns 403 Forbidden for users
- Protected API endpoint `/api/events` (GET) - returns 403 Forbidden for users

### 3. Users Should Not Access Other Restricted Operations
**Problem**: Users could potentially add/update/delete athletes and injuries via API calls.

**Solution**: Added role-based validation to all data-modifying routes:

**Protected Routes**:
- `/athlete/add` (POST) - Protected with `@coach_or_admin_required`
- `/api/athletes/<id>` (PUT) - Added role check, coaches can only update their sport's athletes
- `/api/athletes/<id>` (DELETE) - Added role check, coaches can only delete their sport's athletes  
- `/api/injuries` (POST) - Added role check, coaches can only log injuries for their sport

### 4. Enhanced "VIEW ONLY" Badge
**Improvements to badge styling**:
- Increased opacity: `rgba(59, 130, 246, 0.9)` (more visible blue)
- Enhanced border: `1.5px solid rgba(255, 255, 255, 0.3)`
- Added box-shadow: `0 4px 20px rgba(59, 130, 246, 0.4)` (glow effect)
- Better animation: **pulse-badge** animation (scales and fades in continuous cycle)
- Increased animation duration and smoothness
- Added responsive styling for mobile devices

**Badge Behavior**:
- Shows only for users with `user_role == 'user'`
- Slides in from right on page load
- Continuously pulses for visibility
- Positioned at top-right (fixed position)

## Access Control Summary

### Admin
✅ Full access to all features
✅ Add/Edit/Delete athletes from any sport
✅ Add/Manage events
✅ View/Log injuries for all athletes
✅ Access all analytics

### Coach
✅ Add/Edit/Delete athletes from THEIR sport only
✅ Add/Manage events (global)
✅ View/Log injuries for athletes in THEIR sport only
✅ View athletes from THEIR sport only
✅ Cannot access athletes/injuries from other sports
❌ Cannot perform admin functions

### User
✅ View athletes from THEIR sport only
✅ View analytics and dashboard (filtered for their sport)
❌ Cannot add/edit/delete athletes
❌ Cannot add/manage events
❌ Cannot log/view injury data
❌ Cannot access restricted pages (redirected to dashboard)
✅ "VIEW ONLY" badge displayed

## Protection Checklist

| Operation | Route | Protection |
|-----------|-------|-----------|
| Add Athlete | `/athlete/add` (POST) | `@coach_or_admin_required` |
| Delete Athlete (Form) | `/delete_athlete` (POST) | `@coach_or_admin_required` |
| Update Athlete (API) | `/api/athletes/<id>` (PUT) | Role + Sport check |
| Delete Athlete (API) | `/api/athletes/<id>` (DELETE) | Role + Sport check |
| View Athletes | `/athletes` (GET) | Filters by role/sport |
| Add Event (Form) | `/event/add` (POST) | `@coach_or_admin_required` |
| View Events | `/events` (GET) | Users redirected to dashboard |
| Create Event (API) | `/api/events` (POST) | 403 Forbidden for users |
| Get Events (API) | `/api/events` (GET) | 403 Forbidden for users |
| Log Injury (API) | `/api/injuries` (POST) | Role + Sport check |
| Dashboard | `/` (GET) | Filters data by role/sport |

## Testing Results

✅ Query error fixed - database operations work smoothly
✅ Users cannot add events
✅ Users cannot add/edit/delete athletes
✅ Users cannot log injuries
✅ VIEW ONLY badge displays prominently with pulsing animation
✅ Coaches can only manage their sport's data
✅ Admins have full system access
✅ Role redirects working correctly
✅ All API endpoints properly secured

## Files Modified

1. `app/routes.py` - Added role checks, fixed query ordering, protected routes
2. `templates/base.html` - Enhanced VIEW ONLY badge styling and animation

## Deployment Notes

- Database already has `role` and `sport_specialization` columns
- No migration needed - old database was fresh
- All changes are backward compatible
- Error logging enabled for debugging
