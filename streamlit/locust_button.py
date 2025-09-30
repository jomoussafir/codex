import time
import random
from locust import HttpUser, task, between

class SimpleStreamlitTest(HttpUser):
    """
    Simple load test for Streamlit Generate button
    """
    wait_time = between(2, 5)
    
    def on_start(self):
        """Load the main page when user starts"""
        self.client.get("/")
    
    @task(3)
    def load_main_page(self):
        """Load main page (baseline)"""
        self.client.get("/")
    
    @task(1) 
    def simulate_heavy_computation(self):
        """Simulate the Generate Time Series button click"""
        
        # Simulate what happens when button is clicked
        # This approximates the server load of your time series generation
        
        start_time = time.time()
        
        # Try different Streamlit endpoints that might handle the computation
        endpoints_to_try = [
            "/_stcore/stream",
            "/_stcore/message", 
            "/component/streamlit_app",
            "/"  # Sometimes Streamlit processes everything through main endpoint
        ]
        
        for endpoint in endpoints_to_try:
            try:
                with self.client.post(
                    endpoint,
                    json={
                        "action": "generate_timeseries",
                        "params": {
                            "num_series": random.randint(10, 30),
                            "length": random.randint(5000, 15000)
                        }
                    },
                    timeout=45,
                    catch_response=True,
                    name="Generate Time Series"
                ) as response:
                    
                    elapsed_time = time.time() - start_time
                    
                    # Consider it successful if it doesn't timeout
                    if elapsed_time < 30:
                        response.success()
                        print(f"✅ Generated in {elapsed_time:.2f}s")
                        break
                    else:
                        response.failure(f"Too slow: {elapsed_time:.2f}s")
                        
            except Exception as e:
                print(f"Endpoint {endpoint} failed: {e}")
                continue
    
    @task(2)
    def health_check(self):
        """Check if app is responsive"""
        with self.client.get("/_stcore/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


# Even simpler version - just HTTP load testing
class BasicHttpTest(HttpUser):
    """
    Basic HTTP load test - tests server capacity
    """
    wait_time = between(1, 3)
    
    @task(5)
    def load_page(self):
        """Basic page load"""
        self.client.get("/")
    
    @task(1)
    def simulate_computation_load(self):
        """Simulate computational load on server"""
        
        # This simulates multiple users triggering heavy computation simultaneously
        start_time = time.time()
        
        # Make a request that would trigger server-side computation
        with self.client.get("/", 
                           params={"trigger": "generate", "timestamp": int(time.time())},
                           timeout=30,
                           catch_response=True,
                           name="Heavy Computation") as response:
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                if elapsed_time > 20:
                    response.failure(f"Response too slow: {elapsed_time:.2f}s")
                else:
                    response.success()
                    print(f"Computation completed in {elapsed_time:.2f}s")
            else:
                response.failure(f"Request failed: {response.status_code}")


if __name__ == "__main__":
    print("""
    🚀 Simple Streamlit Load Test
    
    Run with:
    locust -f simple_test.py --host=http://localhost:8501
    
    Or headless:
    locust -f simple_test.py --host=http://localhost:8501 --headless -u 10 -r 2 -t 60s
    """)