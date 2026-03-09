# this bot sucks dont use it

import os
import asyncio
import discord
import re
import datetime
import json
from flask import Flask
from threading import Thread
from discord.ext import tasks
from datetime import timedelta
from discord import Embed

with open("/etc/secrets/keeds.json") as f:
    config = json.load(f)

PORT = int(os.environ.get("PORT", 5000))  # port
discordTOKEN = os.environ.get("DISCORD_TOKEN")
timeoutLength = 300
devId = int(os.environ.get("devId")) # accidentally put the wrong user id oops
kidsToKeepInCheck = set(config["kidsToKeepInCheck"])
timesThisKidHasPinged = 0 # explanatory
pingMin = int(os.environ.get("pingMin")) # amount of pings that can happen before timeout
chances = pingMin + 1 # yeah
aaaa = 0
mineemum = 2 # idk anymore

intents = discord.Intents.default()
intents.message_content = True # required to read messages
intents.members = True # required to check pings in a message

start_time = datetime.datetime.now()

client = discord.Client(intents=intents)

app = Flask('')

@app.route('/')
def home():
    return "if ur seeing this then EXRbot is online!"

def run_web():
    app.run(host="0.0.0.0", port=PORT)

Thread(target=run_web).start()


@client.event
async def on_ready():
    print(f'logged in as {client.user}')
    update_status.start()

@tasks.loop(seconds=10)
async def update_status():
    delta = datetime.datetime.now() - start_time
    uptime_str = format_uptime(delta)
    await client.change_presence(
        activity=discord.Game(name=f"Uptime: {uptime_str}"),
        status=discord.Status.online
    )

async def send_embed(channel, author, title, description, fields=None, color=0xFF5733):

    embed = Embed(title=title, description=f"{description}", color=color)

    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    await channel.send(embed=embed)

def format_uptime(delta):
    total_minutes = int(delta.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes}m"

async def keeed(): 
    global aaaa 
    aaaa += 1  
    await asyncio.sleep(5) 
    aaaa -= 0

async def timeout(guild, message):
            global timesThisKidHasPinged
            global chances
            global aaaa
            global pingMin

            timesThisKidHasPinged = 0
            chances = pingMin + 1
            aaaa = 0
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
                print(f"SENT {message.author} TO TIMEOUT FOR {timeoutLength}")
            except discord.Forbidden:

                await send_embed(
                    channel=message.channel,
                    author=message.author,
                    title="PERMISSION ERROR",
                    description=f"I DONT HAVE PERMISSION TO TIMEOUT {message.author.mention}, plz make sure my role is high enough and that i have administrator privileges! <@{guild.owner_id}>",
                    color=0xFF3333
                )
                print(f"COULDNT TIMEOUT {message.author}")
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
                print(f"ERROR: {e}")
            await message.delete()  
async def warn(message):
            global chances

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
            print(f"WARNED {message.author}")
            await message.delete()  

@client.event
async def on_message(message):
    global timesThisKidHasPinged
    global timeoutLength
    global pingMin
    global chances
    global aaaa
    global mineemum
    
    guild = message.guild

    if message.author == client.user:
        return
    
    if message.author.id == devId or (guild and message.author.id == guild.owner_id):
        msg = message.content.lower()

        if msg == "!exrbot uptime":
            delta = datetime.datetime.now() - start_time
            uptime_str = format_uptime(delta)
            await message.channel.send(f"i have been up for: {uptime_str}")
            return

        if msg == "!exrbot xareopinion":
            await message.channel.send("i hate him")
            return
    
    if (len(message.mentions) > 0 or message.mention_everyone) and message.author.id in kidsToKeepInCheck:
        asyncio.create_task(keeed())

        if message.mention_everyone:
            await timeout(guild, message)

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

        print(f"AAAA: {aaaa}, MINEEMUM: {mineemum}, totalPings: {totalPings}, chances: {chances}")

        if aaaa <= mineemum and totalPings <= mineemum:
            return

        if timesThisKidHasPinged <= pingMin and totalPings <= pingMin:
            await warn(chances, message)
        elif timesThisKidHasPinged >= pingMin and totalPings >= pingMin:
            await timeout(guild, message)

                #await message.channel.send(f"AN ERROR HAS OCCURRED: {e}\n<@{devId}>")
      
    #if message.content.startswith('$hello') and :
    #    print("USER ID FOUND IN kidsToKeepInCheck ", message.author.id)
    #    await message.channel.send('Hello!')

client.run(discordTOKEN)

