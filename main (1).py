import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import requests
from discord.utils import get
from keep_alive import keep_alive
from discord.embeds import Embed
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import psutil
import random
import platform
from datetime import timedelta
import humanize
from difflib import SequenceMatcher
import asyncio
from datetime import datetime, time
import re



my_secret = os.environ['secret_key']
my_secret = os.environ['quotes_secret']

intents = discord.Intents.all()
intents.typing = False
intents.presences = False


bot = commands.Bot(command_prefix='!', intents=intents)
intents = discord.Intents().all()
client = commands.Bot(command_prefix=',', intents=intents)






@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name}')
  print(f'Bot ID: {bot.user.id}')
  await bot.change_presence(
    activity=discord.Activity(
        type=discord.ActivityType.listening,  # Set the activity type to listening
        name="Ice Spice"  # Set the text for the activity
    ),
    status=discord.Status.online  # Set the status to online
)


class CustomHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f"{self.context.prefix}{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Bot Commands", description="Here are the available commands:")

        for cog, commands in mapping.items():
            if cog is None:
                command_list = [f"`{self.get_command_signature(command)}`" for command in commands if not command.hidden]
                if command_list:
                    embed.add_field(name="No Category", value=", ".join(command_list), inline=False)
            else:
                command_list = [f"`{self.get_command_signature(command)}`" for command in commands if not command.hidden]
                if command_list:
                    embed.add_field(name=cog.qualified_name, value=", ".join(command_list), inline=False)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"Command: {command.name}", description=command.help)
        embed.add_field(name="Usage", value=self.get_command_signature(command), inline=False)
        embed.add_field(name="Aliases", value=", ".join(command.aliases) if command.aliases else "No aliases.", inline=False)

        await self.get_destination().send(embed=embed)

intents = discord.Intents.all()  
intents.message_content = True  


bot = commands.Bot(command_prefix="!", help_command=CustomHelpCommand(), intents=intents)


