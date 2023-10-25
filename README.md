# SobbleDex

This is a Discord bot built from [Koduck](https://github.com/Chupalika/Koduck)!

Note: `shuffle_calc_data.json` and `sobble_calc_functions.py` are created by Sky.

## Setup

I've left out some data that were either variable or sensitive. They're not needed for the bot to function, but if you want them, here are up to date links to the data:

- [shuffle_tables/aliases.txt](https://www.dropbox.com/s/cz6j397ahs1edzg/aliases.txt?dl=0)
- [shuffle_tables/help_messages.txt](https://www.dropbox.com/scl/fi/i9jkrana4m5xjdicvhpo9/help_messages.txt?rlkey=t7y8n2l0z3tg60iezhrktpff3&dl=0)
- `shuffle_tables/reminders.txt` - sensitive
- [shuffle_tables/skill_notes.txt](https://www.dropbox.com/scl/fi/ly5kyg1uqqxsbxc6pwvy1/skill_notes.txt?rlkey=qzfhth4glmbastianrbyhdy04&dl=0)
- [shuffle_tables/stage_notes.txt](https://www.dropbox.com/scl/fi/v45gtajpl46u0fu7wx6l3/stage_notes.txt?rlkey=zcd8c0d9wsdtr603nc9wij1cd&dl=0)
- [tables/commands.txt](https://www.dropbox.com/scl/fi/n48skyz4qlfd13odlqh4u/commands.txt?rlkey=d0pf3ebt79w1fweohrme1aow9&dl=0) - edited out the custom responses
- [tables/custom_responses.txt](https://www.dropbox.com/scl/fi/awvzkilcq4iqb64e0q1zr/custom_responses.txt?rlkey=cpscv91bw9m4vjm2v78wxkhza&dl=0)
- `tables/user_levels.txt` - sensitive

`tables/settings.txt` also contains some sensitive values which I've edited out:

- `main_server_id` - server id of SobbleDex's discord server (not the /r/PokemonShuffle server). This is only really used to load some emojis, so it's not necessary for the bot to run.

Add a file called `.env` with `token=` followed by your bot token.

Run `python main.py`
