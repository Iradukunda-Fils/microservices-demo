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
