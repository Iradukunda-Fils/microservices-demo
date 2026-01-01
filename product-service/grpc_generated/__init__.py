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
