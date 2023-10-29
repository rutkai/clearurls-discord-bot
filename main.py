import os
import re
import discord
import requests
from dotenv import load_dotenv
from unalix import clear_url


class MyClient(discord.Client):
    async def on_message(self, message):
        if message.author == client.user:
            permissions = message.channel.guild.me.guild_permissions
            # Suppress embeds for bot messages to avoid visual clutter
            if permissions.manage_messages:
                await message.edit(suppress=True)
                # Add :wastebasket: emoji for easy deletion if necessary
                if permissions.add_reactions and permissions.read_message_history:
                    await message.add_reaction('🗑')

        # Extract links and clean
        urls = re.findall('(?P<url>https?://[^\s]+)', message.content)
        cleaned = []
        for url in urls:

            if clear_url(url) != url:
                cleaned.append(clear_url(url))

        # Send message and add reactions
        if cleaned:
            text = 'It appears that you have sent one or more links with tracking parameters. Below are the same links with those fields removed:\n' + '\n'.join(cleaned)
            await message.reply(text, mention_author=False)

    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        # Delete message if original author clicked on trash reaction
        permissions = message.channel.guild.me.guild_permissions
        if not permissions.manage_messages or message.reference is None:
            return
        channel = client.get_channel(message.reference.channel_id)
        original = await channel.fetch_message(message.reference.message_id)
        if message.author == client.user and user == original.author and reaction.emoji == '🗑':
            await reaction.message.delete()

    def follow_redirect(self, url):
        for _ in range(5):
            try:
                new_url = requests.head(url, allow_redirects=True).url
                if new_url == url:
                    return url
                url = new_url
            except requests.exceptions.ConnectionError:
                return url

        return url


load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(os.environ['TOKEN'])
