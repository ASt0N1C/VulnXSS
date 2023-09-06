import time
import requests
import re
from subprocess import run

# Shared data structure to store injected URLs (e.g., a file or database)
INJECTED_URLS_FILE = 'injected_urls.txt'
# Path to Xss_Payloads.txt
PAYLOADS_FILE = 'Xss_Payloads.txt'


# Function to load payloads from Xss_Payloads.txt
def load_payloads():
    with open(PAYLOADS_FILE, 'r') as f:
        payloads = [line.strip() for line in f.readlines()]
    return payloads


# Function to check for XSS using payloads
def check_for_xss(url, payloads):
    try:
        # Perform an HTTP request to the injected URL
        response = requests.get(url)
        response_content = response.text

        # Check for signs of XSS vulnerabilities in response_content
        for payload in payloads:
            if re.search(re.escape(payload), response_content):
                return True
        return False

    except Exception as e:
        print(f"Error checking {url}: {str(e)}")
        return False


# Function to send an alert using alert.py
def send_alert(url):
    run(["python", "alert.py", "XSS Detected", f"Potential XSS detected in: {url}"])


def check_injected_urls():
    payloads = load_payloads()

    while True:
        # Read injected URLs from the shared data structure (e.g., a file)
        with open(INJECTED_URLS_FILE, 'r') as f:
            injected_urls = f.read().splitlines()

        for url in injected_urls:
            if check_for_xss(url, payloads):
                # Potential XSS detected, send an alert
                send_alert(url)

        # Sleep for a period before checking again (adjust as needed)
        time.sleep(60)


if __name__ == "__main__":
    check_injected_urls()
