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

To chat wit your agent, open another terminal and run this:
```
python user_terminal.py
```
No guarauntee the agent will respond...

To add a function, copy and paste a function that is similar in the functions directory. Rename it to something unique and modify. The function will be automatically loaded.

To see what's going on, check out `logs/feed.log`

