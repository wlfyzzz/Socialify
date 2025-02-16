import asyncio
import json
import os
from datetime import datetime

import nextcord
import requests
from nextcord import Interaction, SlashOption, ButtonStyle
from nextcord.ext import commands, tasks
from nextcord.ui import View, Button
from supabase import Client, create_client

with open("config.json", "r") as f:
    config = json.load(f)

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BOT_TOKEN = config["token"]
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="s.", intents=intents)

cache = {}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    my_task.start()


def create_embed(
    title: str,
    description: str,
    url: str = None,
    author_name: str = None,
    author_url: str = None,
    image_url: str = None,
    thumbnail_url: str = None,
    color: nextcord.Color = nextcord.Color.blurple(),
):
    embed = nextcord.Embed(title=title, description=description, color=color)
    if url:
        embed.url = url
    if author_name:
        embed.set_author(name=author_name, url=author_url)
    if image_url:
        embed.set_image(url=image_url)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    embed.timestamp = datetime.now()
    return embed


async def send_notification(channel_id: int, embed: nextcord.Embed, view: View = None, ping=True):
    channel = bot.get_channel(channel_id)
    if channel:
        if ping == True:
            await channel.send(content="@everyone", embed=embed, view=view)
        else:
            await channel.send(embed=embed, view=view)
    else:
        print(f"Channel {channel_id} not found.")


class LinkButton(Button):
    def __init__(self, url: str, label: str = "View Content"):
        super().__init__(style=ButtonStyle.link, url=url, label=label)


@tasks.loop(seconds=10)
async def my_task():
    global cache
    response = supabase.table("data").select("*").execute()
    data = response.data
    for item in data:
        type = item["type"]
        username = item["username"]
        channel = item["channel"]
        cache_key = f"{type}_{username}"

        try:
            fetched = requests.get(f"http://localhost:5000/{type}/{username}")
            fetched.raise_for_status()
            objects = fetched.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {type} {username}: {e}")
            continue

        if type == "twitter":
            await handle_twitter_notification(objects, username, channel, cache_key)
        elif type == "youtube":
            await handle_youtube_notification(objects, username, channel, cache_key)
        elif type == "twitch":
            await handle_twitch_notification(objects, username, channel, cache_key)
        elif type == "kick":
            await handle_kick_notification(objects, username, channel, cache_key)
        elif type == "tiktok":
            await handle_tiktok_notification(objects, username, channel, cache_key)


async def handle_twitter_notification(objects, username, channel, cache_key):
    global cache
    if "new_tweets" not in objects:
        print(f"{username} is suspended from twitter. Cannot fetch tweets")
        view = View()
        view.add_item(LinkButton(url="https://help.x.com/en/managing-your-account/suspended-x-accounts",label="View more"))
        await send_notification(
    channel,
    embed=create_embed(
        title="Account Suspended on X (Twitter)",
        description=(
            f"We've detected that the X (Twitter) account **{username}** has"
            " been suspended.\n\nDue to this suspension, we are unable to"
            " retrieve tweets from this account and have temporarily disabled"
            " notifications for it."
        ),
        url="https://help.x.com/en/managing-your-account/suspended-x-accounts",
    ),
    ping=False, view=view
)

        query = supabase.table("data").delete().eq("channel", channel).eq("username", username).execute()
        return

    for tweet in objects["new_tweets"]:
        tweet_id = tweet["id"]
        if cache.get(cache_key) != tweet_id:
            embed = create_embed(
                title=f"New tweet from {tweet['user']['name']}",
                description=tweet["content"],
                url=tweet["url"],
                author_name=tweet["user"]["name"],
                author_url=tweet["user"]["url"],
            )
            view = View()
            view.add_item(LinkButton(url=tweet["url"]))
            await send_notification(channel, embed, view)
            cache[cache_key] = tweet_id
        else:
            pass


async def handle_youtube_notification(objects, username, channel, cache_key):
    global cache
    if "new_videos" not in objects:
        print(f"No 'new_videos' found in response for YouTube {username}")
        return

    for video in objects["new_videos"]:
        video_id = video["url"]
        if cache.get(cache_key) != video_id:
            embed = create_embed(
                title=f"New video from {video['channel_name']}",
                description=video["title"],
                url=video["url"],
                author_name=video["channel_name"],
                author_url=video["channel_url"],
                thumbnail_url=video["thumbnail"],
            )
            view = View()
            view.add_item(LinkButton(url=video["url"]))
            await send_notification(channel, embed, view)
            cache[cache_key] = video_id
        else:
            pass


