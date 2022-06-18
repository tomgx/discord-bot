import discord
from bs4 import BeautifulSoup
import requests
import urllib.request, json
import time

intents = discord.Intents.default()


class Bot(discord.Client):
    async def on_ready(self):
        print("Successfully deployed:", self.user)

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
                value="!delete AMOUNT",
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

        deleteAmount = message.content.lstrip("!delete ")
        try:
            if message.content == prefix + "delete " + deleteAmount:
                amount = int(deleteAmount)
                if amount > 100:
                    await message.channel.send("`Failed to delete: Maximum 100`")
                    print("failed to delete", amount, "messages")
                elif amount < 1:
                    await message.channel.send(
                        "`Failed to delete: number must be greater than 0`"
                    )
                else:
                    await message.channel.purge(limit=amount)
                    print("deleted", amount, "messages")
                    # time.sleep(1)
                    embedVar = discord.Embed(
                        title="deleted",
                        description=deleteAmount + " messages",
                        color=0xC200D8,
                    )
                    await message.channel.send(embed=embedVar)
        except:
            print("error")
            await message.channel.send("`!delete [Must be an integer]`")


client = Bot(intents=intents)
token = "your bot token"
client.run(token)
