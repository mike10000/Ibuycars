"""
Simple integration script for adding CRM functionality to app.py

INSTRUCTIONS:
1. Add these imports at the top of app.py (after existing imports):
   from crm_db import init_leads_db
   from crm_routes import register_crm_routes

2. Replace the init_db() function (around line 43) with this:
   
   def init_db():
       with app.app_context():
           db = get_db()
           # Initialize leads table
           init_leads_db(db)
   
3. After the line "init_db()" (around line 61), add:
   
   # Register CRM routes
   register_crm_routes(app)

4. OPTIONAL: Comment out @require_auth on line 79 if not already done:
   
   # @require_auth  # Temporarily disabled

That's it! Save app.py and restart your Flask server.
"""

# Quick test to verify CRM modules load properly
if __name__ == '__main__':
    print("Testing CRM modules...")
    try:
        from crm_db import init_leads_db
        from crm_routes import register_crm_routes
        print("✓ CRM modules imported successfully!")
        print("\nNext steps:")
        print("1. Follow instructions in this file to update app.py")
        print("2. Restart your Flask server")
        print("3. Visit http://localhost:5000 to see the CRM in action")
    except Exception as e:
        print(f"✗ Error: {e}")