async def handle_twitch_notification(objects, username, channel, cache_key):
    global cache
    if "live" not in objects:
        print(f"No 'data' found in response for Twitch {username}")
        return

    is_live = objects["live"].get("live", False)
    if cache.get(cache_key) != is_live and is_live:
        embed = create_embed(
            title=f"{objects['live']['username']} is now live on Twitch!",
            description=objects["live"]["title"],
            url=f"https://www.twitch.tv/{username}",
            author_name=objects["live"]["username"],
            author_url=f"https://www.twitch.tv/{username}",
            image_url=objects["live"]["preview"],
        )
        view = View()
        view.add_item(LinkButton(url=f"https://www.twitch.tv/{username}"))
        await send_notification(channel, embed, view)
        cache[cache_key] = is_live
    else:
        pass


async def handle_kick_notification(objects, username, channel, cache_key):
    global cache
    is_live = objects["live"]
    if cache.get(cache_key) != is_live and is_live:
        embed = create_embed(
            title=f"{objects['user']['slug']} is now live on Kick!",
            description=objects["user"]["livestream"]["session_title"],
            url=f"https://kick.com/{objects['user']['slug']}",
            author_name=objects["user"]["slug"],
            author_url=f"https://kick.com/{objects['user']['slug']}",
            image_url=objects["live"]["thumbnail"]["url"],
        )
        view = View()
        view.add_item(LinkButton(url=f"https://kick.com/{objects['user']['slug']}"))
        await send_notification(channel, embed, view)
        cache[cache_key] = is_live
    else:
        pass


async def handle_tiktok_notification(objects, username, channel, cache_key):
    global cache
    if not isinstance(objects, list):
        print(f"Unexpected response format for TikTok {username}: {objects}")
        return

    for video in objects:
        video_id = video["id"]
        if cache.get(cache_key) != video_id:
            embed = create_embed(
                title=f"New TikTok from {video['author']['nickname']}",
                description=video["desc"],
                url=video["webVideoUrl"],
                author_name=video["author"]["nickname"],
                author_url=f"https://www.tiktok.com/@{video['author']['uniqueId']}",
                thumbnail_url=video["cover"],
            )
            view = View()
            view.add_item(LinkButton(url=video["webVideoUrl"]))
            await send_notification(channel, embed, view)
            cache[cache_key] = video_id
        else:
            pass


