from ..SQLite.DatabaseHandler import DatabaseHandler

from datetime import datetime

from interactions import Extension
from interactions import StringSelectMenu
from interactions.api.events import Component
from interactions import SlashContext, slash_command, slash_option, OptionType, SlashCommandChoice


durationMap = {
    "newUpdate": {
        "Genshin Impact": 21,
        "Honkai Star Rail": 21,
        "Zenless Zone Zero": 22,
        "Wuthering Waves": 23
    },
    "midUpdate": {
        "Genshin Impact": 22,
        "Honkai Star Rail": 22,
        "Zenless Zone Zero": 21,
        "Wuthering Waves": 21,
    }
}

sccListMonth = [
        SlashCommandChoice(name="January", value=1),
        SlashCommandChoice(name="February", value=2),
        SlashCommandChoice(name="March", value=3),
        SlashCommandChoice(name="April", value=4),
        SlashCommandChoice(name="May", value=5),
        SlashCommandChoice(name="June", value=6),
        SlashCommandChoice(name="July", value=7),
        SlashCommandChoice(name="August", value=8),
        SlashCommandChoice(name="September", value=9),
        SlashCommandChoice(name="October", value=10),
        SlashCommandChoice(name="November", value=11),
        SlashCommandChoice(name="December", value=12)
]

class CharactersDuration(Extension):
    def __init__(self, bot):
        self.dbObj = DatabaseHandler()

    @slash_command(name="add", description="Adds a character, its release date, and the game !")
    @slash_option(name="character", description="Name of the character.", opt_type=OptionType.STRING, required=True)
    @slash_option(name="month", description="Month of release.", opt_type=OptionType.INTEGER,
                  required=True, choices=sccListMonth)
    @slash_option(name="day", description="Day of release.", opt_type=OptionType.INTEGER, required=True)
    @slash_option(name="game", description="Name of the game.", opt_type=OptionType.STRING, required=True, choices=
                    [
                        SlashCommandChoice(name="Genshin", value="Genshin Impact"),
                        SlashCommandChoice(name="HSR", value="Honkai Star Rail"),
                        SlashCommandChoice(name="ZZZ", value="Zenless Zone Zero"),
                        SlashCommandChoice(name="Wuwa", value="Wuthering Waves")
                    ])
    @slash_option(name="special_duration", description="If there is a banner duration that change, please add it here.",
                  opt_type=OptionType.INTEGER, required=False)
    @slash_option(name="year", description="Year of release.", opt_type=OptionType.INTEGER, required=False, choices=
                    [
        SlashCommandChoice(name="2025", value=2025),
        SlashCommandChoice(name="2024", value=2024),
    ])
    @slash_option(name="mid_update", description="The character is in the second part of the update.",
                  opt_type=OptionType.STRING, required=False, choices=
                    [
                        SlashCommandChoice(name="Yes", value="midUpdate"),
                        SlashCommandChoice(name="No", value="newUpdate")
                    ])
    async def add(self, ctx, character, month, day, game, special_duration = 0,
                  year = 2025, mid_update="newUpdate"):

        duration = durationMap[mid_update][game] if special_duration == 0 else special_duration

        self.dbObj.add_character(character, year, month, day, game, duration, ctx.author.id)

        await ctx.send(f"{character}'s release date is {year}-{month}-{day}. "
                       f"It's from {game}. It will be available for {duration} days.")

    # --------------------------------------------------------------------------------------------------------------------

    @slash_command(name="update", description="Changes an information about a character.")
    @slash_option(name="month", description="Month of release.", opt_type=OptionType.INTEGER,
                  required=False, choices=sccListMonth)
    @slash_option(name="day", description="Day of release.", opt_type=OptionType.INTEGER, required=False)
    @slash_option(name="game", description="Name of the game.", opt_type=OptionType.STRING, required=False, choices=
    [
        SlashCommandChoice(name="Genshin", value="Genshin Impact"),
        SlashCommandChoice(name="HSR", value="Honkai Star Rail"),
        SlashCommandChoice(name="ZZZ", value="Zenless Zone Zero"),
        SlashCommandChoice(name="Wuwa", value="Wuthering Waves")
    ])
    @slash_option(name="special_duration", description="If there is a banner duration that change, please add it here.",
                  opt_type=OptionType.INTEGER, required=False)
    @slash_option(name="year", description="Year of release.", opt_type=OptionType.INTEGER, required=False, choices=
    [
        SlashCommandChoice(name="2025", value=2025),
        SlashCommandChoice(name="2024", value=2024),
    ])
    @slash_option(name="mid_update", description="The character is in the second part of the update.",
                  opt_type=OptionType.STRING, required=False, choices=
                  [
                      SlashCommandChoice(name="Yes", value="midUpdate"),
                      SlashCommandChoice(name="No", value="newUpdate")
                  ])

    async def update(self, ctx: SlashContext, month=None, day=None, game=None,
                     special_duration=None, year=None, mid_update=None):
        options = self.dbObj.get_names()

        select_menu = StringSelectMenu(
            options,
            custom_id="characters_name",
            placeholder="Character name",
            min_values=1,
            max_values=1
        )

        await ctx.send("Choose the character to update.", components=select_menu)

        try:
            used_component: Component = await self.bot.wait_for_component(components=select_menu, timeout=10)

        except TimeoutError:
            pass

        else:
            row = self.dbObj.get_informations(used_component.ctx.values[0])

            if mid_update and game is None:
                duration = durationMap[mid_update][row[2]]
            elif mid_update and game:
                duration = durationMap[mid_update][game]
            else:
                duration = row[3]

            duration = special_duration if special_duration else duration

            date_obj = datetime.strptime(row[1], "%Y/%m/%d")

            month = month if month else date_obj.month
            day = day if day else date_obj.day
            game = game if game else row[2]
            year = year if year else date_obj.year


            self.dbObj.update_character(used_component.ctx.values[0], month, day, game, year, duration)

            await used_component.ctx.send(f"Character {used_component.ctx.values[0]} updated !")

# --------------------------------------------------------------------------------------------------------------------

    @slash_command(name="delete", description="Delete a character.")
    async def delete(self, ctx: SlashContext):
        options = self.dbObj.get_names()

        select_menu = StringSelectMenu(
            options,
            custom_id="characters_name",
            placeholder="Character name",
            min_values=1,
            max_values=1
        )

        await ctx.send("Choose the character to delete.", components=select_menu)

        try:
            used_component: Component = await self.bot.wait_for_component(components=select_menu, timeout=10)

        except TimeoutError:
            pass

        else:
            self.dbObj.remove_character(used_component.ctx.values[0])
            await used_component.ctx.send(f"Character {used_component.ctx.values[0]} deleted !")



#################################################
