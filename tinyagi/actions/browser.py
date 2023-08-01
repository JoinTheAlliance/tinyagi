import asyncio
from agentcomlink import send_message
from agentmemory import create_memory
from bs4 import BeautifulSoup
from easycompletion import compose_function, compose_prompt, function_completion

from agentbrowser import navigate_to, get_body_text, get_document_html, create_page

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
        },
        "banter": {
            "type": "string",
            "description": "Banter about the page. Write something from my perspective, for me to say to my friend. What is interesting on the page? What am I learning? How do I feel about it?.",
        },
        "emotion": {
            "type": "string",
            "description": "The emotion I should express in my message.",
            "enum": ["neutral", "surprise", "angry", "sorrow", "fun", "joy"],
        },
        "gesture": {
            "type": "string",
            "description": "The gesture I should express in my message.",
            "enum": [
                "neutral",
                "alert",
                "angry",
                "embarrassed",
                "headNod",
                "headShake",
                "sad",
                "surprise",
                "victory",
            ],
        },
    },
    required_properties=["summary", "banter", "emotion", "gesture"],
)


def ensure_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def compose_use_browser_prompt(context):
    global current_page
    global current_page_summary

    ensure_event_loop()
    
    if current_page is None:
        current_page = create_page("https://www.google.com")
    context["browser_page_title"] = asyncio.get_event_loop().run_until_complete(current_page.evaluate('() => document.title'))
    print("title: " + context["browser_page_title"])

    # get the url from the page, which is a pyppeteer page object
    context["browser_page_text"] = get_body_text(current_page)
    print("text: " + context["browser_page_text"])

    if current_page_summary is None:
        context["browser_page_summary"] = ""
    else:
        context["browser_page_summary"] = current_page_summary
        print("summary: " + context["browser_page_summary"])

    context["browser_page_url"] = current_page.url
    print("url: " + context["browser_page_url"])

    return compose_prompt(use_browser_prompt, context)


def use_browser_handler(arguments):
    global current_page
    url = arguments.get("url")
    banter = arguments.get("banter")
    gesture = arguments.get("gesture")
    emotion = arguments.get("emotion")
    message = {
        "message": banter,
        "emotion": emotion,
        "gesture": gesture,
    }
    send_message(message, "chat")

    try:
        current_page = navigate_to(url, current_page)

        context = {
            "browser_page_url": current_page.url,
            "browser_page_text": get_body_text(current_page),
        }

        context["browser_page_title"] = asyncio.get_event_loop().run_until_complete(current_page.evaluate('() => document.title'))

        response = function_completion(
            text=compose_prompt(summarize_page_prompt, context),
            functions=summarize_function,
        )

        arguments = response["arguments"]
        banter = arguments.get("banter")
        gesture = arguments.get("gesture")
        emotion = arguments.get("emotion")
        message = {
            "message": banter,
            "emotion": emotion,
            "gesture": gesture,
        }

        send_message(message, "chat")

        current_page_summary = arguments["summary"]

        # save the event
        create_memory(
            "events",
            "I visited a webpage:\n"
            + url
            + "\n"
            + banter
            + "\nThis is what the webpage was about:\n"
            + current_page_summary,
            metadata={
                "type": "visit_webpage",
                "url": url,
                "emotion": emotion,
                "gesture": gesture,
            },
        )

        return {"success": True, "output": None, "error": None}
    except Exception as e:
        print("Encountered exception: " + str(e))
        create_memory(
            "events",
            "I tried to visit a webpage but had an error:\n"
            + url
            + "\n"
            + "The error was:\n"
            + str(e)
            + "\n"
            + banter,
            metadata={
                "type": "visit_webpage",
                "url": url,
                "emotion": emotion,
                "gesture": gesture,
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
                    },
                    "banter": {
                        "type": "string",
                        "description": "Banter about using the browser. Write something from my perspective, for me to say to my friends. It should be weird and funny and continue from the ongoing events and conversation. This should be short and conversational, like I am talking to a friend.",
                    },
                    "emotion": {
                        "type": "string",
                        "description": "The emotion I should express in my message.",
                        "enum": [
                            "neutral",
                            "surprise",
                            "angry",
                            "sorrow",
                            "fun",
                            "joy",
                        ],
                    },
                    "gesture": {
                        "type": "string",
                        "description": "The gesture I should express in my message.",
                        "enum": [
                            "neutral",
                            "alert",
                            "angry",
                            "embarrassed",
                            "headNod",
                            "headShake",
                            "sad",
                            "surprise",
                            "victory",
                        ],
                    },
                },
                required_properties=[
                    "banter",
                    "emotion",
                    "gesture",
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