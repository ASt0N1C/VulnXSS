import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import hashlib
import time
from Alert import process_alerts
from Smtp import send_email  # Assuming Smtp.py contains the email sending logic

# ASCII art banner
print("""
 ________                     __      __  ________          __                               
|        \                   |  \    |  \|        \        |  \                              
| $$$$$$$$______    ______  _| $$_    \$$| $$$$$$$$______  | $$  _______   ______   _______  
| $$__   /      \  /      \|   $$ \  |  \| $$__   |      \ | $$ /       \ /      \ |       \ 
| $$  \ |  $$$$$$\|  $$$$$$\\$$$$$$  | $$| $$  \   \$$$$$$\| $$|  $$$$$$$|  $$$$$$\| $$$$$$$\
| $$$$$ | $$  | $$| $$   \$$ | $$ __ | $$| $$$$$  /      $$| $$| $$      | $$  | $$| $$  | $$
| $$    | $$__/ $$| $$       | $$|  \| $$| $$    |  $$$$$$$| $$| $$_____ | $$__/ $$| $$  | $$
| $$     \$$    $$| $$        \$$  $$| $$| $$     \$$    $$| $$ \$$     \ \$$    $$| $$  | $$
 \$$      \$$$$$$  \$$         \$$$$  \$$ \$$      \$$$$$$$ \$$  \$$$$$$$  \$$$$$$  \$$   \$$
""")

# Domains to exclude
excluded_domains = ["youtube.com", "itunes.com", "accounts.google.com", "facebook.com", "instagram.com", "twitter.com", "Tiktok.com", "quotestreampro.com", "zacks.com", "businesswire.com", "tradeshownews.com", "linkedin.com", "incommconferencing.com", "quotemedia.com", "networkadvertising.org", "telegram.org", "discord.com", "medium.com", "github.com"]

# URLs that should not be scanned
excluded_urls = set()

# List to store injected payloads and their associated URLs
injected_payloads = []

# Function to extract all links from a webpage
def extract_links(url):
    try:
        response = session.get(url)
        if response.status_code == 403:
            excluded_urls.add(url)
            return []
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True) if not any(domain in a.get('href') for domain in excluded_domains)]
        return links
    except Exception as e:
        print(f"Error while extracting links from {url}: {str(e)}")
        return []

# Function to find and analyze forms for potential XSS
def find_forms(url):
    try:
        response = session.get(url)
        if response.status_code == 403:
            excluded_urls.add(url)
            return
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.find_all('form')
        for form in forms:
            form_hash = hashlib.sha1(str(form).encode()).hexdigest()
            if form_hash not in visited_forms:
                visited_forms.add(form_hash)
                analyze_form(url, form)
    except Exception as e:
        print(f"Error while analyzing forms on {url}: {str(e)}")

# Function to analyze a form for potential XSS
def analyze_form(url, form):
    try:
        action = form.get('action')
        method = form.get('method')
        inputs = form.find_all(['input', 'textarea'])

        print(f"Form found on {url}")
        print(f"Action: {action}")
        print(f"Method: {method}")

        for input_tag in inputs:
            name = input_tag.get('name')
            input_type = input_tag.get('type')
            if input_type != 'hidden':
                print(f"Input field: {name}")
                inject_xss_payloads(url, form, name)
    except Exception as e:
        print(f"Error while analyzing form on {url}: {str(e)}")

# Function to inject XSS payloads into form fields
def inject_xss_payloads(url, form, field_name):
    try:
        with open('Xss_Payloads.txt', 'r') as payload_file:
            payloads = payload_file.readlines()

        for payload in payloads:
            payload = payload.strip()
            form_data = {}
            form_data[field_name] = payload
            print(f"Injecting Payload: {payload} into {field_name}")
            response = session.post(urljoin(url, form.get('action')), data=form_data)

            # Check for XSS and popups using the Alert module
            process_alerts(response.text, payload)

            if payload in response.text:
                print(f"XSS Payload detected in {field_name}: {payload}")
                # Send email when XSS is detected
                send_email("XSS Detected", f"XSS Payload detected in {field_name} on {url}: {payload}")
                # Store the URL and injected payload for later checking
                injected_payloads.append((url, payload))
                # Check for popups or windows created by the payload after a delay
                time.sleep(15)
                check_for_popups()
    except Exception as e:
        if "403" not in str(e):  # Skip logging/showing for 403 errors
            print(f"Error while injecting XSS payloads into {field_name}: {str(e)}")

# Function to check for stored XSS on previously injected URLs
def check_for_stored_xss():
    for url, payload in injected_payloads:
        try:
            response = session.get(url)
            if payload in response.text:
                print(f"Stored XSS Payload detected on {url}: {payload}")
                # Send email when stored XSS is detected
                send_email("Stored XSS Detected", f"Stored XSS Payload detected on {url}: {payload}")
        except Exception as e:
            print(f"Error while checking for stored XSS on {url}: {str(e)}")

# Function to check for popups or windows created by the payload
def check_for_popups():
    try:
        # Execute JavaScript code to check for popups or windows
        popup_check_script = """
        var popupCheck = false;
        for (var i = 0; i < window.length; i++) {
            if (window[i] !== window.top) {
                popupCheck = true;
                break;
            }
        }
        return popupCheck;
        """

        response = session.execute_script(popup_check_script)
        if response:
            print("Popup or window detected created by the XSS payload.")
        else:
            print("No popups or windows detected.")
    except Exception as e:
        print(f"Error while checking for popups: {str(e)}")

# Function to send an email
def send_email(subject, message):
    sender_email = "hackeronetesting12331@gmail.com"
    sender_password = "fifmwjythzeyiwmr"
    receiver_email = "hackeronetesting12331@gmail.com"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    body = message
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error while sending email: {str(e)}")

# Function to recursively scan and test for vulnerabilities
def scan_and_test(target_url, max_depth=5):
    visited = set()
    queue = [(target_url, 0)]

    while queue:
        current_url, depth = queue.pop(0)
        if current_url in excluded_urls:
            continue
        visited.add(current_url)

        print(f"Scanning {current_url}, Depth: {depth}")

        if depth >= max_depth:
            continue

        links = extract_links(current_url)

        print(f"Links found on {current_url}:")
        for link in links:
            print(link)

        find_forms(current_url)

        for link in links:
            if link not in visited and link.startswith("http"):
                queue.append((link, depth + 1))

if __name__ == "__main__":
    target_url = input("Enter the target URL (e.g., http://example.com): ")
    max_depth = int(input("Enter the maximum depth for scanning: "))
    session = requests.Session()
    visited_forms = set()
    scan_and_test(target_url, max_depth)
    # Check for stored XSS after scanning
    check_for_stored_xss()