import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from invite_users import inviter_utilisateur
from github_error_codes import GithubInviteCode

# Load variable from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_GITHUB')
SERVER_ID_ENV = os.getenv('SERVER_ID')
COMMAND_CHANNEL_ID_ENV = os.getenv('COMMAND_CHANNEL_ID')
COMMAND_CHANNEL_ID_TEST_ENV = os.getenv('COMMAND_CHANNEL_ID_TEST')

if SERVER_ID_ENV is None:
    print("Erreur : SERVER_ID manquant dans le .env")
    exit(1)
if COMMAND_CHANNEL_ID_ENV is None:
    print("Erreur : COMMAND_CHANNEL_ID manquant dans le .env")
    exit(1)

SERVER_ID = int(SERVER_ID_ENV)
COMMAND_CHANNEL_ID = int(COMMAND_CHANNEL_ID_ENV)
COMMAND_CHANNEL_ID_TEST = int(COMMAND_CHANNEL_ID_TEST_ENV)

INTENTS = discord.Intents.default()
INTENTS.message_content = True

PREFIX = "$"

bot = commands.Bot(command_prefix=PREFIX, intents=INTENTS)

# Command to invit a person on github 
@bot.tree.command(
    guild=discord.Object(id=SERVER_ID),
    description="Ajoute un utilisateur a GitHub a partir de son pseudo"
)
@app_commands.describe(username="Pseudo GitHub de l'utilisateur a ajouter")
async def ajouter_utilisateur_github(interaction: discord.Interaction, username: str):
    # Checl if the command is in the right chanel
    if(interaction.channel_id != COMMAND_CHANNEL_ID and interaction.channel_id != COMMAND_CHANNEL_ID_TEST):
        await interaction.response.send_message(
            f"Cette commande ne peut etre utilisee que dans <#{COMMAND_CHANNEL_ID}>.",
            ephemeral=True,
        )
        return

    code = inviter_utilisateur(username=username)

    # Send a response indicating whether the operation was successful or not 
    if code == GithubInviteCode.OK:
        await interaction.response.send_message(
            f"Invitation envoyee pour `{username}`.",
        )
    elif code == GithubInviteCode.CONFIG_MISSING_TOKEN:
        await interaction.response.send_message(
            "Configuration invalide: GITHUB_TOKEN manquant.",
            ephemeral=True,
        )
    elif code == GithubInviteCode.USER_NOT_FOUND:
        await interaction.response.send_message(
            f"Utilisateur GitHub introuvable: `{username}`.",
            ephemeral=True,
        )
    elif code == GithubInviteCode.USER_ALREADY_MEMBER:
        await interaction.response.send_message(
            f"`{username}` est deja membre de l'organisation.",
            ephemeral=True,
        )
    elif code == GithubInviteCode.USER_ALREADY_INVITED:
        await interaction.response.send_message(
            f"`{username}` a deja une invitation en attente.",
            ephemeral=True,
        )
    elif code == GithubInviteCode.GITHUB_API_ERROR:
        await interaction.response.send_message(
            "Erreur API GitHub. Reessaie plus tard.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Erreur inconnue pendant l'invitation.",
            ephemeral=True,
        )

# Sart bot
@bot.event
async def on_ready():
    print(f"--- Démarrage de {bot.user} ---")
    try:
        status_text = "/ajouter_utilisateur_github"
        await bot.change_presence(activity=discord.Game(name=status_text))

        guild = discord.Object(id=SERVER_ID)
        sync = await bot.tree.sync(guild=guild)
        print(f"{len(sync)} commande(s) synchronisée(s)")
    except Exception as e:
        print(e)
    print(f'--- {bot.user} connecté ---')

bot.run(token=TOKEN)