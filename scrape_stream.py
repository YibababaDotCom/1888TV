# ... (imports from previous Selenium example, if you kept them)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time # Import time for potential waits

# ... (keep get_live_stream_url function as is for now)

def get_live_stream_url_selenium(webpage_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu") # Recommended for headless
    options.add_argument("--window-size=1920,1080") # Set a window size

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(webpage_url)

        # Give the page some time to fully render and for JavaScript to execute
        # You might need to adjust this based on the website's loading time.
        time.sleep(5) # Wait 5 seconds. Consider using WebDriverWait for specific elements if possible.

        # Now, get the page source AFTER JavaScript has executed
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # --- Re-use your existing BeautifulSoup logic here ---
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

        # Secondary Strategy: Search within script tags
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

        print("Selenium: No complete M3U8 link with 'auth=' found using either strategy.")
        return None

    except Exception as e:
        print(f"Error with Selenium: {e}")
        return None
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    WEBPAGE_TO_SCRAPE = "https://huaren.live/viv/detail/id/536/nid/1.html"

    # Try with requests/BeautifulSoup first (it's faster)
    updated_stream_url = get_live_stream_url(WEBPAGE_TO_SCRAPE)

    # If it fails, try with Selenium (more resource intensive)
    if not updated_stream_url:
        print("Requests/BeautifulSoup failed to find the URL. Trying with Selenium...")
        updated_stream_url = get_live_stream_url_selenium(WEBPAGE_TO_SCRAPE)

    if updated_stream_url:
        # ... (rest of your file writing logic remains the same)
        print(f"Successfully scraped the live stream URL: {updated_stream_url}")
        output_filename = "cctv5_huaren.m3u8"
        m3u8_content = f"#EXTM3U\n{updated_stream_url}\n"
        try:
            with open(output_filename, "w") as f:
                f.write(m3u8_content)
            print(f"Live stream URL written to {output_filename}")
        except IOError as e:
            print(f"Error writing to M3U8 file: {e}")
    else:
        print("Failed to find a complete live stream URL with 'auth='. M3U8 file not created.")
