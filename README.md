# tinyagi
A really simple approach to a self-learning, open-ended system.

To install
```sh
pip install -r requirements.txt # install the dependencies
cp .env.sample .env # copy the sample environment file
```
To change some configuration stuff, edit the `.env` file, especially the `OPENAI_API_KEY` and `AGENT_NAME` variable.

To run
```
python start.py
```

To chat wit your agent, open another terminal and run this:
```
python user_terminal.py
```
No guarauntee the agent will respond...

To add a skill, copy and paste a skill that is similar in the skills directory. Rename it to something unique and modify. The skill will be automatically loaded.

To see what's going on, check out `logs/feed.log`

