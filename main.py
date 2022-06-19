import discord
from bs4 import BeautifulSoup
from discord.ext import tasks
import requests
import urllib.request, json
import os
import datetime
import asyncio


class Bot(discord.Client):
    async def on_ready(self):
        print("Successfully deployed:", self.user)
        dailyLoop.start()

    async def on_message(self, message):
        if message.author == self.user:
            return

        prefix = "!"
        if message.content == prefix + "help":
            embedVar = discord.Embed(title="Commands", color=0xC200D8)
            embedVar.add_field(
                name="Random Cat Image",
                value="!cat",
                inline=False,
            )
            embedVar.add_field(
                name="Retrieve Top Subreddit Posts",
                value="!r subreddit_name",
                inline=False,
            )
            embedVar.add_field(
                name="Delete Messages",
                value="!delete amount",
                inline=False,
            )
            await message.channel.send(embed=embedVar)

        # get image of cat
        if message.content == prefix + "cat":
            with urllib.request.urlopen("https://cataas.com/cat?json=true") as url:
                data = json.loads(url.read().decode())
                catUrl = data["url"]
                catImage = "https://cataas.com/" + catUrl
                embedVar = discord.Embed(title="cat", color=0xC200D8)
                embedVar.set_image(url=catImage)
                await message.channel.send(embed=embedVar)
                print(catUrl)

        # very hit and miss, sometimes it works at retrieving images
        reddit_prefix = "!r "
        str = message.content.lstrip("!r ")
        if message.content == reddit_prefix + str:
            url = "https://www.reddit.com/r/" + str + "/top/"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            image_tags = soup.find_all("img", attrs={"alt": "Post image"})
            print("requested: r/" + str)

            if not image_tags:
                await message.channel.send(
                    "`Could not retrieve image(s) from r/"
                    + str
                    + "`"
                    + "\n`Try Again!`"
                )
                print("Failed to retreive image(s)")
            else:
                for counter, image_tag in enumerate(image_tags):
                    image_url = image_tag["src"]
                    response = requests.get(image_url)
                    embedVar = discord.Embed(title="r/" + str, color=0xC200D8)
                    embedVar.set_image(url=image_url)
                    await message.channel.send(embed=embedVar)
                    print("retrieved " + image_url)

        # delete messages
        deleteAmount = message.content.lstrip("!delete ")
        try:
            if message.content == prefix + "delete " + deleteAmount:
                if not message.author.top_role.permissions.manage_messages:
                    await message.channel.send("`You don't have permission`")
                else:
                    if deleteAmount.isdigit() == True:
                        amount = int(deleteAmount)
                        if amount > 100:
                            await message.channel.send(
                                "`Failed to delete: Maximum 100`"
                            )
                            print("failed to delete", amount, "messages")
                        elif amount < 1:
                            await message.channel.send(
                                "`Failed to delete: number must be greater than 0`"
                            )
                        else:
                            await message.channel.purge(limit=amount)
                            print("deleted", amount, "messages")
                            embedVar = discord.Embed(
                                title="deleted",
                                description=deleteAmount + " messages",
                                color=0xC200D8,
                            )
                            await message.channel.send(embed=embedVar)
                    else:
                        print("not an integer")
                        await message.channel.send("`!delete [Must be an integer]`")
        except discord.DiscordException as err:
            print(discord.DiscordException())
            await message.channel.send("`%s`" % err)


# sends weekly cat pic
@tasks.loop()
async def dailyLoop():
    channel = client.get_channel(398928792334368770)
    current_time = datetime.datetime.now().strftime("%H:%M")
    day_week = datetime.datetime.now().weekday()
    # if monday
    if day_week == 0:
        print(current_time)
        # if 8am
        if current_time == "08:00":
            with urllib.request.urlopen("https://cataas.com/cat?json=true") as url:
                data = json.loads(url.read().decode())
                catUrl = data["url"]
                catImage = "https://cataas.com/" + catUrl
                embedVar = discord.Embed(title="Weekly Cat Pic", color=0xC200D8)
                embedVar.set_image(url=catImage)
                await channel.send(embed=embedVar)
                print("Weekly Pic Sent")
                # wait 60 seconds after first run through
                await asyncio.sleep(60)
                return


TOKEN = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
client = Bot(intents=intents)
client.run(TOKEN)
