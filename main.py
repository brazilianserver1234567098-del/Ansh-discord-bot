import os 
import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# 1. Role Buttons View
class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def toggle_role(self, interaction: discord.Interaction, role_name: str):
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name=role_name)

        if not role:
            await interaction.response.send_message(f"⚠️ Server me '{role_name}' role nahi mila!", ephemeral=True)
            return

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"❌ Role hata diya: **{role_name}**", ephemeral=True)
        else:
            try:
                await member.add_roles(role)
                await interaction.response.send_message(f"✅ Role mil gaya: **{role_name}**", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)

    @discord.ui.button(label="🔞 18+", style=discord.ButtonStyle.primary, custom_id="role_18_plus")
    async def btn_18_plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "18+")

    @discord.ui.button(label="👶 -18", style=discord.ButtonStyle.primary, custom_id="role_under_18")
    async def btn_under_18(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "-18")

    @discord.ui.button(label="💻 PC Player", style=discord.ButtonStyle.success, custom_id="role_pc")
    async def btn_pc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "PC Player")

    @discord.ui.button(label="📱 Mobile Player", style=discord.ButtonStyle.success, custom_id="role_mobile")
    async def btn_mobile(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "Mobile Player")

# 2. Ban Buttons View (Owner DM)
class BanDecisionView(discord.ui.View):
    def __init__(self, target_member: discord.Member, reason: str, guild: discord.Guild):
        super().__init__(timeout=86400)
        self.target_member = target_member
        self.reason = reason
        self.guild = guild

    @discord.ui.button(label="🔨 Ban Player", style=discord.ButtonStyle.danger)
    async def confirm_ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.guild.owner:
            await interaction.response.send_message("❌ Sirf Owner ban kar sakta hai!", ephemeral=True)
            return
        try:
            await self.guild.ban(self.target_member, reason=f"Report: {self.reason}")
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content=f"✅ {self.target_member.name} ban ho gaya!", view=self)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)

    @discord.ui.button(label="❌ Ignore", style=discord.ButtonStyle.secondary)
    async def cancel_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.guild.owner:
            await interaction.response.send_message("❌ Sirf Owner ke liye!", ephemeral=True)
            return
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="🚫 Report ignore kar di gayi.", view=self)

@bot.event
async def on_ready():
    bot.add_view(RoleSelectView())
    print(f"Logged in as: {bot.user.name}")
    print("Bot 24/7 Cloud Worker Online!")

# 3. FAQ Listener
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content.lower().strip()
    if msg in ["rules", "!rules", "rule kya h"]:
        await message.channel.send("📜 **Server Rules:** No spamming, respect all members, keep chat friendly!")
    elif msg in ["owner", "owner kaun h", "who is owner"]:
        await message.channel.send(f"👑 Server owner **{message.guild.owner.name}** hain!")
    elif msg in ["ip", "ip kya h", "server ip"]:
        await message.channel.send("📌 **Server IP:** `play.mysmp.net` | Port: `25565`")

    await bot.process_commands(message)

# 4. Commands
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms ⚡ (Cloud 24/7)")

@bot.command()
async def setup_roles(ctx):
    embed = discord.Embed(
        title="🎭 Select Your Roles",
        description="Niche diye buttons par tap karke role lo ya hatao:\n\n"
                    "• **Age:** 🔞 18+  ya  👶 -18\n"
                    "• **Device:** 💻 PC Player  ya  📱 Mobile Player",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=RoleSelectView())

@bot.command()
async def report(ctx, member: discord.Member = None, *, reason: str = None):
    if not member or not reason:
        await ctx.send("⚠️ Sahi format: `!report @username <reason>`")
        return

    owner = ctx.guild.owner
    embed = discord.Embed(title="🚨 NEW REPORT 🚨", color=discord.Color.red())
    embed.add_field(name="Target Player", value=f"{member.mention} ({member.name})", inline=False)
    embed.add_field(name="Reported By", value=f"{ctx.author.mention}", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)

    try:
        view = BanDecisionView(target_member=member, reason=reason, guild=ctx.guild)
        await owner.send(embed=embed, view=view)
        await ctx.send(f"✅ Report owner ({owner.name}) ke DM me bhej di gayi hai!")
    except Exception as e:
        await ctx.send(f"⚠️ DM fail: {e}")

bot.run(os.environ.get("DISCORD_TOKEN"))
