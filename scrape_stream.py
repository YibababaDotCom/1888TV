import requests
from bs4 import BeautifulSoup
import re
import os

def get_live_stream_url(webpage_url):
    """
    Scrapes the webpage to find the live streaming M3U8 URL with the dynamic auth key.
    """
    try:
        response = requests.get(webpage_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Strategy 1: Find the button with data-play attribute for "咪咕线路"
        # This assumes the '咪咕线路' button is still the primary source for the link
        migu_button = soup.find('button', {'class': 'route-btn', 'data-name': '咪咕线路'})

        if migu_button:
            m3u8_link = migu_button.get('data-play')
            if m3u8_link:
                print(f"Found M3U8 link in data-play attribute: {m3u8_link}")
                return m3u8_link

        # Strategy 2: Fallback to searching within script tags
        print("Migu button data-play not found or empty. Falling back to script tags.")
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                # The regex needs to be more general since the base URL might change to huaren.live
                # or adapt to the new structure if the playUrl variable changes slightly.
                # Given the previous context, it's safer to keep the specific domain,
                # but be aware if the domain itself changes.
                match = re.search(r"var playUrl = '/static/ds3/dplayer.php\?url=(https:\/\/live\.huarenlivewebsite\.top\/stream\/CCTV5_MG\.m3u8\?auth=[^']+)'", script.string)
                if match:
                    extracted_url = match.group(1)
                    print(f"Found M3U8 link in script tag: {extracted_url}")
                    return extracted_url

        return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    # --- IMPORTANT CHANGE HERE ---
    # Update the URL to the new specific detail page URL
    WEBPAGE_TO_SCRAPE = "https://huaren.live/viv/detail/id/536/nid/1.html"

    updated_stream_url = get_live_stream_url(WEBPAGE_TO_SCRAPE)

    if updated_stream_url:
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
        print("Failed to find the live stream URL. M3U8 file not created.")