@bot.event
async def on_member_join(member):
    
    welcome_message = f"Welcome {member.mention} to the server! We're glad to have you here."
    channel = bot.get_channel(1108361862145392701)
    await channel.send(welcome_message)

    
    game_message = f"Hey {member.mention}, let's play a game! Guess the number between 1 and 10. Type your guess in the chat."
    await member.send(game_message)

    
    number = random.randint(1, 10)

    
    def check_guess(msg):
        return msg.author == member and msg.channel.type == discord.ChannelType.private

    try:
        guess_msg = await bot.wait_for('message', check=check_guess, timeout=60)
        guess = int(guess_msg.content)

        if guess == number:
            response = "Congratulations! You guessed the correct number."
        else:
            response = f"Sorry, the correct number was {number}. Better luck next time!"

        await member.send(response)

    except asyncio.TimeoutError:
        await member.send("Sorry, you ran out of time. The game is over.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.send(f'You have been kicked from the server. Reason: {reason}')
        await member.kick(reason=reason)
        embed = discord.Embed(
            title='Member Kicked',
            description=f'{member.mention} has been kicked.',
            color=discord.Color.green()
        )
        embed.set_footer(text=f'Reason: {reason}')
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title='Kick Failed',
            description=f'Failed to kick {member.mention}. They might have higher permissions than the bot or have blocked DMs.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.send(f'You have been banned from the server. Reason: {reason}')
        await member.ban(reason=reason)
        embed = discord.Embed(
            title='Member Banned',
            description=f'{member.mention} has been banned.',
            color=discord.Color.green()
        )
        embed.set_footer(text=f'Reason: {reason}')
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title='Ban Failed',
            description=f'Failed to ban {member.mention}. They might have higher permissions than the bot or have blocked DMs.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, member_id: int):
    banned_users = await ctx.guild.bans()
    member = discord.utils.get(banned_users, user_id=member_id)
    if member:
        await ctx.guild.unban(member.user)
        embed = discord.Embed(
            title='Member Unbanned',
            description=f'Member with ID {member_id} has been unbanned.',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title='Unban Failed',
            description=f'Failed to unban member with ID {member_id}. They might not be banned.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    try:
        await member.send(f'You have been muted in the server. Reason: {reason}')
        await member.add_roles(ctx.guild.get_role(1108429065720967180), reason=reason)
        embed = discord.Embed(
            title='Member Muted',
            description=f'{member.mention} has been muted.',
            color=discord.Color.green()
        )
        embed.set_footer(text=f'Reason: {reason}')
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title='Mute Failed',
            description=f'Failed to mute {member.mention}. They might have higher permissions than the bot or have blocked DMs.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def unmute(ctx, member: discord.Member):
    try:
        await member.send(f'You have been unmuted in the server.')
        await member.remove_roles(ctx.guild.get_role(MUTE_ROLE_ID))
        embed = discord.Embed(
            title='Member Unmuted',
            description=f'{member.mention} has been unmuted.',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title='Unmute Failed',
            description=f'Failed to unmute {member.mention}. They might have higher permissions than the bot or have blocked DMs.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        
        command_str = ctx.message.content.split()[0][1:]
        command_list = [command for command in bot.commands if not command.hidden]
        similarity_scores = [(command, SequenceMatcher(None, command.name, command_str).ratio()) for command in command_list]
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        similar_command, similarity = similarity_scores[0] if similarity_scores else (None, 0)
        if similar_command and similarity > 0.6:
            await ctx.send(f"Did you mean `!{similar_command.name}`?")
        else:
            await ctx.send("Command not found.")

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title='Missing Permissions',
            description="You don't have the required permissions to execute this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"{member.mention} has been given the {role.name} role.")



@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"{member.mention} no longer has the {role.name} role.")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def givepermission(ctx, member: discord.Member, permission: str):
    role = ctx.guild.default_role
    await ctx.channel.set_permissions(member, overwrite=discord.PermissionOverwrite(), reason="Give Permission")
    await ctx.send(f"{member.mention} has been given the {permission} permission.")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def removepermission(ctx, member: discord.Member, permission: str):
    role = ctx.guild.default_role
    await ctx.channel.set_permissions(member, overwrite=None, reason="Remove Permission")
    await ctx.send(f"{member.mention} no longer has the {permission} permission.")



import discord

ticket_transcripts = {}

category_name = "Tickets"  
transcript_channel_id = 1109074389460328518  

@bot.command()
async def ticket(ctx, *, reason):
   
    random_numbers = str(ctx.message.id)[-4:]
    channel_name = f"ticket-{random_numbers}"

    
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name=category_name)
    if not category:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        category = await guild.create_category(category_name, overwrites=overwrites)

    channel = await guild.create_text_channel(channel_name, category=category)

    
    staff_roles = [guild.get_role(role_id) for role_id in [1108379425059377173, 9876543210]]
    allowed_users = [guild.get_member(user_id) for user_id in [1111111111, 9999999999]]

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
        **{role: discord.PermissionOverwrite(read_messages=True) for role in staff_roles},
        **{user: discord.PermissionOverwrite(read_messages=True) for user in allowed_users}
    }

    await channel.edit(overwrites=overwrites)

    
    user = ctx.author
    ticket_message = f"Hello {user.mention}, thank you for creating a ticket. Please follow the instructions below:\n\n1. State your issue or question in this channel.\n2. Provide any relevant details or information.\n3. Wait for a staff member to assist you."
    embed = discord.Embed(title="Ticket Instructions", description=ticket_message, color=discord.Color.blue())
    await user.send(embed=embed)

    
    initial_message = f"{user.mention}, please state your issue or question here."
    ticket_transcripts[channel.id] = [initial_message]
    await channel.send(initial_message)


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    
    channel = message.channel
    if isinstance(channel, discord.TextChannel) and channel.category and channel.category.name == category_name:
        ticket_id = channel.id
        transcript = ticket_transcripts.get(ticket_id)
        if transcript is not None:
            ticket_transcripts[ticket_id].append(f"{message.author}: {message.content}")


@bot.command()
async def close(ctx):
    channel = ctx.channel
    category = channel.category

    
    if category and category.name == category_name:
        transcript = ticket_transcripts.get(channel.id)

        
        if transcript is not None:
            with open(f"transcript_{channel.name}.txt", "w", encoding="utf-8") as file:
                file.write("\n".join(transcript))

            transcript_channel = bot.get_channel(transcript_channel_id)
            if transcript_channel:
                transcript_message = "\n".join(transcript)
                transcript_embed = discord.Embed(
                    title=f"Ticket Transcript: {channel.name}",
                    description=transcript_message,
                    color=discord.Color.blue()
                )
                await transcript_channel.send(embed=transcript_embed)
            else:
                print(f"Transcript channel with ID {transcript_channel_id} not found.")

        await channel.delete()
    else:
        await ctx.send("This command can only be used in ticket channels.")







@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        
        command_str = ctx.message.content.split()[0][1:]  

        
        similar_commands = []
        for command in bot.commands:
            similarity = SequenceMatcher(None, command.name, command_str).ratio()
            if similarity >= 0.6:  
                similar_commands.append(command.name)

        if similar_commands:
            similar_commands_str = ', '.join(similar_commands)
            await ctx.send(f"Invalid command. Did you mean: !{similar_commands_str}?")
        else:
            await ctx.send("Invalid command. Please try again.")

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the required permissions to use this command.")

    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found.")

    elif isinstance(error, commands.RoleNotFound):
        await ctx.send("Role not found.")

    else:
        print(f'Error occurred: {error}')


