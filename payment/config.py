import requests

def get_access_token(consumer_key, consumer_secret):
    token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate'  # Token endpoint URL

    # Construct request data
    data = {
        'grant_type': 'client_credentials',
        'client_id': consumer_key,
        'client_secret': consumer_secret
    }

    try:
        # Make request to obtain access token
        response = requests.post(token_url, data=data)

        # Check if request was successful
        if response.status_code == 200:
            # Extract and return access token from response
            return response.json().get('access_token')
        else:
            # Handle error
            print("Error obtaining access token:", response.text)
            return None
    except Exception as e:
        # Handle exception
        print("Exception occurred:", str(e))
        return None

def main():
    # Replace these with your actual consumer key and consumer secret values
    consumer_key = 'cDGYyZzGam3acgxMb8LeRHdFIBLzY5txGGW2iU6b36FPSRO5'
    consumer_secret = 'iabrvUW10ArTPBG72C9CIvS9Q2KtLHk9rkcK3RDKb90PnAbWI3UMJUbvzkiw6qsS'

    # Get access token
    access_token = get_access_token(consumer_key, consumer_secret)
    if access_token:
        print("Access token:", access_token)
        # Now you can use this access token to make authorized requests to the Safaricom Daraja API
    else:
        print("Failed to obtain access token.")

if __name__ == "__main__":
    main()
