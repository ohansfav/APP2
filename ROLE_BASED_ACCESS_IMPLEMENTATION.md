# Role-Based Access Control Implementation

## Overview
Implemented a comprehensive multi-role access system with three user types: Admin, Coach, and User. Each role has specific permissions and access levels.

## Changes Made

### 1. Database Model Updates (`models/database.py`)

#### User Model Enhancements
- Added `role` field (String, 20 chars): `'admin'`, `'coach'`, or `'user'`
- Added `sport_specialization` field (String, 100 chars): Sport that coaches specialize in
- Updated `to_dict()` method to include new fields

### 2. Authentication Routes (`app/routes.py`)

#### Added Role-Based Decorators
- `@admin_required`: Restricts access to admin users only
- `@coach_or_admin_required`: Restricts access to coaches and admins
- Updated `@login_required`: Base authentication decorator (unchanged)

#### Updated Login Route
- Now stores `user_role` and `user_sport` in session on successful login
- Validates user credentials and retrieves role information from database
- Removed demo user fallback authentication (only database users can login)

#### Updated Signup Route
- Added `role` field to registration form (accepts: 'admin', 'coach', 'user')
- Added `sport_specialization` field for coach accounts
- Validates that coaches select a sport before registration
- Uses role-based setter on new User object

#### Updated Dashboard Route
- Implements role-based data filtering:
  - **Admin**: Views all athletes, events, and injuries globally
  - **Coach**: Views only athletes/events/injuries for their selected sport
  - **User**: Views only athletes for their selected sport (no events/injuries)
- Passes `user_role` and `user_sport` to template

#### Updated Athletes Routes
- `@athletes_list`: Filters athletes based on role and sport
- `@add_athlete`: Protected by `@coach_or_admin_required`; coaches can only add athletes for their sport
- `@delete_athlete_form`: Protected by `@coach_or_admin_required`; coaches can only delete athletes from their sport

### 3. Login/Signup Template (`templates/login.html`)

#### Demo Credentials Section
- Completely removed demo credentials display
- Users must authenticate with real credentials only

#### Signup Form Enhancements
- **Added Role Selection Dropdown**:
  - Option 1: "User (View Only)"
  - Option 2: "Coach (Manage Specific Sport)"
  - Option 3: "Admin (Full Access)"

- **Added Sport Selection Dropdown** (conditional):
  - Shows dynamically only when "Coach" role is selected
  - Lists 11 sports: Football, Basketball, Tennis, Swimming, Track & Field, Cricket, Volleyball, Hockey, Badminton, Gymnastics, Other
  - Required validation for coaches

#### JavaScript Enhancements
- Event listener on role dropdown to show/hide sport selection
- Sport dropdown marked as required when role === 'coach'
- Form validation prevents submission without sport selection for coaches

### 4. Base Template (`templates/base.html`)

#### Added "VIEW ONLY" Badge
- **Location**: Fixed position top-right corner
- **Display**: Only visible for users with `user_role == 'user'`
- **Styling**:
  - Transparent background (rgba-based)
  - Slide-in animation from the right
  - Fade animation effect
  - Glassmorphism effect with backdrop blur
- **Animation**: 
  - Slides in smoothly on page load (500ms)
  - Mild fade animation throughout presence

## User Roles & Permissions

### 1. Admin (Full Access)
- ✅ View all athletes in all sports
- ✅ Add athletes without sport restrictions
- ✅ Delete/edit athletes
- ✅ View all events
- ✅ View all injury data
- ✅ Access all analytics
- ✅ No "VIEW ONLY" badge

### 2. Coach (Sport-Specific Management)
- ✅ View athletes only from their selected sport
- ✅ Add athletes only to their sport
- ✅ Edit/delete athletes only from their sport
- ⚠️ View events (global)
- ✅ View injury data only for their sport
- ✅ Manage only their sport's activities
- ❌ No "VIEW ONLY" badge (they have management access)

### 3. User (View-Only)
- ✅ View athletes only from their selected sport
- ❌ Cannot add/edit/delete athletes
- ❌ Cannot manage events
- ❌ Cannot access injury data
- ❌ Cannot access admin/analytics areas
- ✅ "VIEW ONLY" badge displayed (transparent, top-right)

## Database Changes

### User Table Schema
```sql
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL
ALTER TABLE users ADD COLUMN sport_specialization VARCHAR(100)
```

### Migration Note
- Old database (`sports_management.db`) needs to be deleted
- New database will be created on first run with updated schema
- All existing user data will be lost (fresh start)

## Testing Instructions

### 1. Register as Admin
- Username: `admin_user`
- Role: **Admin**
- Sport: (not required - can be empty)
- Expected: Full access to all features

### 2. Register as Coach
- Username: `football_coach`
- Role: **Coach**
- Sport: **Football**
- Expected: See only football athletes/events, "VIEW ONLY" badge NOT shown

### 3. Register as User
- Username: `football_fan`
- Role: **User**
- Sport: **Football**
- Expected: See only football athletes, "VIEW ONLY" badge in top-right corner

## Security Considerations

1. ✅ Role-based access enforced on all protected routes
2. ✅ Coaches cannot access other sports' data
3. ✅ Users cannot modify any data
4. ✅ Session-based role verification on every request
5. ✅ Demo credentials removed for production readiness

## Files Modified

1. `models/database.py` - Added role and sport fields to User model
2. `app/routes.py` - Added role-based decorators, updated auth routes, implemented filtering
3. `templates/login.html` - Removed demo credentials, added role/sport dropdowns
4. `templates/base.html` - Added "VIEW ONLY" badge with animations
5. `app/__init__.py` - Fixed demo data initialization

## Future Enhancements

- [ ] Coach permission to modify other coaches' athletes (with admin approval)
- [ ] User can select multiple sports
- [ ] Role-based dashboard widgets (different layout per role)
- [ ] Audit logging for admin actions
- [ ] Sport-specific analytics dashboards
- [ ] Coach feedback/notes on athletes
- [ ] Parent role for athlete families
