import requests
import os

BASE_URL = "http://localhost:8000"

def test_backend():
    print("Running backend verification...")
    email = "testuser@example.com"
    password = "securepassword123"

    # 1. Signup
    print("1. Testing Signup...")
    signup_data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if response.status_code == 200:
        print("   Signup successful")
        token = response.json().get("access_token")
    elif response.status_code == 400 and "Email already registered" in response.text:
        print("   User already exists, proceeding to login...")
        # Login if already exists
        response = requests.post(f"{BASE_URL}/auth/login", json=signup_data)
        token = response.json().get("access_token")
    else:
        print(f"   Signup failed: {response.text}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login (Explicit check)
    print("2. Testing Login...")
    response = requests.post(f"{BASE_URL}/auth/login", json=signup_data)
    if response.status_code == 200:
        print("   Login successful")
    else:
        print(f"   Login failed: {response.text}")
        return

    # 3. Get User Me
    print("3. Testing Get Me...")
    response = requests.get(f"{BASE_URL}/api/me", headers=headers)
    if response.status_code == 200:
        print(f"   Get Me successful: {response.json()['email']}")
    else:
        print(f"   Get Me failed: {response.text}")

    # 4. Update Profile
    print("4. Testing Update Profile...")
    profile_data = {
        "full_name": "Test User",
        "role": "QA Engineer",
        "skills": ["Testing", "Python"]
    }
    response = requests.put(f"{BASE_URL}/api/profile", json=profile_data, headers=headers)
    if response.status_code == 200:
        print("   Profile Update successful")
        updated_profile = response.json()
        if updated_profile["role"] == "QA Engineer":
            print("   Profile data verified")
    else:
        print(f"   Profile Update failed: {response.text}")

    # 5. Upload Certificate
    print("5. Testing Certificate Upload...")
    # Create dummy file
    with open("test_cert.txt", "w") as f:
        f.write("This is a test certificate content.")
    
    files = {'file': ('test_cert.txt', open('test_cert.txt', 'rb'), 'text/plain')}
    response = requests.post(f"{BASE_URL}/api/upload", files=files, headers=headers)
    
    if response.status_code == 200:
        print("   Upload successful")
        print(f"   File URL: {response.json()['url']}")
    else:
        print(f"   Upload failed: {response.text}")
    
    # Cleanup
    try:
        os.remove("test_cert.txt")
    except:
        pass

if __name__ == "__main__":
    try:
        test_backend()
    except Exception as e:
        print(f"Verification failed with exception: {e}")
        print("Make sure the server is running on localhost:8000")
