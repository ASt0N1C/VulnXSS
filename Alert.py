import time
from Smtp import send_email

# Function to check for reflected XSS
def check_reflected_xss(response_text, injected_payload):
    # Check if the injected payload is present in the response
    if injected_payload in response_text:
        print(f"Reflected XSS Detected: {injected_payload}")
        send_email("Reflected XSS Detected", f"Reflected XSS detected with payload: {injected_payload}")

# Function to check for popup windows
def check_for_popups(response_text):
    # Example: Check if the response text contains a common popup-triggering event like 'alert'
    if "alert(" in response_text:
        print("Popup or window detected.")
        send_email("Popup Detected", "A popup or window was detected on the page.")

# Function to check for XSS vulnerabilities
def check_for_xss(response_text, injected_payload):
    # Check if the injected payload is present in the response
    if injected_payload in response_text:
        print(f"XSS Detected: {injected_payload}")
        send_email("XSS Detected", f"XSS detected with payload: {injected_payload}")

# Main function to process alerts
def process_alerts(response_text, injected_payload):
    check_reflected_xss(response_text, injected_payload)
    check_for_popups(response_text)
    check_for_xss(response_text, injected_payload)

# Example usage of the functions in Alert.py
if __name__ == "__main__":
    response_text = "Sample response text containing injected payload alert('XSS')"
    injected_payload = "alert('XSS')"

    process_alerts(response_text, injected_payload)