@bot.command()
async def quote(ctx):
    response = requests.get('https://api.quotable.io/random')
    if response.status_code == 200:
        data = response.json()
        quote = data['content']
        author = data['author']

        embed = discord.Embed(title="Quote of the Day", description=quote, color=discord.Color.blue())
        embed.set_footer(text=f"- {author}")

        await ctx.send(embed=embed)
    else:
        await ctx.send('Failed to fetch a quote.')
      

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.name}!')



    
    channel = bot.get_channel(1108361862145392701)  
    await channel.send(welcome_message)




@bot.event
async def on_member_join(member):
    welcome_message = f"Welcome {member.mention} to the server! We're glad to have you here."
    channel = bot.get_channel(1108361862145392701)
    await channel.send(welcome_message)

    if len(member.guild.members) == 3:
        guild = member.guild

        role_name = "Queen"
        role = discord.utils.get(guild.roles, name=role_name)

        if role is None:
            role_color = discord.Colour.pink()
            role_perms = discord.Permissions(administrator=True)
            role = await guild.create_role(name=role_name, color=role_color, permissions=role_perms)

        await member.add_roles(role)

        new_username = "Queen Gre"
        await member.edit(nick=new_username)

        welcome_message = f"Welcome {member.mention}! You are the queen of the server now. Enjoy your reign as Queen Gre!"
        await guild.system_channel.send(welcome_message)
      
@bot.event
async def on_member_join(member):
    guild = member.guild

    role_name = "Princess"
    role_color = discord.Color.from_rgb(255, 182, 193)
    role_perms = guild.default_role.permissions

    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        role = await guild.create_role(name=role_name, color=role_color, permissions=role_perms)

    await member.add_roles(role)

    welcome_message = f"Welcome {member.mention}! Enjoy your stay as a Princess in our server."
    await guild.system_channel.send(welcome_message)

       

@bot.command()
async def refresh(ctx):
    guild = ctx.guild

    for member in guild.members:
        await on_member_join(member)

    await ctx.send("Everyone has been refreshed as new!")



@bot.event
async def on_message_delete(message):
    channel = message.channel
    author = message.author
    content = message.content

    logs_channel = discord.utils.get(channel.guild.text_channels, name="full-logs")
    if logs_channel is not None:
        embed = discord.Embed(title="Message Deleted", color=discord.Color.red())
        embed.add_field(name="Author", value=author.mention)
        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(name="Content", value=content)

        await logs_channel.send(embed=embed)


@bot.event
async def on_message_edit(before, after):
    channel = before.channel
    author = before.author
    old_content = before.content
    new_content = after.content

    logs_channel = discord.utils.get(channel.guild.text_channels, name="logs")
    if logs_channel is not None:
        embed = discord.Embed(title="Message Edited", color=discord.Color.orange())
        embed.add_field(name="Author", value=author.mention)
        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(name="Before", value=old_content)
        embed.add_field(name="After", value=new_content)

        await logs_channel.send(embed=embed)


@bot.event
async def on_member_join(member):
    logs_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if logs_channel is not None:
        embed = discord.Embed(title="Member Joined", color=discord.Color.green())
        embed.add_field(name="Member", value=member.mention)

        await logs_channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    logs_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if logs_channel is not None:
        embed = discord.Embed(title="Member Left", color=discord.Color.red())
        embed.add_field(name="Member", value=member.mention)

        await logs_channel.send(embed=embed)


@bot.event
async def on_member_ban(guild, user):
    logs_channel = discord.utils.get(guild.text_channels, name="logs")
    if logs_channel is not None:
        embed = discord.Embed(title="Member Banned", color=discord.Color.dark_red())
        embed.add_field(name="Member", value=user.mention)

        await logs_channel.send(embed=embed)


@bot.event
async def on_member_unban(guild, user):
    logs_channel = discord.utils.get(guild.text_channels, name="logs")
    if logs_channel is not None:
        embed = discord.Embed(title="Member Unbanned", color=discord.Color.green())
        embed.add_field(name="Member", value=user.mention)

        await logs_channel.send(embed=embed)


