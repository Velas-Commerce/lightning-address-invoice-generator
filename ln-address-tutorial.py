"""
Lightning Address to BOLT11 Invoice Generator - Tutorial

This tutorial demonstrates how to convert a Lightning Address (like user@domain.com) 
into a BOLT11 invoice that can be used to receive Lightning Network payments.

The process follows these main steps:
1. Parse the Lightning Address to extract username and domain
2. Build the LNURL-pay discovery URL following the standard format
3. Fetch the payment parameters from the Lightning service
4. Generate the actual invoice with the specified amount
5. Return the BOLT11 invoice string

Educational Note: Lightning Addresses use the LNURL-pay protocol under the hood,
which provides a user-friendly way to request Lightning payments.
"""

import requests
import json

def build_lnurl_pay_url(lightning_address):
    """
    STEP 1: Convert Lightning Address to LNURL-pay Discovery URL
    
    Lightning Address format: username@domain.com
    LNURL-pay URL format: https://domain.com/.well-known/lnurlp/username
    
    This follows the Lightning Address specification (LUD-16) which defines
    how to discover the LNURL-pay endpoint from a simple email-like address.
    """
    print(f"\n=== STEP 1: Converting Lightning Address to Discovery URL ===")
    print(f"Input Lightning Address: {lightning_address}")
    
    # Split the address at the @ symbol to separate username and domain
    address_parts = lightning_address.split('@')
    
    # Basic validation - Lightning Address should have exactly one @
    if len(address_parts) != 2:
        print("❌ Error: Invalid Lightning Address format. Should be username@domain.com")
        return None
        
    username = address_parts[0]  # Part before @
    domain = address_parts[1]    # Part after @
    
    print(f"  → Username: {username}")
    print(f"  → Domain: {domain}")
    
    # Build the LNURL-pay discovery URL according to the standard
    discovery_url = f"https://{domain}/.well-known/lnurlp/{username}"
    print(f"  → Generated Discovery URL: {discovery_url}")
    
    return discovery_url

def fetch_payment_parameters(discovery_url):
    """
    STEP 2: Fetch Payment Parameters from Lightning Service
    
    The discovery URL returns JSON with information about:
    - callback: The URL to call to generate the actual invoice
    - minSendable: Minimum amount that can be sent (in millisatoshis)
    - maxSendable: Maximum amount that can be sent (in millisatoshis)
    - metadata: Description and other payment details
    """
    print(f"\n=== STEP 2: Fetching Payment Parameters ===")
    print(f"Requesting payment info from: {discovery_url}")
    
    # Make HTTP GET request to the discovery URL
    response = requests.get(discovery_url)
    print(f"  → HTTP Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Error: Failed to fetch payment parameters (HTTP {response.status_code})")
        return None
    
    # Parse the JSON response  
    payment_params = json.loads(response.text)
    print(f"  → Response received successfully!")
    
    # Extract the important parameters
    callback_url = payment_params.get("callback")
    min_sendable = payment_params.get("minSendable")  # in millisatoshis
    max_sendable = payment_params.get("maxSendable")  # in millisatoshis
    
    print(f"  → Callback URL: {callback_url}")
    print(f"  → Min sendable: {min_sendable} millisats ({min_sendable/1000} sats)")
    print(f"  → Max sendable: {max_sendable} millisats ({max_sendable/1000} sats)")
    
    return {
        'callback': callback_url,
        'minSendable': min_sendable,
        'maxSendable': max_sendable
    }

def generate_invoice(callback_url, amount_sats, min_sendable):
    """
    STEP 3: Generate the Actual BOLT11 Invoice
    
    Now we call the callback URL with our desired amount to get the BOLT11 invoice.
    The amount must be converted to millisatoshis (multiply by 1000).
    """
    print(f"\n=== STEP 3: Generating BOLT11 Invoice ===")
    print(f"Requesting invoice for {amount_sats} sats")
    
    # Convert satoshis to millisatoshis (Lightning protocol uses millisats)
    amount_millisats = amount_sats * 1000
    print(f"  → Amount in millisats: {amount_millisats}")
    
    # Use the higher of requested amount or minimum required amount
    final_amount = max(amount_millisats, min_sendable)
    if final_amount != amount_millisats:
        print(f"  → Adjusted to minimum: {final_amount} millisats ({final_amount/1000} sats)")
    
    # Build the callback URL with the amount parameter
    invoice_request_url = f"{callback_url}?amount={final_amount}"
    print(f"  → Invoice request URL: {invoice_request_url}")
    
    # Request the actual invoice
    response = requests.get(invoice_request_url)
    print(f"  → HTTP Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Error: Failed to generate invoice (HTTP {response.status_code})")
        return None
    
    # Parse the response
    invoice_response = json.loads(response.text)
    
    # Check if we got a valid invoice
    if 'pr' in invoice_response:
        bolt11_invoice = invoice_response['pr']
        print(f"  ✅ Invoice generated successfully!")
        print(f"  → BOLT11 length: {len(bolt11_invoice)} characters")
        return bolt11_invoice.upper()  # Convert to uppercase for consistency
    
    elif 'reason' in invoice_response:
        error_reason = invoice_response['reason']
        print(f"❌ Error from Lightning service: {error_reason}")
        return None
    
    else:
        print(f"❌ Error: Unexpected response format")
        return None

def create_lightning_invoice(lightning_address, amount_sats):
    """
    Main function that orchestrates the entire process of converting
    a Lightning Address into a BOLT11 invoice.
    """
    print("⚡Lightning Address to BOLT11 Invoice Generator")
    print("=" * 55)
    
    # Step 1: Convert Lightning Address to discovery URL
    discovery_url = build_lnurl_pay_url(lightning_address)
    if not discovery_url:
        return None
    
    # Step 2: Fetch payment parameters from the Lightning service
    payment_params = fetch_payment_parameters(discovery_url)
    if not payment_params:
        return None
    
    # Step 3: Generate the actual BOLT11 invoice
    bolt11_invoice = generate_invoice(
        payment_params['callback'], 
        amount_sats, 
        payment_params['minSendable']
    )
    
    return bolt11_invoice

def main():
    """
    Interactive tutorial - walks the user through creating a Lightning invoice
    """
    print("Welcome to the Lightning Address Invoice Generator Tutorial!")
    print("This will show you exactly how Lightning Addresses work.\n")
    
    # Get user input
    lightning_address = input("Enter a Lightning Address (e.g., user@domain.com): ")
    amount_input = input("Enter amount in satoshis: ")
    
    # Convert amount to integer
    amount_sats = int(amount_input)
    
    # Generate the invoice
    bolt11_invoice = create_lightning_invoice(lightning_address, amount_sats)
    
    # Display results
    print(f"\n" + "=" * 55)
    print("🎉 FINAL RESULT")
    print("=" * 55)
    
    if bolt11_invoice:
        print(f"✅ Successfully generated BOLT11 invoice!")
        print(f"📄 Invoice: {bolt11_invoice}")
        print(f"\nThis invoice can now be used with any Lightning wallet to receive payment.")
    else:
        print("❌ Failed to generate invoice. Please check the Lightning Address and try again.")

if __name__ == "__main__":
    main()