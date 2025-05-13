#!/usr/bin/env python3
import requests
import json
import logging
import argparse
import sys
import re

def get_payurl(lnaddress):
    try:
        parts = lnaddress.split('@')
        domain = parts[1]
        username = parts[0]
        transform_url = "https://" + domain + "/.well-known/lnurlp/" + username
        logging.info("Transformed URL:" + transform_url)
        return transform_url
    except Exception as e: 
        logging.error("Exception, possibly malformed LN Address: " + str(e))
        return {'status' : 'error', 'msg' : 'Possibly a malformed LN Address'}

def get_url(path, headers):
    response = requests.get(path, headers=headers)
    return response.text

def get_bolt11(lnaddress, amount):
    try: 
        purl = get_payurl(lnaddress)
        json_content = get_url(path=purl, headers={})
        datablock = json.loads(json_content)

        lnurlpay = datablock["callback"]
        min_amount = datablock["minSendable"]
        max_amount = datablock["maxSendable"]

        logging.info("min. amount: " + str(min_amount))
        logging.info("max. amount: " + str(max_amount))

        payquery = lnurlpay + "?amount=" + str(min_amount)
        if amount is not None:
            amount_msat = int(amount * 1000)
            if amount_msat > max_amount:
                raise ValueError("Amount is more than maximum sendable")        
            if amount_msat >= int(min_amount):
                payquery = lnurlpay + "?amount=" + str(amount_msat)
            else:
                raise ValueError("Amount is less than minimum sendable, you may pay in more than a single invoice")        

        logging.info("amount: " + str(amount))
        logging.info("payquery: " + str(payquery))

        ln_res = get_url(path=payquery, headers={})
        pr_dict = json.loads(ln_res)

        if 'pr' in pr_dict: 
            bolt11 = pr_dict['pr']
            ubolt11 = bolt11.upper()
            return ubolt11

        elif 'reason' in pr_dict: 
            reason = pr_dict['reason']
            return reason

    except Exception as e: 
        logging.error("in get bolt11 : "  + str(e))
        return {'status': 'error', 'msg': 'Cannot make a Bolt11, are you sure the address `' + str(lnaddress) + '` is valid and the amount withing the allowed range [' + str(int(min_amount // 1000)) + '; ' + str(int(max_amount // 1000)) + '] Satoshi?'}

def parse_positional_args(argv):
    lnaddress = None
    amount = None

    for arg in argv:
        # Detect email-like LN address (must contain one @ and at least one dot after it)
        if re.match(r"^[^@]+@[^@]+\.[^@]+$", arg):
            lnaddress = arg
        # Detect valid integer amount (non-negative)
        elif arg.isdigit():
            amount = int(arg)

    return lnaddress, amount

def main():
    # Try to detect lnaddress and amount from positional args
    detected_lnaddress, detected_amount = parse_positional_args(sys.argv[1:])

    parser = argparse.ArgumentParser(description="Send a Lightning payment.")
    parser.add_argument("-r", "--lnaddress", help="Lightning Address")
    parser.add_argument("-a", "--amount", type=int, help="Desired amount (integer)")

    # Unpacking of parse_known_args()
    args, _ = parser.parse_known_args()

    # Access parsed arguments safely
    lnaddress = args.lnaddress or detected_lnaddress or input("Enter your Lightning Address: ")
    amount = args.amount or detected_amount

    # Prompt for amount only if still missing
    if amount is None:
        while True:
            user_input = input("Enter amount (integer): ")
            if user_input.isdigit():
                amount = int(user_input)
                break
            else:
                print("Amount must be a non-negative integer.")

    bolt11 = get_bolt11(lnaddress, amount)
    print(f"Generated bolt11: {bolt11}")

if __name__ == "__main__":
    main()
