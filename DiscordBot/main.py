# too lazy to change anything here. Need help dm @nv9lx on discord.
import discord
from discord.ext import commands
import datetime
import random
import asyncio
import json
import datetime
import requests
import aiohttp
import os


# necessary apis
APIUrl = "https://devapi.frzn.app/"
APIUrlSecondary = "https://dev.frzn.app"
APIWorkerRequestLink = "https://access-control-worker.funwrlddoo.workers.dev/"
AuthorizationKey = "FRZNDEVPORTAL"


KeyApproval = 0
whitelisted = [1, 2, 3, 4]


link_webhook = "add linked logs webhook here"

valid_codes = {}
status_webhooks = {}
linked_users = {}

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

codes_file = "codes.json"
api_keys_file = "user_api_keys.json"

def load_status_webhooks():
    global status_webhooks
    try:
        with open("status_webhooks.json", "r") as file:
            status_webhooks = json.load(file)
    except FileNotFoundError:
        status_webhooks = {}

def save_status_webhooks():
    with open("status_webhooks.json", "w") as file:
        json.dump(status_webhooks, file)

try:
    with open('linked_users.json', 'r') as file:
        linked_users = json.load(file)
except FileNotFoundError:
    pass

load_status_webhooks()

@client.event
async def on_ready():
    guild_id = #server id  
    target_role_id = # member role id  
    exempt_user_id = #bot id  

    guild = client.get_guild(guild_id)
    if guild:
        target_role = guild.get_role(target_role_id)
        if target_role:
            for member in guild.members:
                if member.id != exempt_user_id:  
                    if target_role not in member.roles:
                        try:
                            await member.add_roles(target_role)
                            print(f"Added {target_role.name} to {member.display_name}")
                        except Exception as e:
                            print(f"Failed to add {target_role.name} to {member.display_name}: {e}")
                else:
                    print(f"Skipped adding {target_role.name} to user ID {exempt_user_id}")
        else:
            print(f"Role with ID {target_role_id} not found in the guild.")
    else:
        print(f"Guild with ID {guild_id} not found.")
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="Running V3"))
def load_codes():
    try:
        with open(codes_file, "r") as file:
            data = json.load(file)
            valid_codes.update(data["codes"])
    except FileNotFoundError:
        pass

def save_codes():
    with open(codes_file, "w") as file:
        data = {"codes": valid_codes}
        json.dump(data, file)

load_codes()

def load_user_api_keys():
    try:
        with open(api_keys_file, 'r') as file:
            user_api_keys = json.load(file)
    except FileNotFoundError:
        user_api_keys = {}
    return user_api_keys


def save_user_api_keys(user_api_keys):
    with open(api_keys_file, 'w') as file:
        json.dump(user_api_keys, file, indent=4)


user_api_keys = load_user_api_keys()

@client.command()
async def generate(ctx, amount: int, prefix: str = "", robux_value: str = ""):
    if ctx.author.id not in whitelisted:
        await ctx.send("You are not authorized to use this command.")
        return
    if amount <= 0:
        await ctx.send("Please specify a positive number of codes to generate.")
        return
    if amount >= 101:
        await ctx.send("A max of 100 codes can be generated at once.")
        return
    codes = []
    for i in range(amount):
        code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
        worth = f"{robux_value} Robux"
        valid_codes[f"{prefix}${code}"] = worth
        codes.append(f"`{prefix}${code}` ({worth})")
    save_codes()
    embed = discord.Embed(title=f"{amount} Codes Generated", color=0x0000FF)
    embed.add_field(name="Codes:", value='\n'.join(codes), inline=False)
    embed.set_footer(text="FRZN Softworks")
    await ctx.send(embed=embed)

