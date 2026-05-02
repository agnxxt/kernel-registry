import os
import socket
import time

SERVICES = [
    ("postgres", int(os.getenv("POSTGRES_PORT", "5432"))),
    ("kafka", int(os.getenv("KAFKA_PORT", "9092"))),
]

TIMEOUT = int(os.getenv("WAIT_TIMEOUT", "90"))


def wait_for(host: str, port: int, timeout: int) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=3):
                return
        except OSError:
            time.sleep(2)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


if __name__ == "__main__":
    for host, port in SERVICES:
        wait_for(host, port, TIMEOUT)
    print("All required services are reachable.")
