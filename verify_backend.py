import sys
import os

# Add current directory to sys.path to allow correct module resolution
sys.path.append(os.getcwd())

print("--- DIAGNOSTIC VERIFICATION START ---")

# 1. Test Package Imports
print("\n[1/4] Verifying imports...")
required_packages = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("bcrypt", "Bcrypt"),
    ("geocoder", "Geocoder"),
    ("mysql.connector", "MySQL Connector"),
    ("langchain_groq", "LangChain Groq"),
    ("langchain_core", "LangChain Core"),
    ("langgraph", "LangGraph"),
    ("mcp_use", "MCP-Use"),
    ("mcp", "MCP SDK"),
    ("bs4", "BeautifulSoup")
]

failed_imports = 0
for module_name, friendly_name in required_packages:
    try:
        __import__(module_name)
        print(f"  ✔ {friendly_name} ({module_name}) imported successfully!")
    except ImportError as e:
        print(f"  ❌ Failed to import {friendly_name} ({module_name}): {e}")
        failed_imports += 1

if failed_imports == 0:
    print("  ✔ All packages imported successfully!")
else:
    print(f"  ❌ {failed_imports} imports failed. Please check dependencies.")

# 2. Test Database Connections
print("\n[2/4] Verifying database connections...")
databases = ["user", "medical_profiles", "conversation", "DoctorDB"]
failed_dbs = 0

try:
    from backend.app.database import get_connection
    for db in databases:
        try:
            conn = get_connection(db)
            if conn.is_connected():
                print(f"  ✔ Connected successfully to database: '{db}'")
            conn.close()
        except Exception as e:
            print(f"  ❌ Connection failed for database '{db}': {e}")
            failed_dbs += 1
except Exception as e:
    print("  ❌ Failed to import backend.app.database:", e)
    failed_dbs = len(databases)

# 3. Test Doctor Locator Logic
print("\n[3/4] Verifying doctor locator logic...")
try:
    from backend.app.doctorconnect import find_nearest_doctors
    # Let's search nearest doctors around Bangalore coordinates (12.9716, 77.5946)
    doctors = find_nearest_doctors(12.9716, 77.5946)
    print(f"  ✔ Found {len(doctors)} doctors near latitude 12.9716, longitude 77.5946:")
    for name, specialty, phone, distance in doctors:
        print(f"    - {name} ({specialty}) - {distance:.2f} km away - Phone: {phone}")
except Exception as e:
    print("  ❌ Doctor locator check failed:", e)

# 4. Test Triage Agent Logic
print("\n[4/4] Verifying triage agent risk assessment...")
try:
    from backend.app.triagent import check_risk
    
    test_cases = [
        ("I have severe chest pain", "high/moderate - high"),
        ("Just a minor cold and cough", "low"),
        ("I do not have any difficulty breathing", "low")
    ]
    
    for query, expected in test_cases:
        res = check_risk(query)
        print(f"  Query: '{query}' -> Risk Level: '{res['risk_level']}', Advice: '{res['advice']}'")
except Exception as e:
    print("  ❌ Triage agent check failed:", e)

print("\n--- DIAGNOSTIC VERIFICATION END ---")
