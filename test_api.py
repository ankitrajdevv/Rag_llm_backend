import requests
import os

# Test the upload endpoint first
def test_upload():
    try:
        # Use an existing PDF file
        pdf_path = "uploads/COE0056186.pdf"
        if not os.path.exists(pdf_path):
            print("PDF file not found")
            return None
            
        with open(pdf_path, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            response = requests.post("http://127.0.0.1:8000/upload/", files=files)
            print(f"Upload response: {response.status_code}")
            print(f"Upload content: {response.text}")
            return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Upload error: {e}")
        return None

# Test the ask endpoint
def test_ask():
    try:
        data = {
            "filename": "test.pdf",
            "query": "What is this document about?",
            "username": "testuser"
        }
        response = requests.post("http://127.0.0.1:8000/ask/", data=data)
        print(f"Ask response: {response.status_code}")
        print(f"Ask content: {response.text}")
    except Exception as e:
        print(f"Ask error: {e}")

if __name__ == "__main__":
    print("Testing upload...")
    upload_result = test_upload()
    
    if upload_result:
        print("\nTesting ask...")
        test_ask()
    else:
        print("Upload failed, skipping ask test")
