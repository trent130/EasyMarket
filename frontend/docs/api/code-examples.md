# API Usage Examples

This document provides code examples for common API usage scenarios in various programming languages.

## Authentication

### User Registration (Python)

```python
import requests

url = "https://api.example.com/v1/auth/register"
data = {
    "email": "user@example.com",
    "password": "securePassword123!",
    "name": "John Doe"
}

response = requests.post(url, json=data)

if response.status_code == 201:
    print("User registered successfully")
    print(response.json())
else:
    print("Error:", response.json()["error"])
```

### User Login (JavaScript)

```javascript
async function login(email, password) {
  const response = await fetch('https://api.example.com/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('accessToken', data.accessToken);
    return data;
  } else {
    const errorData = await response.json();
    throw new Error(errorData.error);
  }
}

// Usage
login('user@example.com', 'securePassword123!')
  .then(data => console.log('Logged in successfully', data))
  .catch(error => console.error('Login failed', error));
```

## User Profile

### Get User Profile (Ruby)

```ruby
require 'net/http'
require 'json'

def get_user_profile(access_token)
  uri = URI('https://api.example.com/v1/user/profile')
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true

  request = Net::HTTP::Get.new(uri)
  request['Authorization'] = "Bearer #{access_token}"

  response = http.request(request)

  if response.code == '200'
    JSON.parse(response.body)
  else
    raise "Error: #{JSON.parse(response.body)['error']}"
  end
end

# Usage
begin
  profile = get_user_profile('your_access_token_here')
  puts "User profile: #{profile}"
rescue StandardError => e
  puts e.message
end
```

## Two-Factor Authentication

### Enable 2FA (Java)

```java
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;

public class Enable2FA {
    public static void main(String[] args) {
        String accessToken = "your_access_token_here";
        String apiUrl = "https://api.example.com/v1/auth/2fa/enable";

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(apiUrl))
                .header("Authorization", "Bearer " + accessToken)
                .POST(HttpRequest.BodyPublishers.noBody())
                .build();

        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                System.out.println("2FA enabled successfully");
                System.out.println(response.body());
            } else {
                System.out.println("Error: " + response.body());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

## Data Export

### Request Data Export (Go)

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

func requestDataExport(accessToken string) error {
    url := "https://api.example.com/v1/user/data-export"
    
    client := &http.Client{}
    req, err := http.NewRequest("POST", url, nil)
    if err != nil {
        return err
    }
    
    req.Header.Add("Authorization", "Bearer "+accessToken)
    
    resp, err := client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode == http.StatusOK {
        var result map[string]interface{}
        json.NewDecoder(resp.Body).Decode(&result)
        fmt.Println("Data export requested successfully:", result)
    } else {
        var errorResult map[string]string
        json.NewDecoder(resp.Body).Decode(&errorResult)
        return fmt.Errorf("Error: %s", errorResult["error"])
    }
    
    return nil
}

func main() {
    accessToken := "your_access_token_here"
    err := requestDataExport(accessToken)
    if err != nil {
        fmt.Println(err)
    }
}
```

These examples demonstrate basic usage of the API for common scenarios. Remember to replace  with an actual access token in real-world usage, and always handle errors and edge cases appropriately in production code.