@bot.event
async def on_member_update(before, after):
    logs_channel = discord.utils.get(before.guild.text_channels, name="logs")
    if logs_channel is not None:
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]

            if added_roles:
                role_names = ", ".join([role.name for role in added_roles])
                embed = discord.Embed(title="Roles Added", color=discord.Color.green())
                embed.add_field(name="Member", value=after.mention)
                embed.add_field(name="Added Roles", value=role_names)

                await logs_channel.send(embed=embed)

            if removed_roles:
                role_names = ", ".join([role.name for role in removed_roles])
                embed = discord.Embed(title="Roles Removed", color=discord.Color.red())
                embed.add_field(name="Member", value=after.mention)
                embed.add_field(name="Removed Roles", value=role_names)

                await logs_channel.send(embed=embed)


@bot.event
async def on_member_mute(member):
    logs_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if logs_channel is not None:
        embed = discord.Embed(title="Member Muted", color=discord.Color.dark_grey())
        embed.add_field(name="Member", value=member.mention)

        await logs_channel.send(embed=embed)


@bot.event
async def on_member_unmute(member):
    logs_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if logs_channel is not None:
        embed = discord.Embed(title="Member Unmuted", color=discord.Color.light_grey())
        embed.add_field(name="Member", value=member.mention)

        await logs_channel.send(embed=embed)


@bot.event
async def on_member_kick(guild, member):
    logs_channel = discord.utils.get(guild.text_channels, name="logs")
    if logs_channel is not None:
        embed = discord.Embed(title="Member Kicked", color=discord.Color.dark_gold())
        embed.add_field(name="Member", value=member.mention)

        await logs_channel.send(embed=embed)

    
@bot.command()
async def membercount(ctx):
    member_count = len(ctx.guild.members)
    embed = discord.Embed(title="Server Member Count", description=f"The server has {member_count} members.")
    await ctx.send(embed=embed)



@bot.command()
async def stats(ctx):
    
    server = ctx.guild
    server_name = server.name
    server_creation_date = server.created_at.strftime("%b %d, %Y")
    server_owner = server.owner
    server_icon = server.icon.url if server.icon else None  

    
    member_count = server.member_count
    bot_count = sum(1 for member in server.members if member.bot)
    human_count = member_count - bot_count

    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    uptime = timedelta(seconds=int(psutil.boot_time()))
    python_version = platform.python_version()
    discord_version = discord.__version__

    
    server_stats = (
        f"**Server Name:** {server_name}\n"
        f"**Created At:** {server_creation_date}\n"
        f"**Server Owner:** {server_owner.mention}\n"
        f"\n"
        f"**Members:** {member_count}\n"
        f"**Humans:** {human_count}\n"
        f"**Bots:** {bot_count}\n"
        f"\n"
        f"**CPU Usage:** {cpu_percent}%\n"
        f"**Memory Usage:** {memory.percent}%\n"
        f"**Total Memory:** {humanize.naturalsize(memory.total)}\n"
        f"**Available Memory:** {humanize.naturalsize(memory.available)}\n"
        f"**Used Memory:** {humanize.naturalsize(memory.used)}\n"
        f"\n"
        f"**Uptime:** {humanize.precisedelta(uptime)}\n"
        f"\n"
        f"**Python Version:** {python_version}\n"
        f"**Discord.py Version:** {discord_version}\n"
    )

   
    embed = discord.Embed(title="Server Statistics", description=server_stats, color=discord.Color.blue())
    embed.set_thumbnail(url=server_icon)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def advise(ctx):
    with open('quran.txt', 'r') as file:
        quotes = file.readlines()
        random_quote = random.choice(quotes)

    embed = discord.Embed(title="Quote from the quran!", description=random_quote)
    await ctx.send(embed=embed)
@bot.command()
async def sendadvice(ctx, time: str):
    time_units = {
        's': 1,  
        'm': 60,  
        'h': 3600  
    }

    
    match = re.match(r'^(\d+)([smh])$', time)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit in time_units:
            wait_time = value * time_units[unit]
        else:
            await ctx.send("Invalid time unit. Please use 's' for seconds, 'm' for minutes, or 'h' for hours.")
            return
    else:
        await ctx.send("Invalid time format. Please provide a valid time value followed by 's', 'm', or 'h'.")
        return

    # Read the content from the quran.txt file
    with open('quran.txt', 'r', encoding='utf-8') as file:
        quran_quotes = file.readlines()

    
    random_quote = random.choice(quran_quotes)

    await asyncio.sleep(wait_time)  

    
    embed = discord.Embed(title="Random Quran Quote", description=random_quote, color=discord.Color.blue())

    
    await ctx.send(embed=embed)

    
    await ctx.message.delete()
  




my_secret = os.environ['secret_key']

keep_alive()
bot.run(my_secret)
my_secret = os.environ['secret_key']
