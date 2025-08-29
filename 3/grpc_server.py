import grpc
from concurrent import futures
import sort_pb2
import sort_pb2_grpc

class SortServicer(sort_pb2_grpc.SortServiceServicer):
    def Sort(self,request,context):
        sorted_arr = sorted(request.arr)
        return sort_pb2.Result(arr=sorted_arr)
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    sort_pb2_grpc.add_SortServiceServicer_to_server(SortServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC Server running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

