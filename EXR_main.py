# this bot is designed to keep xare in check because he is A FAT ANNOYING NOOB
# note: plz disable pings in your server because this bot wont prevent them, this is only to punish xare if he mass pings
# also this is like my third discord bot so the code is kinda buns
import os
import discord
import re
from flask import Flask
from threading import Thread
from datetime import timedelta
from discord import Embed

PORT = int(os.environ.get("PORT", 5000))  # port
discordTOKEN = os.environ.get("DISCORD_TOKEN")
timeoutLength = 300 # about an hour
devId = int(os.environ.get("devId")) # accidentally put the wrong user id oops
kidToKeepInCheck = int(os.environ.get("kidToKeepInCheck"))
timesThisKidHasPinged = 0 # explanatory
pingMin = int(os.environ.get("pingMin")) # amount of pings that can happen before timeout
chances = pingMin + 1 # yeah
#amountOfPingsBeforeKick = 10 # how many pings need to have happpened before we kick xare (unused because yeah)

app = Flask('')

@app.route('/')
def home():
    return "if ur seeing this then EXRbot is online!"

def run_web():
    app.run(host="0.0.0.0", port=PORT)

Thread(target=run_web).start()

intents = discord.Intents.default()
intents.message_content = True # required to read messages
intents.members = True # required to check pings in a message

client = discord.Client(intents=intents)

async def send_embed(channel, author, title, description, fields=None, color=0xFF5733):

    embed = Embed(title=title, description=f"{description}", color=color)

    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    await channel.send(embed=embed)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global timesThisKidHasPinged
    global timeoutLength
    global pingMin
    global chances

    guild = message.guild

    if message.author == client.user:
        return
    
    if (len(message.mentions) > 0 or message.mention_everyone) and message.author.id == kidToKeepInCheck:
        #print(f"{message.author.id} and {kidToKeepInCheck}")

        timesThisKidHasPinged += 1

        user_pings = re.findall(r"<@!?\d+>", message.content)
        role_pings = re.findall(r"<@&\d+>", message.content)
        channel_pings = re.findall(r"<#\d+>", message.content)
        everyone_pings = re.findall(r"@everyone|@here", message.content)

        totalPings = (
            len(user_pings) +
            len(role_pings) +
            len(channel_pings) +
            len(everyone_pings)
        )

        if message.mention_everyone: # lololololololo
            timesThisKidHasPinged = 100 
            totalPings = 100
        #print("pings:", totalPings)

        await message.delete()  

        if timesThisKidHasPinged <= pingMin and totalPings <= pingMin:
            chances -= 1
            #await message.channel.send(f"i detected a ping from you {message.author.mention}\nif you keep it up then you will be timed out for {timeoutLength} seconds\nyou have {chances} chances left\nnote: pinging more people than your remaining chances will result in a timeout!")

            fields = [
                ("warning", f"if you keep it up, you'll be timed out for **{timeoutLength} seconds**", False),
                ("chances left", f"you have **{chances}** chances remaining.\nnote: pinging more people than your remaining chances or using `@everyone` will result in an instant timeout!", False)
            ]
            
            await send_embed(
                channel=message.channel,
                author=message.author,
                title="NOTIFICATION",
                description=f"i detected a ping from you, {message.author.mention}!",
                fields=fields,
                color=0xFF5733
            )
        else:
            # reset da stuff we changed
            timesThisKidHasPinged = 0
            chances = pingMin + 1

            try:
                TimeoutReason = f"{message.author.mention} has pinged over the ping limit which is {pingMin}, the user has been sent to timeout for {timeoutLength} seconds."

                await message.author.timeout(
                    timedelta(seconds=timeoutLength),
                    reason=TimeoutReason
                )

                fields = [
                    ("duration", f"{timeoutLength} seconds", False),
                    ("reason", TimeoutReason, False)
                ]

                await send_embed(
                    channel=message.channel,
                    author=message.author,
                    title="TIMEOUT NOTIFICATION",
                    description=f"{message.author.mention} has been timed out!",
                    fields=fields,
                    color=0xFF3333
                )

                #await message.channel.send(f"{message.author.mention} has been timed out for {timeoutLength} seconds!\nReason: {TimeoutReason}")
            except discord.Forbidden:

                await send_embed(
                    channel=message.channel,
                    author=message.author,
                    title="PERMISSION ERROR",
                    description=f"I DONT HAVE PERMISSION TO TIMEOUT {message.author.mention}, plz make sure my role is high enough and that i have administrator privileges! <@{guild.owner_id}>",
                    color=0xFF3333
                )
            
                #await message.channel.send(f"I DONT HAVE PERMISSION TO TIMEOUT {message.author.mention}, plz make sure my role is high enough and that i have administrator privileges! <@{guild.owner_id}>")
            except Exception as e:
                fields = [
                    ("duration", f"{timeoutLength} seconds", False),
                    ("reason", TimeoutReason, False)
                ]

                await send_embed(
                    channel=message.channel,
                    author=message.author,
                    title="AN ERROR HAS OCCURRED",
                    description=f"{e}\n<@{devId}>",
                    fields=fields,
                    color=0xFF3333
                )
                #await message.channel.send(f"AN ERROR HAS OCCURRED: {e}\n<@{devId}>")
      
    #if message.content.startswith('$hello') and :
    #    print("USER ID FOUND IN kidsToKeepInCheck ", message.author.id)
    #    await message.channel.send('Hello!')


client.run(discordTOKEN)




