import requests
import json
import time

class RunPodAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.runpod.ai/v2"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

    def get_pods(self):
        """Get list of all pods"""
        endpoint = f"{self.base_url}/get-pods"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()

    def create_pod(self, name, image_name, container_disk_in_gb=10, volume_in_gb=0, ports="80/http"):
        """Create a new pod"""
        endpoint = f"{self.base_url}/create-pod"
        payload = {
            "name": name,
            "image_name": image_name,
            "container_disk_in_gb": container_disk_in_gb,
            "volume_in_gb": volume_in_gb,
            "ports": ports
        }
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()

    def stop_pod(self, pod_id):
        """Stop a running pod"""
        endpoint = f"{self.base_url}/stop-pod"
        payload = {"pod_id": pod_id}
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()

    def resume_pod(self, pod_id):
        """Resume a stopped pod"""
        endpoint = f"{self.base_url}/resume-pod"
        payload = {"pod_id": pod_id}
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()

    def run_pod(self, pod_id, input_data):
        """Run a specific pod with input data"""
        endpoint = f"{self.base_url}/{pod_id}/run"
        data = {
            'input': input_data
        }
        try:
            response = requests.post(endpoint, headers=self.headers, json=data)
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response.text}

    def check_job_status(self, job_id):
        """Check the status of a job"""
        endpoint = f"{self.base_url}/{job_id}/status"
        try:
            response = requests.get(endpoint, headers=self.headers)
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response.text}

    def get_job_output(self, job_id):
        """Get the output of a completed job"""
        endpoint = f"{self.base_url}/{job_id}/status"
        try:
            response = requests.get(endpoint, headers=self.headers)
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response.text}

def main():
    # Get your API key from: https://www.runpod.io/console/user/settings
    # Replace this with your actual RunPod API key
    API_KEY = input("Please enter your RunPod API key: ")
    
    # Initialize the RunPod API client with your API key
    runpod = RunPodAPI(API_KEY)
    
    try:
        # Example: Run a specific pod with input data
        print("\nRunning pod with input data...")
        pod_id = "tzwg1ryfn03n0t"  # The pod ID you were invited to use
        input_data = {
            "input": {
                # Add your input parameters here
                "prompt": "What is the capital of France?",
                "max_tokens": 50
            }
        }
        result = runpod.run_pod(pod_id, input_data)
        print("Initial response:", json.dumps(result, indent=2))
        
        # Get the job ID from the response
        job_id = result.get("id")
        if job_id:
            print("\nChecking job status...")
            while True:
                status = runpod.check_job_status(job_id)
                print(f"Current status: {status.get('status')}")
                
                if status.get("status") == "COMPLETED":
                    print("\nJob completed! Getting output...")
                    output = runpod.get_job_output(job_id)
                    print("Output:", json.dumps(output, indent=2))
                    break
                elif status.get("status") in ["FAILED", "CANCELLED"]:
                    print(f"\nJob {status.get('status')}")
                    break
                
                # Wait for 2 seconds before checking again
                time.sleep(2)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 