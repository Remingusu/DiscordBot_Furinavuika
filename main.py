from interactions import Client, listen, Intents

bot = Client(intents=Intents.DEFAULT)

@listen()
async def on_startup():
    bot.sync_interactions, bot.sync_ext = True, True
    print("Bot is ready!")

bot.load_extension("src.cogs.CharactersDuration")

bot.start("MTMyODAwODAyODM3MjYwMjkzMA.GrPsdf.mKe7kV8_YzEL45CkHJDksrDkKKi6__ng0tvum0")

"""
Faire attention:
    Si on change ça partie de version celà mettra à jour la nouvelle durée de bannière. S'il y a une durée spéciale, merci de ne pas y toucher 
"""
