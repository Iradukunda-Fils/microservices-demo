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
