import asyncio
import signal
from pyppeteer import launch
from collections import defaultdict
from typing import Dict


class VirtualBrowser:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.browser = self.loop.run_until_complete(launch())
        self.pages: Dict[str, Dict] = defaultdict(dict)
        self.current_page_id = None
        signal.signal(signal.SIGINT, self.handle_interrupt)

    async def close_browser(self):
        await self.browser.close()

    def handle_interrupt(self):
        asyncio.ensure_future(self.close_browser())
        self.loop.stop()


browser = VirtualBrowser()

if __name__ == "__main__":
    # Check if the browser has been initialized
    assert browser.browser is not None, "Browser initialization failed."

    # Check if the asyncio event loop has been set
    assert browser.loop is not None, "Event loop initialization failed."

    # Check if the pages dictionary has been initialized correctly
    assert isinstance(browser.pages, defaultdict), "Pages initialization failed."

    # Check if the current_page_id is None as expected initially
    assert browser.current_page_id is None, "current_page_id initialization failed."
    
    print("All tests passed.")
