# A virtual chrome browser for the agent to use.

import asyncio  # for asynchronous I/O
from pyppeteer import launch  # for launching a headless browser
from collections import defaultdict  # for storing the browser pages
from typing import Dict  # for type annotation


class VirtualBrowser:
    def __init__(self):
        self.loop = (
            asyncio.get_event_loop()
        )  # get the current event loop (main thread), if no event loop is active it will create a new one
        self.browser = self.loop.run_until_complete(
            launch()
        )  # launch a new browser in the event loop and wait for it to complete
        self.pages: Dict[str, Dict] = defaultdict(
            dict
        )  # a dictionary to store the pages (browser tabs)
        self.current_page_id = None  # keeps track of the currently active page (if any)


# create an instance of the VirtualBrowser class
browser = VirtualBrowser()
if __name__ == "__main__":
    # Create an instance of the VirtualBrowser class
    browser = VirtualBrowser()

    # Check if the browser has been initialized
    assert browser.browser is not None, "Browser initialization failed."

    # Check if the asyncio event loop has been set
    assert browser.loop is not None, "Event loop initialization failed."

    # Check if the pages dictionary has been initialized correctly
    assert isinstance(browser.pages, defaultdict), "Pages initialization failed."

    # Check if the current_page_id is None as expected initially
    assert browser.current_page_id is None, "current_page_id initialization failed."

    print("All tests passed.")
