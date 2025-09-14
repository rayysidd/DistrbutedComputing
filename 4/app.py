from flask import Flask, jsonify
import numpy as np
import time

app = Flask(__name__)

@app.route("/multiprocessing")
def processing_invert():
    N = 1000  # smaller size for demo
    # Well-conditioned diagonally dominant matrix
    A = np.random.rand(N, N) + N * np.eye(N)
    
    t0 = time.time()
    # Just do normal inversion; Gunicorn workers handle multiprocessing
    result = np.linalg.inv(A)
    t1 = time.time()
    
    verification = np.allclose(np.dot(A, result), np.eye(N))
    
    return jsonify({
        "status": "ok",
        "method": "Multiprocessing (Gunicorn workers)",
        "execution_time_sec": round(t1 - t0, 4),
        "matrix_size": f"{N}x{N}",
        "verification_passed": verification,
        "sample_original": A[0, :5].tolist(),
        "sample_inverted": result[0, :5].tolist()
    })

@app.route("/threading")
def processing_threading():
    N = 1000
    A = np.random.rand(N, N) + N * np.eye(N)
    
    t0 = time.time()
    # Single-threaded; Gunicorn threads will handle concurrency
    result = np.linalg.inv(A)
    t1 = time.time()
    
    verification = np.allclose(np.dot(A, result), np.eye(N))
    
    return jsonify({
        "status": "ok",
        "method": "Multithreading (Gunicorn threads)",
        "execution_time_sec": round(t1 - t0, 4),
        "matrix_size": f"{N}x{N}",
        "verification_passed": verification,
        "sample_original": A[0, :5].tolist(),
        "sample_inverted": result[0, :5].tolist()
    })

@app.route("/")
def index():
    return "Matrix Inversion API"
