# locustfile.py
import time
import json
from locust import HttpUser, task, between
from locust.contrib.fasthttp import FastHttpUser
import websocket
import threading

class StreamlitUser(HttpUser):
    """
    Load test for Streamlit app
    Note: Streamlit uses WebSockets, so this is a simplified HTTP-only test
    """
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        # Get the main page first
        self.client.get("/")
        
        # Get Streamlit's static assets
        self.client.get("/_stcore/static/css/bootstrap.min.css")
        self.client.get("/_stcore/static/js/bootstrap.min.js")
    
    @task(3)
    def load_main_page(self):
        """Load the main Streamlit page"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load main page: {response.status_code}")
    
    @task(2)
    def get_health_check(self):
        """Streamlit health check endpoint"""
        with self.client.get("/_stcore/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(1)
    def get_static_assets(self):
        """Load static assets"""
        assets = [
            "/_stcore/static/css/fonts.css",
            "/_stcore/static/favicon.ico",
        ]
        
        for asset in assets:
            with self.client.get(asset, catch_response=True) as response:
                if response.status_code in [200, 304]:  # 304 is cached
                    response.success()
                else:
                    response.failure(f"Failed to load {asset}: {response.status_code}")


# Advanced WebSocket testing (more realistic for Streamlit)
class StreamlitWebSocketUser(HttpUser):
    """
    More realistic Streamlit load test that simulates WebSocket behavior
    """
    wait_time = between(2, 5)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.ws = None
    
    def on_start(self):
        """Initialize session"""
        # Get main page and extract session info
        response = self.client.get("/")
        if response.status_code == 200:
            # In real implementation, you'd parse the HTML to get session info
            self.session_id = "simulated_session_" + str(int(time.time()))
        
        # Simulate initial WebSocket handshake
        self.simulate_websocket_handshake()
    
    def simulate_websocket_handshake(self):
        """Simulate WebSocket connection setup"""
        # This simulates what happens when Streamlit connects via WebSocket
        with self.client.get("/_stcore/stream", catch_response=True) as response:
            if response.status_code in [200, 101]:  # 101 is WebSocket upgrade
                response.success()
            else:
                response.failure(f"WebSocket handshake failed: {response.status_code}")
    
    @task(5)
    def simulate_user_interaction(self):
        """Simulate user clicking buttons, changing inputs, etc."""
        # This would simulate POST requests that Streamlit makes when users interact
        
        # Simulate button click or widget interaction
        payload = {
            "type": "user_interaction",
            "session_id": self.session_id,
            "widget_id": f"button_{int(time.time())}",
            "timestamp": time.time()
        }
        
        with self.client.post("/_stcore/message", 
                            json=payload, 
                            catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"User interaction failed: {response.status_code}")
    
    @task(2)
    def load_page_refresh(self):
        """Simulate page refresh"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Page refresh failed: {response.status_code}")
    
    def on_stop(self):
        """Clean up when user stops"""
        if self.ws:
            self.ws.close()


# Performance monitoring during load test
class StreamlitPerformanceMonitor:
    """Monitor app performance metrics during load test"""
    
    def __init__(self, app_url):
        self.app_url = app_url
        self.metrics = {
            'response_times': [],
            'error_rates': [],
            'memory_usage': [],
            'cpu_usage': []
        }
    
    def monitor_performance(self):
        """Monitor performance metrics"""
        import requests
        import psutil
        
        while True:
            try:
                # Test response time
                start_time = time.time()
                response = requests.get(self.app_url, timeout=10)
                response_time = time.time() - start_time
                
                self.metrics['response_times'].append(response_time)
                
                # Monitor system resources (if testing locally)
                self.metrics['memory_usage'].append(psutil.virtual_memory().percent)
                self.metrics['cpu_usage'].append(psutil.cpu_percent(interval=1))
                
                print(f"Response Time: {response_time:.2f}s, "
                      f"Memory: {psutil.virtual_memory().percent}%, "
                      f"CPU: {psutil.cpu_percent()}%")
                
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            time.sleep(5)  # Monitor every 5 seconds


# Custom load test scenario
class CustomStreamlitLoadTest(HttpUser):
    """Custom load test specific to your time series app"""
    wait_time = between(3, 8)  # Users wait 3-8 seconds between actions
    
    @task(1)
    def generate_time_series(self):
        """Simulate clicking the 'Run' button to generate time series"""
        
        # First load the main page
        self.client.get("/")
        
        # Simulate the heavy computation request
        # Note: Actual Streamlit apps use WebSocket messages, 
        # but this simulates the server load
        
        start_time = time.time()
        
        # Simulate the computation time for generating 20 time series of 10k points
        # This would normally be a WebSocket message, but we simulate with HTTP
        
        with self.client.post("/_stcore/component-request", 
                            json={
                                "action": "generate_timeseries",
                                "num_series": 20,
                                "length": 10000
                            },
                            timeout=30,  # Long timeout for heavy computation
                            catch_response=True) as response:
            
            elapsed_time = time.time() - start_time
            
            if elapsed_time > 10:  # If it takes more than 10 seconds
                response.failure(f"Time series generation too slow: {elapsed_time:.2f}s")
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Generation failed: {response.status_code}")


if __name__ == "__main__":
    # Example of how to run the performance monitor
    monitor = StreamlitPerformanceMonitor("http://localhost:8501")
    
    # Run in separate thread
    import threading
    monitor_thread = threading.Thread(target=monitor.monitor_performance, daemon=True)
    monitor_thread.start()
    
    print("Performance monitor started. Run 'locust -f locustfile.py' to start load test.")
    print("Press Ctrl+C to stop monitoring.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping performance monitor...")