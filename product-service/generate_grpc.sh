#!/bin/bash
# Script to generate Python code from Protocol Buffer definitions

echo "🔧 Generating Python code from Protocol Buffers..."

# Create output directory
mkdir -p grpc_generated

# Generate Python code
python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./grpc_generated \
    --grpc_python_out=./grpc_generated \
    ./protos/product.proto

# Fix imports in generated files (change "import product_pb2" to "from . import product_pb2")
echo "🔧 Fixing imports in generated files..."
sed -i 's/^import product_pb2 as product__pb2/from . import product_pb2 as product__pb2/' grpc_generated/product_pb2_grpc.py 2>/dev/null || \
    sed -i'' -e 's/^import product_pb2 as product__pb2/from . import product_pb2 as product__pb2/' grpc_generated/product_pb2_grpc.py

# Create __init__.py if it doesn't exist (preserve manual edits)
if [ ! -f grpc_generated/__init__.py ]; then
    echo "📝 Creating __init__.py..."
    cat > grpc_generated/__init__.py << 'EOF'
"""
gRPC Generated Code Package - Product Service

This package contains auto-generated Python code from Protocol Buffer (.proto) definitions
for the ProductService gRPC API.

Auto-Generated Files (DO NOT EDIT):
    - product_pb2.py: Message classes (ProductInfoRequest, ProductInfoResponse, etc.)
    - product_pb2_grpc.py: Service classes (ProductServiceServicer, ProductServiceStub)

Regeneration:
    Run `bash generate_grpc.sh` to regenerate these files from protos/product.proto.
    The script automatically fixes imports to use relative imports.

Usage:
    # Server-side (grpc_server.py)
    from grpc_generated import product_pb2, product_pb2_grpc
    
    # Client-side (other services)
    from grpc_generated import product_pb2, product_pb2_grpc

Architecture:
    - product_pb2.py: Data structures (messages) for requests/responses
    - product_pb2_grpc.py: Service interface (ProductServiceServicer for server, ProductServiceStub for client)

Note:
    This is the SERVER-SIDE package for ProductService.
    Other services import this as a CLIENT to call ProductService.
"""

# Import all generated modules for convenient access
try:
    from . import product_pb2
    from . import product_pb2_grpc
    
    __all__ = [
        'product_pb2',
        'product_pb2_grpc',
    ]
except ImportError as e:
    # If imports fail, the generated files don't exist yet
    # Run generate_grpc.sh to create them
    import warnings
    warnings.warn(
        f"gRPC generated files not found: {e}\n"
        "Run 'bash generate_grpc.sh' to generate gRPC code from protos/product.proto",
        ImportWarning
    )
    __all__ = []
EOF
fi

echo "✅ Generated grpc_generated/product_pb2.py"
echo "✅ Generated grpc_generated/product_pb2_grpc.py"
echo "✅ Import fixes applied"
echo ""
