import asyncio
import discord
from bs4 import BeautifulSoup
import aiohttp
from discord.ext import commands
import datetime

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=discord.Intents.default(),
    help_command=None,
)

doing = False

@bot.event
async def on_ready():
    print("Bot is ready!")


@bot.command()
async def pulse(ctx):
    """
    Reverse engineer macreconline.ca to get API endpoints :p
    """
    async with aiohttp.ClientSession() as session:
        payloads = [
            {
                "facilityId": "0986c0ef-0cc6-4659-9f7c-925af22a98c6",
                "occupancyDisplayType": "00000000-0000-0000-0000-000000004488",
            },
            {
                "facilityId": "7a0d7831-5fa8-4bfb-804b-0128d1dd6a18",
                "occupancyDisplayType": "00000000-0000-0000-0000-000000004488",
            },
            {
                "facilityId": "da4739b0-2ecb-4a55-9247-b411669f4ad8",
                "occupancyDisplayType": "00000000-0000-0000-0000-000000004488",
            },
        ]
        tasks = []
        for payload in payloads:
            tasks.append(fetch(payload))
        results = await asyncio.gather(*tasks)
        embed = discord.Embed(
            title="The Pulse Stats",
            description="Live Stats! More live than the actual website",
            color=0x00FF00,
        )
        embed.add_field(
            name="the Pulse | Sport Hall", value=f"`{results[0][0]} | {results[0][1]}`"
        )
        embed.add_field(
            name="Pop Up Pulse", value=f"`{results[1][0]} | {results[1][1]}`"
        )
        embed.add_field(
            name="Track Pulse", value=f"`{results[2][0]} | {results[2][1]}`"
        )
        await ctx.send(embed=embed)


@bot.command(name="runutil")
async def runutil(ctx):
    global doing
    if doing:
        return await ctx.send("`Session already in progress.`")

    payloads = [
        {
            "facilityId": "0986c0ef-0cc6-4659-9f7c-925af22a98c6",
            "occupancyDisplayType": "00000000-0000-0000-0000-000000004488",
        },
        {
            "facilityId": "7a0d7831-5fa8-4bfb-804b-0128d1dd6a18",
            "occupancyDisplayType": "00000000-0000-0000-0000-000000004488",
        },
        {
            "facilityId": "da4739b0-2ecb-4a55-9247-b411669f4ad8",
            "occupancyDisplayType": "00000000-0000-0000-0000-000000004488",
        },
    ]
    tasks = []
    for payload in payloads:
        tasks.append(fetch(payload))
    results = await asyncio.gather(*tasks)
    embed = create_embed(results)
    msg = await ctx.send(embed=embed)
    doing = True
    while True:
        tasks = []
        await asyncio.sleep(360)
        for payload in payloads:
            tasks.append(fetch(payload))
        res = await asyncio.gather(*tasks)
        new_embed = create_embed(res)
        await msg.edit(embed=new_embed)


def create_embed(results):
    embed = discord.Embed(
        title="The Pulse Stats",
        description=f"`Live Stats! More live than the actual website\nUpdate number: {update}`",
        color=0x00FF00,
        timestamp=datetime.datetime.utcnow(),
    )
    embed.add_field(
        name="the Pulse | Sport Hall", value=f"`{results[0][0]} | {results[0][1]}`"
    )
    embed.add_field(name="Pop Up Pulse", value=f"`{results[1][0]} | {results[1][1]}`")
    embed.add_field(name="Track Pulse", value=f"`{results[2][0]} | {results[2][1]}`")

    return embed


async def fetch(payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://macreconline.ca/FacilityOccupancy/GetFacilityData", data=payload
        ) as r:
            res = await r.text()
            soup = BeautifulSoup(res, "html.parser")
            max_cap = soup.find("p", {"class": "max-occupancy"}).get_text()
            occupancy = soup.find("p", {"class": "occupancy-count"}).get_text()
            return (occupancy, max_cap[15:])


bot.run("BOT_TOKEN")
"""
@infiniteregrets (Mehul)
https://github.com/infiniteregrets
"""