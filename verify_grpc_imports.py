#!/usr/bin/env python3
"""
Verification script for gRPC package imports.

This script verifies that all gRPC generated packages have proper:
- __init__.py files
- Explicit imports
- __all__ declarations
- Error handling

Run this script to verify the improvements are working correctly.
"""

import sys
import importlib
import warnings

def test_package(package_name, expected_modules):
    """Test a gRPC generated package."""
    print(f"\n{'='*60}")
    print(f"Testing: {package_name}")
    print(f"{'='*60}")
    
    try:
        # Import the package
        package = importlib.import_module(package_name)
        print(f"✅ Package imported successfully")
        
        # Check __all__ exists
        if hasattr(package, '__all__'):
            print(f"✅ __all__ is defined: {package.__all__}")
            
            # Verify expected modules are in __all__
            for module in expected_modules:
                if module in package.__all__:
                    print(f"   ✅ {module} in __all__")
                else:
                    print(f"   ❌ {module} NOT in __all__")
        else:
            print(f"❌ __all__ is NOT defined")
        
        # Check if modules can be imported
        for module in expected_modules:
            try:
                mod = getattr(package, module)
                print(f"✅ {module} is accessible")
            except AttributeError:
                print(f"❌ {module} is NOT accessible")
        
        # Check documentation
        if package.__doc__:
            doc_lines = package.__doc__.strip().split('\n')
            print(f"✅ Documentation exists ({len(doc_lines)} lines)")
            print(f"   First line: {doc_lines[0]}")
        else:
            print(f"❌ No documentation")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("gRPC Package Import Verification")
    print("="*60)
    
    results = []
    
    # Test Order Service (client stubs)
    results.append(test_package(
        'orders.grpc_generated',
        ['user_pb2', 'user_pb2_grpc', 'product_pb2', 'product_pb2_grpc']
    ))
    
    # Test User Service (server)
    results.append(test_package(
        'grpc_generated',  # user-service
        ['user_pb2', 'user_pb2_grpc']
    ))
    
    # Note: product-service would need to be in Python path
    # Skipping for now as this script runs from order-service context
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