@client.command()
async def redeem(ctx, code: str):
    worth = valid_codes.get(code)
    if worth is not None:
        del valid_codes[code]
        save_codes()
        dm_channel = await ctx.author.create_dm()
        await ctx.send(f"{ctx.author.mention}, please check your DMs for further instructions.")
        await dm_channel.send(f"Please send your ROBLOX username! Please have a gamepass worth: *** {worth} ***! ** IMPORTANT: Since this is BETA for username system it only supports gamepasses. **")
        def check(message):
            return message.author == ctx.author and message.channel == dm_channel
        try:
            gamepass_id_message = await client.wait_for('message', check=check, timeout=120)
        except asyncio.TimeoutError:
            await dm_channel.send("Sorry, you took too long to respond.")
            return
        gamepass_id = gamepass_id_message.content
        
        embed = discord.Embed(title="Code Redeemed", color=0xFF0000)
        embed.add_field(name="Code:", value=f"`{code}`", inline=False)
        embed.add_field(name="Redeemed by:", value=f"{ctx.author.mention} ({ctx.author.id})", inline=False)
        embed.add_field(name="Roblox Username:", value=f"`{gamepass_id}`", inline=False)
        embed.add_field(name="Worth:", value=f"**{worth}**", inline=False)
        embed.set_footer(text="FRZN Softworks")

        await ctx.send(f"{ctx.author.mention}, your code has been redeemed **successfully**!")
        
        yourself = client.get_user(KeyApproval)
        await yourself.send(embed=embed)
    else:
        await ctx.send(f"{ctx.author.mention}, this code is **invalid** or **used**. Please try again.")

@client.command()
async def validcodes(ctx):
    if ctx.author.id not in whitelisted:
        await ctx.send("You are not authorized to use this command.")
        return
    if not valid_codes:
        await ctx.send("There are no valid codes at the moment.")
        return
    embed = discord.Embed(title="Valid Codes", color=0xff69b4)
    embed.add_field(name="Codes:", value='\n'.join([f"`{valid_code}`" for valid_code in valid_codes]), inline=False)
    embed.set_footer(text="FRZN Softworks")
    await ctx.send(embed=embed)

@client.command()
async def custom(ctx, prefix: str, robux_value: str = ""):
    if ctx.author.id not in whitelisted:
        await ctx.send("You are not authorized to use this command.")
        return
    code = prefix
    worth = f"{robux_value} Robux"
    valid_codes[code] = worth
    save_codes()
    embed = discord.Embed(title="Code Generated", color=0x0000FF)
    embed.add_field(name="Code:", value=f"`{code}`", inline=False)
    embed.add_field(name="Worth:", value=f"**{worth}**", inline=False)
    embed.set_footer(text="FRZN Softworks")
    await ctx.send(embed=embed)



