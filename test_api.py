import requests
import json
import base64

# Test the API endpoint
def test_api():
    url = "http://localhost:8000/api/"
    
    # Test 1: Basic question without image
    print("Test 1: Basic question")
    data = {
        "question": "What is the difference between gpt-4o-mini and gpt-3.5-turbo?"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer']}")
            print(f"Links: {result['links']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to API: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Question with image
    print("Test 2: Question with image")
    try:
        # Read and encode the image
        with open("project-tds-virtual-ta-q1.webp", "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        data = {
            "question": "What does this image show? How should I calculate the cost?",
            "image": image_data
        }
        
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer']}")
            print(f"Links: {result['links']}")
        else:
            print(f"Error: {response.text}")
    except FileNotFoundError:
        print("Image file not found, skipping image test")
    except Exception as e:
        print(f"Error in image test: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Health check
    print("Test 3: Health check")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Health: {result}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to health endpoint: {e}")

if __name__ == "__main__":
    print("Testing TDS Virtual TA API")
    print("Make sure to start the server with: python main.py")
    print("And set your OPENAI_API_KEY environment variable")
    print("\n" + "="*50 + "\n")
    test_api()