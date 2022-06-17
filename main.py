import discord
from bs4 import BeautifulSoup
import requests
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
            embedVar = discord.Embed(title="commands", color=0xC200D8)
            embedVar.add_field(
                name="Retrieve top subreddit posts",
                value="!r subreddit_name",
                inline=False,
            )
            await message.channel.send(embed=embedVar)

        reddit_prefix = "!r "
        str = message.content.lstrip("!r ")
        if message.content == reddit_prefix + str:
            url = "https://www.reddit.com/r/" + str + "/top/"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            image_tags = soup.find_all("img", attrs={"alt": "Post image"})

            count = 0
            while not image_tags:
                top = "https://www.reddit.com/r/" + str + "/top/"
                url = top
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")
                image_tags = soup.find_all("img", attrs={"alt": "Post image"})
                time.sleep(2)
                count += 1

                if count == 5:
                    await message.channel.send(
                        "`Could not retrieve image from r/"
                        + str
                        + "`"
                        + "\n`Try Again!`"
                    )
                    break
                else:
                    for counter, image_tag in enumerate(image_tags):
                        image_url = image_tag["src"]
                        response = requests.get(image_url)
                        embedVar = discord.Embed()
                        embedVar.set_image(url=image_url)
                        await message.channel.send(embed=embedVar)


client = Bot(intents=intents)
token = "your bot token"
client.run(token)
