import requests
from bs4 import BeautifulSoup
import re
import os

# --- Imports for Selenium (uncomment if you intend to use Selenium) ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time # Import time for potential waits in Selenium


def get_live_stream_url_requests(webpage_url):
    """
    Scrapes the webpage using requests and BeautifulSoup to find the live streaming M3U8 URL.
    """
    try:
        response = requests.get(webpage_url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Primary Strategy: Look for the 'data-play' attribute on the "咪咕线路" button
        migu_button = soup.find('button', {'class': 'route-btn', 'data-name': '咪咕线路'})

        if migu_button:
            m3u8_link = migu_button.get('data-play')
            if m3u8_link and 'auth=' in m3u8_link:
                print(f"Requests: Found complete M3U8 link in data-play attribute: {m3u8_link}")
                return m3u8_link
            elif m3u8_link:
                print(f"Requests: Found M3U8 link in data-play, but 'auth=' is missing. Link: {m3u8_link}")
        else:
            print("Requests: Migu button with data-name='咪咕线路' not found.")


        # Secondary Strategy: Search within script tags for the 'playUrl' variable
        print("Requests: Attempting to find M3U8 link in script tags...")
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                # Regex to capture the full URL including 'auth='
                match = re.search(r"var playUrl = '/static/ds3/dplayer.php\?url=(https:\/\/live\.huarenlivewebsite\.top\/stream\/CCTV5_MG\.m3u8\?auth=[^']+)'", script.string)
                if match:
                    extracted_url = match.group(1)
                    if 'auth=' in extracted_url:
                        print(f"Requests: Found complete M3U8 link in script tag: {extracted_url}")
                        return extracted_url
                    else:
                        print(f"Requests: Found M3U8 link in script tag, but 'auth=' is missing. Link: {extracted_url}")

        print("Requests: No complete M3U8 link with 'auth=' found using requests/BeautifulSoup.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Requests: Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"Requests: An unexpected error occurred: {e}")
        return None


def get_live_stream_url_selenium(webpage_url):
    """
    Scrapes the webpage using Selenium (headless browser) to find the live streaming M3U8 URL.
    This is typically used when content is loaded via JavaScript.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(webpage_url)

        # Give the page some time to fully render and for JavaScript to execute
        # Adjust this wait time as needed.
        time.sleep(5) 

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Primary Strategy: Look for the 'data-play' attribute on the "咪咕线路" button
        migu_button = soup.find('button', {'class': 'route-btn', 'data-name': '咪咕线路'})

        if migu_button:
            m3u8_link = migu_button.get('data-play')
            if m3u8_link and 'auth=' in m3u8_link:
                print(f"Selenium: Found complete M3U8 link in data-play attribute: {m3u8_link}")
                return m3u8_link
            elif m3u8_link:
                print(f"Selenium: Found M3U8 link in data-play, but 'auth=' is missing. Link: {m3u8_link}")
        else:
            print("Selenium: Migu button with data-name='咪咕线路' not found.")

        # Secondary Strategy: Search within script tags for the 'playUrl' variable
        print("Selenium: Attempting to find M3U8 link in script tags...")
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                match = re.search(r"var playUrl = '/static/ds3/dplayer.php\?url=(https:\/\/live\.huarenlivewebsite\.top\/stream\/CCTV5_MG\.m3u8\?auth=[^']+)'", script.string)
                if match:
                    extracted_url = match.group(1)
                    if 'auth=' in extracted_url:
                        print(f"Selenium: Found complete M3U8 link in script tag: {extracted_url}")
                        return extracted_url
                    else:
                        print(f"Selenium: Found M3U8 link in script tag, but 'auth=' is missing. Link: {extracted_url}")

        print("Selenium: No complete M3U8 link with 'auth=' found using Selenium.")
        return None

    except Exception as e:
        print(f"Selenium: Error with Selenium: {e}")
        return None
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    WEBPAGE_TO_SCRAPE = "https://huaren.live/viv/detail/id/536/nid/1.html"

    updated_stream_url = None

    # Try with requests/BeautifulSoup first (it's faster and uses less resources)
    print("Attempting to scrape using requests/BeautifulSoup...")
    updated_stream_url = get_live_stream_url_requests(WEBPAGE_TO_SCRAPE)

    # If requests/BeautifulSoup failed to find the complete URL, try with Selenium
    if not updated_stream_url:
        print("\nRequests/BeautifulSoup failed or found incomplete URL. Trying with Selenium (requires browser setup)...")
        updated_stream_url = get_live_stream_url_selenium(WEBPAGE_TO_SCRAPE)

    if updated_stream_url:
        print(f"\nSuccessfully scraped the live stream URL: {updated_stream_url}")

        output_filename = "cctv5_huaren.m3u8"
        m3u8_content = f"#EXTM3U\n{updated_stream_url}\n"

        try:
            with open(output_filename, "w") as f:
                f.write(m3u8_content)
            print(f"Live stream URL written to {output_filename}")
        except IOError as e:
            print(f"Error writing to M3U8 file: {e}")
    else:
        print("\nFailed to find a complete live stream URL with 'auth=' using any method. M3U8 file not created.")
