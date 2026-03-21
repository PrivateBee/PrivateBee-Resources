import os
import asyncio
import datetime
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

## Config
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID_ENV = os.getenv('SERVER_ID')

# Information about the discord
COMMAND_CHANNEL_ID = os.getenv('COMMAND_CHANNEL_ID')
COMMAND_CHANNEL_ID = int(COMMAND_CHANNEL_ID) if COMMAND_CHANNEL_ID else None

if SERVER_ID_ENV is None:
    print("Erreur : SERVER_ID ou ID_SERVEUR manquant dans le .env")
    exit(1)

SERVER_ID = int(SERVER_ID_ENV)
PREFIX = "!"

current_auto_role_name = None 

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

def get_annual_role_name(year_offset=0):
    """Génère le nom du rôle annuel (ex: Année 2026)."""
    target_year = datetime.datetime.now().year + year_offset
    return f"Année {target_year}"


async def run_annual_cycle(guild):
    """Logique pour s'assurer de l'année N et nettoyer N-2 ou plus vieux."""
    current_year = datetime.datetime.now().year
    
    # Check if the role already exist
    target_name = f"Année {current_year}"
    existing_role = discord.utils.get(guild.roles, name=target_name)
    if not existing_role:
        try:
            await guild.create_role(name=target_name, mentionable=True, colour=discord.Color.blue())
        except Exception as e:
            print(f"Erreur création rôle N : {e}")

    # Clean old roles
    total_kicks = 0
    roles_deleted = []
    
    for role in list(guild.roles):
        if role.name.startswith("Année "):
            try:
                role_year = int(role.name.split(" ")[1])
                if role_year <= (current_year - 2):
                    async for member in guild.fetch_members(limit=None):
                        if role in member.roles and member != bot.user:
                            try:
                                await member.kick(reason=f"Cycle annuel : Nettoyage {role.name}")
                                total_kicks += 1
                                await asyncio.sleep(0.1)
                            except: continue
                    await role.delete()
                    roles_deleted.append(role.name)
            except: continue
                
    return total_kicks, roles_deleted


@bot.event
async def on_ready():
    status_text = f"{PREFIX}botHelp | {get_annual_role_name()}"
    await bot.change_presence(activity=discord.Game(name=status_text))
    print(f'--- Bot connecté : {bot.user.name} ---')

@bot.check
async def globally_restrict_channels(ctx):
    """Restriction globale : les commandes ne marchent que dans le salon spécifié."""
    if COMMAND_CHANNEL_ID is None:
        return True # If no ID configured work evrywhere
    
    if ctx.channel.id != COMMAND_CHANNEL_ID:
        return False
    return True

@bot.event
async def on_member_join(member):
    if member.guild.id != SERVER_ID:
        return
    role_to_find = current_auto_role_name or get_annual_role_name()
    role = discord.utils.get(member.guild.roles, name=role_to_find)
    if role:
        try: await member.add_roles(role)
        except: pass


@tasks.loop(hours=24)
async def check_date_and_create_role():
    now = datetime.datetime.now()
    if now.day == 1 and now.month == 1:
        guild = bot.get_guild(SERVER_ID)
        if guild:
            # Log into the chanel
            kicks, deleted = await run_annual_cycle(guild)
            channel = bot.get_channel(COMMAND_CHANNEL_ID)
            if channel and (kicks > 0 or deleted):
                await channel.send(f"ߓ堪*Rapport du 1er Janvier** : {kicks} membres expulsés. Rôles supprimés : {', '.join(deleted)}")


@bot.command(name='forceCycle')
@commands.has_permissions(administrator=True)
async def force_cycle(ctx):
    await ctx.send("ߚࠌancement du cycle (Vérification N / Nettoyage <= N-2)...")
    kicks, deleted = await run_annual_cycle(ctx.guild)
    
    msg = f"✅ Terminé.\n- Membres expulsés : {kicks}"
    if deleted: msg += f"\n- Rôles supprimés : {', '.join(deleted)}"
    await ctx.send(msg)

@bot.command(name='setRole')
@commands.has_permissions(manage_roles=True)
async def set_role(ctx, *, role_input: str):
    global current_auto_role_name
    clean_name = role_input.replace('<@&', '').replace('>', '')
    role = ctx.guild.get_role(int(clean_name)) if clean_name.isdigit() else discord.utils.get(ctx.guild.roles, name=role_input)

    if role is None:
        role = await ctx.guild.create_role(name=role_input, mentionable=True, colour=discord.Colour.green())
    
    current_auto_role_name = role.name
    await ctx.send(f"✅ Rôle automatique défini sur : **{role.name}**")

@bot.command(name='kickrole')
@commands.has_permissions(kick_members=True, manage_roles=True)
async def kick_role_command(ctx, target_role: discord.Role):
    await ctx.send(f"⚠️ Nettoyage manuel de {target_role.name}...")
    count = 0
    async for member in ctx.guild.fetch_members(limit=None):
        if target_role in member.roles and member != bot.user and member != ctx.author:
            try:
                await member.kick(reason=f"Manuel : {target_role.name}")
                count += 1
            except: continue
    await target_role.delete()
    await ctx.send(f"✅ {count} membres expulsés et rôle supprimé.")

@bot.command(name='botHelp')
async def bot_help(ctx):
    help_text = (
        "**ߓꠇuide des commandes (Salon unique) :**\n"
        f"- `{PREFIX}setRole Nom`: Définit le rôle auto.\n"
        f"- `{PREFIX}kickrole @Role`: Nettoyage manuel.\n"
        f"- `{PREFIX}forceCycle`: Lance le cycle annuel.\n"
        f"**Rôle actuel :** `{current_auto_role_name or get_annual_role_name()}`"
    )
    await ctx.send(help_text)

if __name__ == "__main__":
    bot.run(TOKEN)