import grpc
import time
import os
import psutil
import sort_pb2
import sort_pb2_grpc

def benchmark(num_requests=1000):
    process = psutil.Process(os.getpid())

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = sort_pb2_grpc.SortServiceStub(channel)

        # Test payload
        arr = list(range(100, 0, -1))  # 100 integers (descending)

        # Measure size of request + response
        request_proto = sort_pb2.Array(arr=arr)
        response_proto = sort_pb2.Result(arr=arr)
        size_request = len(request_proto.SerializeToString())
        size_response = len(response_proto.SerializeToString())
        total_size_per_call = size_request + size_response

        # Warmup (avoid startup overhead)
        stub.Sort(request_proto)

        # CPU before benchmark
        cpu_before = process.cpu_percent(interval=None)

        start = time.time()
        for _ in range(num_requests):
            stub.Sort(request_proto)
        end = time.time()

        # CPU after benchmark
        cpu_after = process.cpu_percent(interval=None)

        # Metrics
        total_time = end - start
        avg_latency = (total_time / num_requests) * 1000  # ms
        total_bandwidth = total_size_per_call * num_requests / 1024  # KB approx

        print("\n=== gRPC Benchmark Results ===")
        print(f"Requests: {num_requests}")
        print(f"Payload size (req+res): {total_size_per_call} bytes")
        print(f"Total bandwidth used: {total_bandwidth:.2f} KB")
        print(f"Total time: {total_time:.4f} seconds")
        print(f"Average latency: {avg_latency:.2f} ms per request")
        print(f"CPU utilization (process): {cpu_after - cpu_before:.2f}%\n")

if __name__ == '__main__':
    benchmark(100)  # change to 100, 1000, etc.
