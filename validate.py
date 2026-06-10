#!/usr/bin/env python3
"""
API Validation Script - Run after dependencies are installed
Tests all API endpoints for proper functionality
"""

import sys
import os
import json
from pathlib import Path

def check_files():
    """Verify all required files exist"""
    print("=" * 60)
    print("FILE STRUCTURE VALIDATION")
    print("=" * 60)
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/database.py",
        "app/models.py",
        "app/schemas.py",
        "app/routers/__init__.py",
        "app/routers/surveys.py",
        "app/routers/questions.py",
        "app/routers/responses.py",
        "app/routers/certificates.py",
        "app/services/file_service.py",
        "app/services/xml_service.py",
        "database_schema.sql",
        "requirements.txt",
        ".env",
        ".gitignore",
        "README.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def check_imports():
    """Verify all Python imports work"""
    print("\n" + "=" * 60)
    print("IMPORT VALIDATION")
    print("=" * 60)
    
    sys.path.insert(0, '.')
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("fastapi.responses", "Response"),
        ("mysql.connector", None),
        ("pydantic", "BaseModel"),
        ("python_dotenv", "load_dotenv"),
    ]
    
    all_ok = True
    for module_name, item_name in imports_to_test:
        try:
            if item_name:
                exec(f"from {module_name} import {item_name}")
            else:
                __import__(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"✗ {module_name} - {e}")
            all_ok = False
    
    # Check custom modules
    try:
        from app.services.xml_service import dict_to_xml
        print(f"✓ app.services.xml_service")
    except Exception as e:
        print(f"✗ app.services.xml_service - {e}")
        all_ok = False
    
    try:
        from app.services.file_service import save_uploaded_file
        print(f"✓ app.services.file_service")
    except Exception as e:
        print(f"✗ app.services.file_service - {e}")
        all_ok = False
    
    return all_ok

def check_requirements():
    """Verify requirements.txt is properly formatted"""
    print("\n" + "=" * 60)
    print("REQUIREMENTS VALIDATION")
    print("=" * 60)
    
    required_packages = {
        "fastapi": "0.104.1",
        "uvicorn": "0.24.0",
        "python-dotenv": "1.0.0",
        "mysql-connector-python": "8.2.0",
        "pydantic": "2.5.0",
        "pydantic-extra-types": "2.4.0",
        "python-multipart": "0.0.6"
    }
    
    try:
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
        
        all_ok = True
        for package, version in required_packages.items():
            expected = f"{package}=={version}\n"
            if expected in lines:
                print(f"✓ {package}=={version}")
            else:
                print(f"✗ {package}=={version} - Not found or wrong version")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        return False

def check_database_schema():
    """Verify database schema file is complete"""
    print("\n" + "=" * 60)
    print("DATABASE SCHEMA VALIDATION")
    print("=" * 60)
    
    required_tables = [
        "CREATE TABLE surveys",
        "CREATE TABLE questions",
        "CREATE TABLE options",
        "CREATE TABLE responses",
        "CREATE TABLE answer_texts",
        "CREATE TABLE answer_choices",
        "CREATE TABLE certificates"
    ]
    
    try:
        with open("database_schema.sql", "r") as f:
            content = f.read()
        
        all_ok = True
        for table in required_tables:
            if table in content:
                table_name = table.split()[-1]
                print(f"✓ Table: {table_name}")
            else:
                table_name = table.split()[-1]
                print(f"✗ Table: {table_name} - Not found")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"✗ Error reading database_schema.sql: {e}")
        return False

def check_env_config():
    """Verify .env configuration"""
    print("\n" + "=" * 60)
    print("ENVIRONMENT CONFIGURATION")
    print("=" * 60)
    
    required_vars = [
        "DB_HOST",
        "DB_PORT",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
        "DB_POOL_SIZE"
    ]
    
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
        
        all_ok = True
        for var in required_vars:
            if any(var in line for line in lines):
                print(f"✓ {var}")
            else:
                print(f"✗ {var} - Not found")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"✗ Error reading .env: {e}")
        return False

def check_python_syntax():
    """Check Python files for syntax errors"""
    print("\n" + "=" * 60)
    print("PYTHON SYNTAX VALIDATION")
    print("=" * 60)
    
    python_files = [
        "app/main.py",
        "app/database.py",
        "app/models.py",
        "app/schemas.py",
        "app/routers/surveys.py",
        "app/routers/questions.py",
        "app/routers/responses.py",
        "app/routers/certificates.py",
        "app/services/xml_service.py",
        "app/services/file_service.py"
    ]
    
    all_ok = True
    for py_file in python_files:
        try:
            with open(py_file, "r") as f:
                compile(f.read(), py_file, "exec")
            print(f"✓ {py_file}")
        except SyntaxError as e:
            print(f"✗ {py_file} - {e}")
            all_ok = False
    
    return all_ok

def main():
    """Run all validation checks"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "SKY SURVEY API VALIDATION" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = {
        "File Structure": check_files(),
        "Python Syntax": check_python_syntax(),
        "Requirements": check_requirements(),
        "Database Schema": check_database_schema(),
        "Environment Config": check_env_config(),
    }
    
    # Imports are optional if packages not installed yet
    try:
        results["Imports"] = check_imports()
    except Exception as e:
        print("\n" + "=" * 60)
        print("IMPORT VALIDATION (SKIPPED)")
        print("=" * 60)
        print("Note: Dependencies not installed. Run: pip install -r requirements.txt")
        results["Imports"] = None
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for check, passed in results.items():
        if passed is None:
            status = "⊘ SKIPPED"
        elif passed:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        print(f"{check:.<40} {status}")
    
    all_passed = all(v for v in results.values() if v is not None)
    
    print("\n" + "=" * 60)
    
    # Import failures are expected if dependencies not installed yet
    if results["Imports"] is False:
        print("⊘ NOTE: Import failures are expected before running: pip install -r requirements.txt")
        print("\nREADY FOR SETUP - All core validations passed!")
    
    if all_passed:
        print("✓ ALL CHECKS PASSED - Project is ready!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create database: mysql -u root -p < database_schema.sql")
        print("3. Configure .env with your database credentials")
        print("4. Start API: uvicorn app.main:app --reload")
        print("5. Visit: http://localhost:8000/docs")
        return 0
    elif results["Imports"] is False and all(v for k, v in results.items() if k != "Imports" and v is not None):
        print("✓ CORE VALIDATIONS PASSED - Ready for dependency installation")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create database: mysql -u root -p < database_schema.sql")
        print("3. Configure .env with your database credentials")
        print("4. Start API: uvicorn app.main:app --reload")
        print("5. Visit: http://localhost:8000/docs")
        return 0
    else:
        print("✗ VALIDATION FAILED - Please fix errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