@bot.slash_command(
    name="list-pings",
    description="List ping configurations for this server.",
)
async def list_pings(
    interaction: Interaction,
    scope: str = SlashOption(
        name="scope",
        description="List pings for the current channel or the entire server.",
        choices={"Channel": "channel", "Server": "server"},
        required=True,
    ),
):
    await interaction.response.defer(ephemeral=True)

    if scope == "channel":
        channel_id = interaction.channel.id
        query = supabase.table("data").select("*").eq("channel", channel_id)
        embed_title = f"Ping Configurations - This Channel"
        embed_description = f"Listing configurations for {interaction.channel.mention}."
    elif scope == "server":
        query = supabase.table("data").select("*")
        embed_title = "Ping Configurations - This Server"
        embed_description = "Listing all ping configurations for this server."
    else:
        await interaction.followup.send("Invalid scope selected.", ephemeral=True)
        return

    try:
        response = query.execute()
        data = response.data

        if not data:
            await interaction.followup.send(
                "No ping configurations found for the selected scope.",
                ephemeral=True,
            )
            return

        description = ""
        for item in data:
            type = item["type"]
            username = item["username"]
            channel_id = item["channel"]
            channel = bot.get_channel(channel_id)
            channel_mention = (
                channel.mention if channel else f"Channel ID: {channel_id}"
            )

            description += f"• **{username}** on **{type}** in {channel_mention}\n"

        embed = nextcord.Embed(
            title=embed_title,
            description=embed_description,
            color=nextcord.Color.blurple(),
        )
        embed.add_field(name="Configurations:", value=description, inline=False)
        embed.set_footer(
            text=f"Requested by {interaction.user.name}",
            icon_url=interaction.user.avatar.url,
        )

        messages = []
        if len(embed) > 6000:
            messages = []
            while len(description) > 4096:
                split_index = description[:4096].rfind("\n")
                if split_index == -1:
                    split_index = 4096
                messages.append(description[:split_index])
                description = description[split_index:]
            messages.append(description)

            for message in messages:
                embed = nextcord.Embed(
                    title=embed_title,
                    description=embed_description,
                    color=nextcord.Color.blurple(),
                )
                embed.add_field(name="Configurations:", value=message, inline=False)
                embed.set_footer(
                    text=f"Requested by {interaction.user.name}",
                    icon_url=interaction.user.avatar.url,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

        else:
            await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        await interaction.followup.send(
            f"An error occurred while listing ping configurations: {e}",
            ephemeral=True,
        )


@bot.slash_command(
    name="add-ping",
    description="Add a channel to ping for in a channel [ADMIN ONLY]",
)
async def addping(
    interaction: Interaction,
    user: str,
    typ: str = SlashOption(
        name="type",
        description="The social the user is on",
        choices={
            "Twitch": "twitch",
            "Tiktok": "tiktok",
            "Twitter": "twitter",
            "Youtube": "youtube",
            "Kick": "kick",
        },
        required=True,
    ),
    channel: nextcord.TextChannel = nextcord.SlashOption(
        name="channel",
        description="The channel to send notifications to.",
        required=True,
    ),
):
    perms = interaction.user.guild_permissions
    if not perms.administrator:
        return await interaction.response.send_message(
            "You don't have permission to use this. Missing Permission: Administrator",
            ephemeral=True,
        )

    existing_data = (
        supabase.table("data")
        .select("*")
        .eq("type", typ)
        .eq("username", user)
        .eq("channel", channel.id)
        .execute()
    )

    if existing_data.data:
        return await interaction.response.send_message(
            f"A notification for {user} on {typ} is already configured for {channel.mention}.",
            ephemeral=True,
        )

    try:
        response = (
            supabase.table("data")
            .insert(
                {
                    "type": typ,
                    "created_by": interaction.user.id,
                    "username": user,
                    "channel": channel.id,
                }
            )
            .execute()
        )

        await interaction.response.send_message(
            f"Successfully added notifications for {user} on {typ} to {channel.mention}!",
            ephemeral=True,
        )

    except Exception as e:
        await interaction.response.send_message(
            f"An error occurred while adding the notification: {e}",
            ephemeral=True,
        )


@bot.slash_command(
    name="remove-ping",
    description="Remove a ping configuration from a channel [ADMIN ONLY]",
)
async def remove_ping(
    interaction: Interaction,
    user: str = SlashOption(
        name="user",
        description="The user to remove from notifications (autocomplete).",
        autocomplete=True,
        required=True,
    ),
    channel: nextcord.TextChannel = SlashOption(
        name="channel",
        description="The channel to remove notifications from.",
        required=True,
    ),
):
    perms = interaction.user.guild_permissions
    if not perms.administrator:
        return await interaction.response.send_message(
            "You don't have permission to use this. Missing Permission: Administrator",
            ephemeral=True,
        )

    try:
        response = (
            supabase.table("data")
            .delete()
            .eq("channel", channel.id)
            .eq("username", user)
            .execute()
        )

        if response.data:
            await interaction.response.send_message(
                f"Successfully removed notifications for {user} from {channel.mention}!",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"No notification found for {user} in {channel.mention}.",
                ephemeral=True,
            )

    except Exception as e:
        await interaction.response.send_message(
            f"An error occurred while removing the notification: {e}",
            ephemeral=True,
        )


@remove_ping.on_autocomplete("user")
async def remove_ping_autocomplete(
    interaction: Interaction, user: str, channel: nextcord.TextChannel = None
):
    if not channel:
        return await interaction.response.send_autocomplete([])

    try:
        channel_id = channel.id if isinstance(channel, nextcord.TextChannel) else None

        if not channel_id:
            return await interaction.response.send_autocomplete([])

        query = (
            supabase.table("data")
            .select("username")
            .eq("channel", channel_id)
        )
        if user:
            query = query.ilike("username", f"%{user}%")
        result = query.execute()

        usernames = [item["username"] for item in result.data]
        unique_usernames = list(dict.fromkeys(usernames))

        await interaction.response.send_autocomplete(unique_usernames[:25])
    except Exception as e:
        print(f"Autocomplete error: {e}")
        await interaction.response.send_autocomplete([])


bot.run(BOT_TOKEN)

