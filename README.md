# tinyagi
A really simple approach to a self-learning, open-ended system.

To install
```sh
pip install -r requirements.txt # install the dependencies
cp .env.example .env # copy the example environment file
```
To change some configuration stuff, edit the `.env` file, especially the `OPENAI_API_KEY` variable.

To run
```
python start.py
```

To chat wit your agent, wait until they've figured out how to establish contact

## Actions
Actions are things that the agent can do. They are loaded from the actions directory and can be used, written and edited at runtime. Make sure you back up any code you use if you don't want it changed.

To add an action, copy and paste a action that is similar in the actions directory. Rename it to something unique and modify. The action will be automatically loaded.

# Connectors
Connectors get the agent into the outside world. They are loaded from the connectors directory and can be used, written and edited at runtime. Make sure you back up any code you use if you don't want it changed.


To see what's going on, check out `logs/feed.log`

