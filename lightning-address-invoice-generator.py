#!/usr/bin/env python3
import requests
import json
import logging
import argparse

def get_payurl(email):
    try:
        parts = email.split('@')
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

def get_bolt11(email, amount):
    try: 
        purl = get_payurl(email)
        json_content = get_url(path=purl, headers={})
        datablock = json.loads(json_content)

        lnurlpay = datablock["callback"]
        min_amount = datablock["minSendable"]

        payquery = lnurlpay + "?amount=" + str(min_amount)
        if amount is not None:
            if int(amount*1000) > int(min_amount):
                payquery = lnurlpay + "?amount=" + str(amount*1000)
        
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
        return {'status': 'error', 'msg': 'Cannot make a Bolt11, are you sure the address is valid?'}

def main():
    parser = argparse.ArgumentParser(description="Send a Lightning payment.")
    parser.add_argument("-r", "--lnaddress", help="Lightning Address")
    parser.add_argument("-a", "--amount", type=int, help="Desired amount")

    args = parser.parse_args()

    lnaddress = args.lnaddress if args.lnaddress else input("Enter your Lightning Address: ")
    amount = args.amount if args.amount else int(input("Enter amount: "))

    bolt11 = get_bolt11(lnaddress, amount)
    print(f"Generated bolt11: {bolt11}")

if __name__ == "__main__":
    main()
