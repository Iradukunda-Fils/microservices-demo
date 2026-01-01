#!/bin/bash

# Generate Python code from Protocol Buffer definitions
# Educational Note: This script uses grpcio-tools to generate:
# 1. *_pb2.py - Message classes (data structures)
# 2. *_pb2_grpc.py - Service stubs (client code)

echo "🔧 Generating gRPC client code from .proto files..."

# Create output directory
mkdir -p orders/grpc_generated

# Generate code for UserService
python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./orders/grpc_generated \
    --grpc_python_out=./orders/grpc_generated \
    ./protos/user.proto

# Generate code for ProductService
python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./orders/grpc_generated \
    --grpc_python_out=./orders/grpc_generated \
    ./protos/product.proto

# Fix imports in generated files (change absolute imports to relative imports)
# Educational Note: protoc generates absolute imports, but we need relative imports
# for proper Python package structure
echo "🔧 Fixing imports in generated files..."

sed -i 's/^import user_pb2 as user__pb2/from . import user_pb2 as user__pb2/' orders/grpc_generated/user_pb2_grpc.py 2>/dev/null || \
    sed -i'' -e 's/^import user_pb2 as user__pb2/from . import user_pb2 as user__pb2/' orders/grpc_generated/user_pb2_grpc.py

sed -i 's/^import product_pb2 as product__pb2/from . import product_pb2 as product__pb2/' orders/grpc_generated/product_pb2_grpc.py 2>/dev/null || \
    sed -i'' -e 's/^import product_pb2 as product__pb2/from . import product_pb2 as product__pb2/' orders/grpc_generated/product_pb2_grpc.py

# Create __init__.py if it doesn't exist (preserve manual edits)
if [ ! -f orders/grpc_generated/__init__.py ]; then
    echo "📝 Creating __init__.py..."
    cat > orders/grpc_generated/__init__.py << 'EOF'
"""
gRPC Generated Code Package - Order Service Client Stubs

This package contains auto-generated Python code from Protocol Buffer (.proto) definitions
for communicating with UserService and ProductService via gRPC.

Auto-Generated Files (DO NOT EDIT):
    - user_pb2.py: UserService message classes (ValidateUserRequest, ValidateUserResponse, etc.)
    - user_pb2_grpc.py: UserService client stub (UserServiceStub)
    - product_pb2.py: ProductService message classes (ProductInfoRequest, etc.)
    - product_pb2_grpc.py: ProductService client stub (ProductServiceStub)

Regeneration:
    Run `bash generate_grpc.sh` to regenerate these files from .proto definitions.
    The script automatically fixes imports to use relative imports.

Usage:
    from orders.grpc_generated import user_pb2, user_pb2_grpc
    from orders.grpc_generated import product_pb2, product_pb2_grpc

Note:
    This package is for ORDER SERVICE CLIENT STUBS only.
    It contains clients to call UserService and ProductService.
"""

# Import all generated modules for convenient access
# This allows: from orders.grpc_generated import user_pb2
# Instead of: from orders.grpc_generated.user_pb2 import *

try:
    from . import user_pb2
    from . import user_pb2_grpc
    from . import product_pb2
    from . import product_pb2_grpc
    
    __all__ = [
        'user_pb2',
        'user_pb2_grpc',
        'product_pb2',
        'product_pb2_grpc',
    ]
except ImportError as e:
    # If imports fail, the generated files don't exist yet
    # Run generate_grpc.sh to create them
    import warnings
    warnings.warn(
        f"gRPC generated files not found: {e}\n"
        "Run 'bash generate_grpc.sh' to generate client stubs.",
        ImportWarning
    )
    __all__ = []
EOF
fi

echo "✅ gRPC client code generated successfully!"
echo "📁 Generated files:"
echo "   - orders/grpc_generated/user_pb2.py"
echo "   - orders/grpc_generated/user_pb2_grpc.py"
echo "   - orders/grpc_generated/product_pb2.py"
echo "   - orders/grpc_generated/product_pb2_grpc.py"
echo ""
echo "✅ Import fixes applied - using relative imports"
