# multiple windows
# new_tab, close_tab, switch_tab, go_to, click_on, type_in, call_puppeteer
def get_functions():
    return {
        "new_tab": {
            "name": "new_tab",
            "description": "Open a new tab.",
            "parameters": [],
            "return": "None",
            "function": create_new_tab,
        },
    }

def create_new_tab():
    print("creating new tab")

if __name__ == "__main__":
    get_functions()
