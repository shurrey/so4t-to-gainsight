# Migration tool - Stack Overflow for Teams to Gainsight Customer Communities

This tool is built to migrate users, posts, comments, and correct answers from a Stack Overflow for Teams community to a single forum in Gainsight Customer Communities.

To run:
1. Copy .env.template to .env and fill in your credential details. Be sure to replace the last token `team` in the SO4T_URI with your team name.
2. Run `pip install -r requirements.txt` to install requirements. We recommend first setting up a virtual environment with either `virtualenv .venv` or `python -m venv .venv` and then activating that environment with `source .venv/bin/activate`.
3. Run `python migrate.py`.