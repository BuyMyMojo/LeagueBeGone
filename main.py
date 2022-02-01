import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import tasks
from datetime import datetime
import time
import os

client = nextcord.Client(intents=nextcord.Intents.all())

TESTING_GUILD_ID = 915068875551440977
BotAdmins = [383507911160233985]
game_title = "Type ?help"

client.league_tracker = dict()
client.CurrentDate = datetime.now().date()


@tasks.loop(seconds=60)
async def league_tracker_loop():
    processed_users = []
    if client.CurrentDate is not datetime.now().date():
        client.league_tracker.clear()
        client.CurrentDate = datetime.now().date()


    for guild in client.guilds:  # Get all servers
        for member in guild.members:  # Get all users in said servers
            if member.activity is not None:
                if member.id not in processed_users:  # Check if user is playing a game, not a bot and not already processed from another server
                    if member.activity.name == game_title:  # Check if they are playing the game
                        if member.id in client.league_tracker:  # Check if they are already in the play time tracking dict
                            if client.league_tracker[member.id][1] > 7200:  # Get banned if you hit that 2 hour mark lmao -- Not actually banning yet until I can confirm it works
                                channel = client.get_user(383507911160233985)  # Send the DM directly to me since I'm testing on a bot and not an alt

                                mutuals = channel.mutual_guilds
                                mutual_content = ""
                                for guilds in mutuals:
                                    mutual_content = f"{mutual_content}{guilds.name} - {guilds.owner.name}\n"

                                await channel.send(
                                    f"You have been playing `{game_title}` for 2 hours! This is the limit of play time allowed by this bot within 24hours. you will be banned in these servers(Server owner listed next to them so you can contact them):\n```{mutual_content}```")
                                await guild.ban(client.get_user(member.id))
                                processed_users.append(member.id)
                            elif member.id not in processed_users:  # If member not already processed this loop
                                now = time.time()
                                time_stuff = client.league_tracker.get(member.id)[1]
                                then = float(client.league_tracker.get(member.id)[0])
                                td = now - then  # Work out time since last check. using this instead of just adding the loop time for accuracy with larger server counts

                                play_time = float(float(time_stuff) + td)
                                update_dict = {member.id: [now, play_time]}
                                client.league_tracker.update(update_dict)
                                processed_users.append(member.id)

                                if 1845 > client.league_tracker[member.id][1] > 5400:  # if you have played for an hour and a half send a warning
                                    channel = client.get_user(383507911160233985)  # Send the DM directly to me since I'm testing on a bot and not an alt

                                    mutuals = channel.mutual_guilds
                                    mutual_content = ""
                                    for guilds in mutuals:
                                        mutual_content = f"{mutual_content}{guilds.name} - Owner: {guilds.owner.name}\n"

                                    await channel.send(f"You have been playing `{game_title}` for {round(time_stuff / 60)} minutes! if you play for another {120 - round(time_stuff / 60)} minutes you will be banned in these servers:\n```{mutual_content}```")
                        else:  # If member isn't already in the dict add them
                            now = time.time()
                            play_time = float(0)
                            update_dict = {member.id: [now, play_time]}
                            client.league_tracker.update(update_dict)
                            processed_users.append(member.id)
    print("LeagueTracker triggered")
    return


@client.event
async def on_ready():
    await client.change_presence(activity=nextcord.Game(name="Screw your league time"))
    print(f"Online as: {client.user.name}")
    league_tracker_loop.start()


@client.slash_command(guild_ids=[TESTING_GUILD_ID], description="Allows bot admins to shutdown the bot")
async def shutdown_bot(interaction: Interaction):
    """Shuts down the bot"""
    if interaction.user.id in BotAdmins:
        await interaction.response.send_message('Exiting now!')
        exit(420)
    else:
        await interaction.response.send_message('You do not have permission to shutdown the bot')


@client.slash_command(guild_ids=[TESTING_GUILD_ID], description=f"Check a users '{game_title}' play time logged today")
async def playtime_logged(
        interaction: Interaction,
        player: nextcord.Member = SlashOption(name="user", description="@ the Member you want to check")
):
    """Check a users play time logged today"""
    if player.id in client.league_tracker:
        time_stuff = client.league_tracker.get(player.id)[1]
        await interaction.response.send_message(f"{player.name} has played for {time_stuff / 60} minutes today", ephemeral=True)
    else:
        await interaction.response.send_message(f"{player.name} has not played today",ephemeral=True)


# Random command so I can trigger debugging
@client.slash_command(guild_ids=[TESTING_GUILD_ID], description="This literally is just so I can trigger debugging")
async def debug(interaction: Interaction):
    """This literally is just so I can trigger debugging"""
    if interaction.user.id in BotAdmins:
        await interaction.response.send_message("Debugging now", ephemeral=True)
        print()

client.run(os.environ.get('LeagueBeGone_Token'))
