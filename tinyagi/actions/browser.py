import asyncio
import base64
from agentcomlink import send_message
from agentmemory import create_event
from bs4 import BeautifulSoup
from easycompletion import compose_function, compose_prompt, function_completion

from agentbrowser import (
    navigate_to,
    get_body_text,
    get_document_html,
    create_page,
    screenshot_page,
    get_page_title,
)

current_page = None
current_page_summary = None
use_browser_prompt = """
{{relevant_knowledge}}
{{events}}
{{summary}}
{{browser_page_title}}
{{browser_page_summary}}
{{browser_page_url}}
{{browser_page_links}}
{{reasoning}}

Based on the action reasoning, where should I navigate to from here? Please include the full URL."""

summarize_page_prompt = """I'm visiting the webpage {{browser_page_url}} with the title {{browser_page_title}}
Here is the text on the page:
{{browser_page_text}}

Summarize the page and banter about the current webpage from my perspective. Anything interesting? Aything funny? Learn anything new?
"""


def ensure_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def extract_links(page):
    html = get_document_html(page)
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a_tag in soup.find_all("a"):
        # Check if the link has non-blank text and an href attribute
        if a_tag.text.strip() and a_tag.get("href"):
            links.append({"name": a_tag.text, "url": a_tag.get("href")})

    return links


summarize_function = compose_function(
    name="summarize",
    description="Summarize the current page.",
    properties={
        "summary": {
            "type": "string",
            "description": "The summary of the current page.",
        }
    },
    required_properties=["summary"],
)


def compose_use_browser_prompt(context):
    ensure_event_loop()
    global current_page
    global current_page_summary

    if current_page is None:
        current_page = create_page("https://www.google.com")
    context["browser_page_title"] = asyncio.get_event_loop().run_until_complete(
        current_page.evaluate("() => document.title")
    )

    # get the url from the page, which is a pyppeteer page object
    context["browser_page_text"] = get_body_text(current_page)

    if current_page_summary is None:
        context["browser_page_summary"] = ""
    else:
        context["browser_page_summary"] = current_page_summary

    context["browser_page_url"] = current_page.url

    return compose_prompt(use_browser_prompt, context)


def use_browser_handler(arguments):
    ensure_event_loop()
    global current_page
    url = arguments.get("url")

    try:
        if current_page is None:
            current_page = create_page(url)
        else:
            current_page = navigate_to(url, current_page, wait_until="networkidle")

        body_text = get_body_text(current_page)

        context = {
            "browser_page_url": current_page.url,
            "browser_page_text": body_text,
        }

        context["browser_page_title"] = get_page_title(current_page)

        image = screenshot_page(current_page)
        base64_img = base64.b64encode(image).decode("utf-8")
        send_message(base64_img, "browser_screenshot", "browser_screenshot")

        response = function_completion(
            text=compose_prompt(summarize_page_prompt, context),
            functions=summarize_function,
        )

        arguments = response["arguments"]

        current_page_summary = arguments["summary"]

        # save the event
        create_event(
            "I visited a webpage:\n"
            + url
            + "\nThis is what the webpage was about:\n"
            + current_page_summary,
            metadata={
                "type": "visit_webpage",
                "url": url,
            },
        )

        return {"success": True, "output": current_page_summary, "error": None}
    except Exception as e:
        create_event(
            "I tried to visit a webpage but had an error:\n"
            + url
            + "\n"
            + "The error was:\n"
            + str(e),
            metadata={
                "type": "visit_webpage",
                "url": url,
            },
        )
        return {"success": False, "output": None, "error": str(e)}


def get_actions():
    return [
        {
            "function": compose_function(
                name="browse_internet",
                description="Use my browser (Chrome) to browse the internet. I can use this to go to explore the internet, probably very helpful for research, learning and working on my tasks!",
                properties={
                    "url": {
                        "type": "string",
                        "description": "The url of the webpage to visit. Must be a complete URL, i.e. https:// etc.",
                    }
                },
                required_properties=[
                    "url",
                ],
            ),
            "prompt": use_browser_prompt,
            "builder": compose_use_browser_prompt,
            "handler": use_browser_handler,
            "suggestion_after_actions": ["browse_internet"],  # suggest self
            "never_after_actions": [],
        }
    ]
