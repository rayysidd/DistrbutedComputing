import grpc
import arithmetic_pb2
import arithmetic_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = arithmetic_pb2_grpc.ArithmeticStub(channel)

        # Addition
        response = stub.Addition(arithmetic_pb2.TwoNumbers(a=15, b=7))
        print(f"Addition(15, 7) = {response.value}")

        # Subtraction
        response = stub.Subtraction(arithmetic_pb2.TwoNumbers(a=30, b=12))
        print(f"Subtraction(30, 12) = {response.value}")

        # Multiplication
        response = stub.Multiplication(arithmetic_pb2.TwoNumbers(a=6, b=8))
        print(f"Multiplication(6, 8) = {response.value}")

if __name__ == '__main__':
    run()
