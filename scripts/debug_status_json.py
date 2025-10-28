#!/usr/bin/env python3
"""
Debug script to find non-JSON-serializable fields in processing_status
"""

import json
from typing import Any, Dict

def check_json_serializable(obj: Any, path: str = "root") -> list[str]:
    """
    Recursively check if object is JSON-serializable.
    Returns list of problematic paths.
    """
    problems = []
    
    try:
        json.dumps(obj)
        return []  # Everything OK
    except (TypeError, ValueError) as e:
        # This level has a problem
        if isinstance(obj, dict):
            # Check each key-value pair
            for key, value in obj.items():
                sub_path = f"{path}.{key}"
                try:
                    json.dumps({key: value})
                except (TypeError, ValueError):
                    # This field is problematic
                    value_type = type(value).__name__
                    if callable(value):
                        problems.append(f"{sub_path} = <{value_type}: {getattr(value, '__name__', 'anonymous')}> [METHOD/FUNCTION]")
                    elif hasattr(value, '__dict__'):
                        problems.append(f"{sub_path} = <{value_type} object> [HAS __dict__]")
                        # Recurse into object
                        problems.extend(check_json_serializable(value, sub_path))
                    elif isinstance(value, dict):
                        # Recurse into dict
                        problems.extend(check_json_serializable(value, sub_path))
                    elif isinstance(value, (list, tuple)):
                        # Recurse into list/tuple
                        for i, item in enumerate(value):
                            problems.extend(check_json_serializable(item, f"{sub_path}[{i}]"))
                    else:
                        problems.append(f"{sub_path} = {value!r} [{value_type}]")
        
        elif isinstance(obj, (list, tuple)):
            for i, item in enumerate(obj):
                problems.extend(check_json_serializable(item, f"{path}[{i}]"))
        
        else:
            # Primitive problematic value
            value_type = type(obj).__name__
            problems.append(f"{path} = {obj!r} [{value_type}]")
    
    return problems


if __name__ == "__main__":
    # Import here to avoid import issues
    import sys
    sys.path.insert(0, '/app')
    
    from app.core.processor import processing_status
    
    upload_id = '11b3a971-da82-41a1-8c1b-779c06463708'
    
    status = processing_status.get(upload_id)
    
    if not status:
        print(f"❌ Upload ID not found: {upload_id}")
        sys.exit(1)
    
    print(f"📊 Status dict keys: {list(status.keys())}")
    print(f"📊 Status: {status.get('status')}")
    print(f"📊 Stage: {status.get('stage')}")
    print(f"\n🔍 Checking JSON serializability...\n")
    
    problems = check_json_serializable(status, "status")
    
    if problems:
        print(f"❌ Found {len(problems)} problematic field(s):\n")
        for problem in problems:
            print(f"  • {problem}")
    else:
        print("✅ All fields are JSON-serializable!")
        print("\n📋 Full status dict:")
        print(json.dumps(status, indent=2))

