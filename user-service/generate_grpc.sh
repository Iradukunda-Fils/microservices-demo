#!/bin/bash
# Script to generate Python code from Protocol Buffer definitions
#
# Educational Note: grpcio-tools compiles .proto files into Python code
# This generates two files:
# - user_pb2.py: Message classes (data structures)
# - user_pb2_grpc.py: Service classes (RPC methods)

echo "🔧 Generating Python code from Protocol Buffers..."

# Create output directory
mkdir -p grpc_generated

# Generate Python code
python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./grpc_generated \
    --grpc_python_out=./grpc_generated \
    ./protos/user.proto

# Fix imports in generated files (change "import user_pb2" to "from . import user_pb2")
echo "🔧 Fixing imports in generated files..."
sed -i 's/^import user_pb2 as user__pb2/from . import user_pb2 as user__pb2/' grpc_generated/user_pb2_grpc.py 2>/dev/null || \
    sed -i'' -e 's/^import user_pb2 as user__pb2/from . import user_pb2 as user__pb2/' grpc_generated/user_pb2_grpc.py

# Create __init__.py if it doesn't exist (preserve manual edits)
if [ ! -f grpc_generated/__init__.py ]; then
    echo "📝 Creating __init__.py..."
    cat > grpc_generated/__init__.py << 'EOF'
"""
gRPC Generated Code Package - User Service

This package contains auto-generated Python code from Protocol Buffer (.proto) definitions
for the UserService gRPC API.

Auto-Generated Files (DO NOT EDIT):
    - user_pb2.py: Message classes (ValidateUserRequest, ValidateUserResponse, UserInfo, etc.)
    - user_pb2_grpc.py: Service classes (UserServiceServicer, UserServiceStub)

Regeneration:
    Run `bash generate_grpc.sh` to regenerate these files from protos/user.proto.
    The script automatically fixes imports to use relative imports.

Usage:
    # Server-side (grpc_server.py)
    from grpc_generated import user_pb2, user_pb2_grpc
    
    # Client-side (other services)
    from grpc_generated import user_pb2, user_pb2_grpc

Architecture:
    - user_pb2.py: Data structures (messages) for requests/responses
    - user_pb2_grpc.py: Service interface (UserServiceServicer for server, UserServiceStub for client)

Note:
    This is the SERVER-SIDE package for UserService.
    Other services import this as a CLIENT to call UserService.
"""

# Import all generated modules for convenient access
try:
    from . import user_pb2
    from . import user_pb2_grpc
    
    __all__ = [
        'user_pb2',
        'user_pb2_grpc',
    ]
except ImportError as e:
    # If imports fail, the generated files don't exist yet
    # Run generate_grpc.sh to create them
    import warnings
    warnings.warn(
        f"gRPC generated files not found: {e}\n"
        "Run 'bash generate_grpc.sh' to generate gRPC code from protos/user.proto",
        ImportWarning
    )
    __all__ = []
EOF
fi

echo "✅ Generated grpc_generated/user_pb2.py"
echo "✅ Generated grpc_generated/user_pb2_grpc.py"
echo "✅ Import fixes applied"
echo ""
