import discord
from discord.ext import commands
import datetime



# Configurações Iniciais
TOKEN = 'TOKENAQ'
PREFIX = '$'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Dicionário simples para salvar configurações
autorole_config = {
    "active": False,
    "user_role": None,
    "bot_role": None
}

@bot.event
async def on_ready():
    print(f'✅ Zux Store conectada como {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Zux Store | $help"))

# --- COMANDO HELP ---
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def help(ctx):
    embed = discord.Embed(
        title="📚 Painel de Comandos - Zux Store",
        description=f"Olá {ctx.author.mention}, aqui estão meus comandos disponíveis!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🛡️ Moderação",
        value=(
            "`$kick @user` - Expulsa um membro\n"
            "`$ban @user` - Bane um membro\n"
            "`$unban ID` - Desbane via ID\n"
            "`$mute @user tempo` - Silencia o membro\n"
            "`$unmute @user` - Remove o silêncio"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Configuração",
        value="`$autorole` - Abre o painel de configuração de cargos automáticos",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Utilidades",
        value=(
            "`$userinfo @user` - Informações de um usuário\n"
            "`$avatar @user` - Mostra a foto de perfil\n"
            "`$banner @user` - Mostra o banner do perfil"
        ),
        inline=False
    )
    
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text="Zux Store - Todos os direitos reservados.")
    await ctx.send(embed=embed)

# --- COMANDOS DE UTILIDADE ---

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.mention for role in member.roles[1:]] # Remove o @everyone
    
    embed = discord.Embed(title=f"Informações de {member.name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID:", value=member.id, inline=True)
    embed.add_field(name="Nickname:", value=member.nick or "Nenhum", inline=True)
    embed.add_field(name="Conta Criada:", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Entrou na Loja:", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name=f"Cargos ({len(roles)}):", value=" ".join(roles) if roles else "Nenhum", inline=False)
    embed.set_footer(text=f"Solicitado por {ctx.author}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ Avatar de {member.name}", color=discord.Color.random())
    embed.set_image(url=member.display_avatar.with_size(1024).url)
    await ctx.send(embed=embed)

@bot.command()
async def banner(ctx, member: discord.Member = None):
    member = member or ctx.author
    # É necessário buscar o usuário completo para ver o banner
    user = await bot.fetch_user(member.id)
    
    if not user.banner:
        return await ctx.send(f"❌ {member.mention} não possui um banner.")
    
    embed = discord.Embed(title=f"🖼️ Banner de {member.name}", color=discord.Color.random())
    embed.set_image(url=user.banner.with_size(1024).url)
    await ctx.send(embed=embed)

# --- COMANDOS DE MODERAÇÃO ---

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Não informado"):
    await member.kick(reason=reason)
    await ctx.send(f"✅ {member.mention} foi expulso da Zux Store.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Não informado"):
    await member.ban(reason=reason)
    await ctx.send(f"❌ {member.mention} foi banido permanentemente.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, id: int):
    user = await bot.fetch_user(id)
    await ctx.guild.unban(user)
    await ctx.send(f"🔓 O usuário {user.name} foi desbanido.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, tempo: int = 60, *, reason="Não informado"):
    duration = datetime.timedelta(minutes=tempo)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"🔇 {member.mention} foi silenciado por {tempo} minutos.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 O silenciamento de {member.mention} foi removido.")

# --- SISTEMA DE AUTO-ROLE ---

class AutoRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ativar/Desativar", style=discord.ButtonStyle.primary)
    async def toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
        autorole_config["active"] = not autorole_config["active"]
        status = "✅ Ativado" if autorole_config["active"] else "❌ Desativado"
        await interaction.response.send_message(f"Auto-role agora está: **{status}**", ephemeral=True)

    @discord.ui.button(label="Cargo Membro", style=discord.ButtonStyle.secondary)
    async def set_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Mencione o cargo para **Membros** agora:", ephemeral=True)
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await bot.wait_for("message", check=check)
        if msg.role_mentions:
            autorole_config["user_role"] = msg.role_mentions[0].id
            await interaction.followup.send(f"Cargo de Membro definido!", ephemeral=True)

    @discord.ui.button(label="Cargo Bot", style=discord.ButtonStyle.secondary)
    async def set_bot(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Mencione o cargo para **Bots** agora:", ephemeral=True)
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await bot.wait_for("message", check=check)
        if msg.role_mentions:
            autorole_config["bot_role"] = msg.role_mentions[0].id
            await interaction.followup.send(f"Cargo de Bot definido!", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def autorole(ctx):
    embed = discord.Embed(
        title="⚙️ Configuração Auto-role | Zux Store",
        description="Clique nos botões abaixo para configurar a entrada automática.",
        color=discord.Color.dark_purple()
    )
    await ctx.send(embed=embed, view=AutoRoleView())

@bot.event
async def on_member_join(member):
    if not autorole_config["active"]: return
    
    role_id = autorole_config["bot_role"] if member.bot else autorole_config["user_role"]
    if role_id:
        role = member.guild.get_role(role_id)
        if role: await member.add_roles(role)

# Tratamento de Erros
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏱️ Aguarde {error.retry_after:.2f}s para usar este comando novamente.")

bot.run(TOKEN)
