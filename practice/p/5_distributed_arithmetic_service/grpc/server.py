# python -m pip install grpcio grpcio-tools
# python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. arithmetic.proto

import grpc
from concurrent import futures
import time

import arithmetic_pb2
import arithmetic_pb2_grpc

# Implement the Arithmetic service
class ArithmeticServicer(arithmetic_pb2_grpc.ArithmeticServicer):
    
    def Addition(self, request, context):
        print(f"Received remote call: ADD({request.a}, {request.b})")
        return arithmetic_pb2.Result(value=request.a + request.b)

    def Subtraction(self, request, context):
        print(f"Received remote call: SUBTRACT({request.a}, {request.b})")
        return arithmetic_pb2.Result(value=request.a - request.b)

    def Multiplication(self, request, context):
        print(f"Received remote call: MULTIPLY({request.a}, {request.b})")
        return arithmetic_pb2.Result(value=request.a * request.b)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    arithmetic_pb2_grpc.add_ArithmeticServicer_to_server(ArithmeticServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Arithmetic gRPC service listening on port 50051...")
    server.start()
    try:
        while True:
            time.sleep(86400)  # keep server alive
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
