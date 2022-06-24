# reactions and role management
import discord
from discord.ext import commands
import json

class ReactionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # standard unicode character - PARROT from https://www.fileformat.info/info/unicode/char/1f99c/index.htm
    # "\uD83E\uDD9C": [989590380964114442]
    # custom discord emoji <:name:id>
    # "<:ai:989617213902303252>": [989590509355925516]
    # config.json example:
    # [
    #     {
    #         "msg_id": 989591224539316325,
    #         "guild_id": 874574602783842324,
    #         "emoji_roles_map": {
    #             "\uD83E\uDD9C": [989590380964114442],
    #             "<:ai:989617213902303252>": [989590509355925516]
    #         }
    #     }
    # ]

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        with open("Data/reaction_role_config.json", "r") as config_file:
            config = json.load(config_file)
            for setting in config:
                if setting['msg_id'] == payload.message_id:
                    guild = self.bot.get_guild(setting['guild_id'])
                    for emote,roles in setting['emoji_roles_map'].items():
                        for role_id in roles:
                            if emote == str(payload.emoji):
                                await payload.member.add_roles(guild.get_role(role_id))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        with open("Data/reaction_role_config.json", "r") as config_file:
            config = json.load(config_file)
            for setting in config:
                if setting['msg_id'] == payload.message_id:
                    guild = self.bot.get_guild(setting['guild_id'])
                    for emote, roles in setting['emoji_roles_map'].items():
                        for role_id in roles:
                            if emote == str(payload.emoji):
                                await guild.get_member(payload.user_id).remove_roles(guild.get_role(role_id))




async def setup(bot):  # an extension must have a setup function
    await bot.add_cog(ReactionCog(bot))  # adding a cog
