import requests
import lnurl

def get_lnurlp_response(decode_endpoint):
    try:
        response = requests.get(decode_endpoint)
        response.raise_for_status()
        return response.json()
    except (requests.HTTPError, ValueError) as e:
        print(f"Error decoding LNURLp: {e}")
        return None

# Example usage
decode_endpoint = "https://getalby.com/.well-known/lnurlp/ealvar13"  # Replace with the actual decode endpoint URL

response = get_lnurlp_response(decode_endpoint)
print(response)

# Replace with the URL you received from your previous call
decoded_url = "https://getalby.com/lnurlp/ealvar13/callback"

# Encode the URL into a LNURL string
encoded_lnurl = lnurl.encode(decoded_url)

print(encoded_lnurl)