@client.command()
async def ban(ctx, member: discord.Member, *, reason: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not authorized to use this command.")
        return
    user_embed = discord.Embed(title="You Have Been Banned", color=0xFF0000)
    user_embed.add_field(name="Banned by:", value=ctx.author.display_name, inline=False)
    user_embed.add_field(name="Reason:", value=reason, inline=False)
    await member.send(embed=user_embed)
    
    watered_reason = f"FRZN_BAN: {reason}"
    await member.ban(reason=watered_reason)
    embed_server = discord.Embed(title="Member Banned", color=0xFF0000)
    embed_server.add_field(name="Banned Member:", value=member.mention, inline=False)
    embed_server.add_field(name="Banned by:", value=ctx.author.mention, inline=False)
    embed_server.set_footer(text="FRZN Softworks")
    await ctx.send(embed=embed_server)

    embed_log = discord.Embed(title="Member Banned", color=0xFF0000)
    embed_log.add_field(name="Banned Member:", value=member.mention, inline=False)
    embed_log.add_field(name="Banned by:", value=ctx.author.mention, inline=False)
    embed_log.add_field(name="Reason:", value=reason, inline=False)
    embed_log.set_footer(text="FRZN Softworks")

    if member.guild.id == 1100248381760213032:
        yourself = client.get_user(KeyApproval)
        await yourself.send(embed=embed_log)

@client.event
async def on_member_join(member):
    if member.guild.id == 1100248381760213032:
        channel = client.get_channel(1103848224353165442)
        await channel.send(f'Hello, {member.mention}!')

        dm_channel = await member.create_dm()
        intro_message = "Hi! Welcome to FRZN. Our server is all about this bot! We give away free robux. Want to know the process?, check out <#1177431441454403584>"
        await dm_channel.send(intro_message)

        autorole_id = 1105879411242324049
        autorole = member.guild.get_role(autorole_id)

        if autorole is not None:
            await member.add_roles(autorole)

@client.event
async def on_member_remove(member):
    if member.guild.id == 1100248381760213032:
        channel = client.get_channel(1103848224353165442)
        await channel.send(f'Bye, {member.display_name}!')


@client.command()
async def status(ctx, *, message: str):
    if ctx.author.id not in whitelisted:
        await ctx.send("You are not authorized to use this command.")
        return
        
    sent_to_servers = []
    
    for guild_id, webhook_url in status_webhooks.items():
        payload = {"content": message}
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            sent_to_servers.append(str(ctx.guild.get_member(guild_id)))
        except requests.exceptions.RequestException as e:
            print(f"Failed to send status message to webhook {webhook_url}: {e}")
    
    if sent_to_servers:
        sent_message = ", ".join(sent_to_servers)
        await ctx.send(f"Status message sent to servers with logstatus enabled")
    else:
        await ctx.send("No servers with logstatus enabled were found.")


@client.command()
@commands.has_permissions(administrator=True)
async def logstatus(ctx, webhook_url: str):
    global status_webhooks
    status_webhooks[ctx.guild.id] = webhook_url
    save_status_webhooks()
    await ctx.message.delete()
    await ctx.send(f"Log status webhook URL has been set for this server.")

@client.command()
async def commands(ctx):
    
    embed = discord.Embed(title="FRZN Commands", description="List of available commands and their descriptions:", color=0x00FF00)
    
    help_commands = [
        {"!commands", "This help command"},
        ("!generate <amount> <name> <worth>", "Generate redemption codes. **Permission Needed**"),
        ("!redeem <code>", "Redeem a code."),
        ("!validcodes", "List valid codes. **Permission Needed**"),
        ("!custom <code> <worth>", "Generate a custom code. **Permission Needed**"),
        ("!ban", "Ban a member. **Obtainable Permission**"),
        ("!logstatus <webhook_url>", "Sets your webhook for FRZN Announcements. **Obtainable Permission**"),
        ("!status <message>", "Makes a message to all servers. **Permission Needed**"),
        ("!linkuser <user>", "Links your RBX to your discord."),
        ("!adminlinkuser <mention> <n>", "Can remove peoples linked users. Can change them. **Permission Needed**"),
        ("!setpremium <linked_user>", "Links user to the premium version of FRZN **Permission Needed**"),
        ("!profile <mention>", "Shows users info"),
        ("!myapikey", "Gets an API key for developers wanting to use the FRZN API."),
        ("!deletecode <code>", "Deletes a code that has been generated"),
        ("!dm <mention> <message>", "DM's a message to the user from the bot!"),
    ]
    
    for command, description in help_commands:
        embed.add_field(name=command, value=description, inline=False)
    
    embed.set_footer(text="FRZN Softworks")
    await ctx.send(embed=embed)


@client.command()
async def linkuser(ctx, name):
    try:
        user_id = str(ctx.author.id)

        
        if user_id in linked_users:
            await ctx.send("You can't be linked again! Please contact FRZN Support Here: https://discord.gg/rQG3hVYG3Z")
            return
        
        name = name.lower()

        
        if name in linked_users.values():
            await ctx.send("Someone already has this username! Choose another.")
            return

        
        await ctx.send(f"Linked to account @{name} right now.")

        
        await ctx.author.send(f"You are now linked to @{name}")

        
        log_message = {
            "embeds": [{
                "title": "User Linked",
                "description": f"{ctx.author.mention} is now linked to @{name}",
                "color": 0x00FF00  
            }]
        }

        
        linked_users[user_id] = name
        with open('linked_users.json', 'w') as file:
            json.dump(linked_users, file)

        
        async with aiohttp.ClientSession() as session:
            async with session.post(link_webhook, data=json.dumps(log_message), headers={"Content-Type": "application/json"}):
                pass

    except Exception as e:
        print(f"An error occurred: {str(e)}")



@client.command()
async def adminlinkuser(ctx, mentioned_user: discord.User, new_user=None):
    
    if ctx.author.id in whitelisted:
        user_id = str(mentioned_user.id)

        
        if user_id in linked_users:
            
            removed_user = linked_users.pop(user_id)

            if new_user is not None:
                
                linked_users[user_id] = new_user

                new_user = new_user.lower()
            
            if new_user in linked_users.values():
                await ctx.send("Welcome Admin! There is someone with the exact username as this! Please choose another!")
            return

            
            with open('linked_users.json', 'w') as file:
                json.dump(linked_users, file)

            
            if new_user is None:
                await ctx.send(f"Removed {mentioned_user.mention}'s user.")
            else:
                await ctx.send(f"Changed {mentioned_user.mention}'s user to @{new_user}.")

            
            if new_user is None:
                await mentioned_user.send(f"An admin removed your linked user.")
            else:
                await mentioned_user.send(f"An admin changed your linked user to @{new_user}.")

            
            log_message = {
                "embeds": [{
                    "title": "User Removed",
                    "description": f"{mentioned_user.mention}'s user was removed{' and changed to ' + new_user if new_user else ''} by an admin.",
                    "color": 0xFF0000 if new_user is None else 0x00FF00  
                }]
            }

            
            async with aiohttp.ClientSession() as session:
                async with session.post(link_webhook, data=json.dumps(log_message), headers={"Content-Type": "application/json"}):
                    pass
        else:
            await ctx.send(f"@{mentioned_user}'s user is not linked.")
    else:
        await ctx.send("You do not have permission to use this command.")

@client.command()
async def setpremium(ctx, linked_username):
    
    if ctx.author.id in whitelisted:
        
        linked_user_id = None
        for user_id, username in linked_users.items():
            if username.lower() == linked_username.lower():
                linked_user_id = user_id
                break

        if linked_user_id is not None:
            
            linked_user = ctx.guild.get_member(int(linked_user_id))
            if linked_user:
                
                role_id = 1148785133332213790  
                role = ctx.guild.get_role(role_id)

                if role:
                    
                    await linked_user.add_roles(role)
                    await ctx.send(f"Given Premium to: {linked_user.mention}.")
                else:
                    await ctx.send("The specified role was not found on this server.")
            else:
                await ctx.send("The linked Discord user is not currently on this server.")
        else:
            await ctx.send(f"No user linked to the username {linked_username}.")
    else:
        await ctx.send("You do not have permission to use this command.")

@client.command()
async def profile(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    premium_role_id = 1148785133332213790
    premium_role = discord.utils.get(member.roles, id=premium_role_id)
    
    linked_username = linked_users.get(str(member.id), "N/A")  
    
    embed = discord.Embed(title=f"{member.display_name}", color=0x00FF00)
    embed.add_field(name="User ID", value=member.id, inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="Linked User", value=linked_username, inline=False)
    
    if premium_role:
        embed.add_field(name="Premium Status", value="<:FRZNPremiumV2:1157513094524833792>", inline=False)
        embed.set_footer(text="FRZN Softworks")
    else:
        embed.add_field(name="Premium Status", value="<:FRZNV2:1157513052074291273>", inline=False)
        embed.set_footer(text="FRZN Softworks")
    
    await ctx.send(embed=embed)


@client.command()
async def myapikey(ctx):
    user_id = str(ctx.author.id)
    
    
    if user_id in user_api_keys:
        api_key = user_api_keys[user_id]
    else:
        
        api_key = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=12))
        
        
        user_api_keys[user_id] = api_key
        save_user_api_keys(user_api_keys)
    if ctx.author.id in whitelisted:
        await ctx.author.send(f"Here is your FRZN API Key: {api_key}")
    else:
        await ctx.send(f"api keys made by nolzz. This is not available to the public yet.")

@client.command()
async def deletecode(ctx, code: str):
    if ctx.author.id not in whitelisted:
        await ctx.send("You are not authorized to use this command.")
        return

    if code in valid_codes:
        del valid_codes[code]
        save_codes()
        await ctx.send(f"Code `{code}` has been deleted.")
    else:
        await ctx.send(f"The specified code `{code}` does not exist or is not valid.")

@client.command()
async def dm(ctx, user: discord.User, *, message: str):
    if ctx.author.id not in whitelisted:
        await ctx.send("You are not authorized to use this command.")
        return

    
    if user:
        try:
            await user.send(message)
            await ctx.send(f"Message sent to {user.mention}: {message}")
        except discord.Forbidden:
            await ctx.send("I'm unable to send a message to that user.")
    else:
        await ctx.send("User not found. Please mention a valid user.")



client.run('bot token')