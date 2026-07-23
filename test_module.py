import sys
import json
import os

# Adjust path to import backend modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.placement_service import generate_mock_module

# Test Aptitude Module
result = generate_mock_module("aptitude", None, "easy", 20)

if "error" in result:
    print("Error:", result["error"])
else:
    print(f"Success! Generated {len(result['questions'])} questions for {result['module']} ({result['difficulty']})")
    
# Test Technical Module
result2 = generate_mock_module("technical-mcq", None, "hard", 20)
if "error" in result2:
    print("Error:", result2["error"])
else:
    print(f"Success! Generated {len(result2['questions'])} questions for {result2['module']} ({result2['difficulty']})")

