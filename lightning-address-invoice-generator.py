import requests

class InvoiceGenerator:
    def __init__(self, decode_endpoint):
        self.decode_endpoint = decode_endpoint

    def decode_lightning_address(self, lightning_address):
        payload = {
            "lnAddress": lightning_address
        }
        try:
            response = requests.post(self.decode_endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except (requests.HTTPError, ValueError) as e:
            print(f"Error decoding Lightning address: {e}")
            return None

    def generate_lightning_invoice(self, callback_url, amount, comment):
        invoice_url = f"{callback_url}?amount={amount}&comment={comment}"
        try:
            response = requests.get(invoice_url)
            response.raise_for_status()
            return response.json()
        except (requests.HTTPError, ValueError) as e:
            print(f"Error generating Lightning invoice: {e}")
            return None

    def pay_lightning_address(self, lightning_address, amount, comment):
        response = self.decode_lightning_address(lightning_address)

        if response and response["status"] == "OK":
            callback_url = response["callback"]
            invoice_response = self.generate_lightning_invoice(callback_url, amount, comment)

            if invoice_response and invoice_response["status"] == "OK":
                invoice = invoice_response["invoice"]
                # Process the generated invoice as needed
                print("Received Lightning invoice:", invoice)
            else:
                print("Failed to generate Lightning invoice")
        else:
            print("Failed to decode Lightning address")

# Example usage
decode_endpoint = "https://your-decode-endpoint.com"  # Replace with the actual decode endpoint URL
invoice_gen = InvoiceGenerator(decode_endpoint)

lightning_address = "alice@lightningaddress.com"
amount = 1000  # Satoshis
comment = "Payment for goods"

invoice_gen.pay_lightning_address(lightning_address, amount, comment)
