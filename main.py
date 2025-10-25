import discord
from discord.ext import commands
from discord.ui import Button, View
import os

# ---- CONFIG ----
TOKEN = os.getenv("TOKEN")  # ✅ Read token from Render environment
GUILD_ID = 1353061334530396211
REPORT_CHANNEL_ID = 1431488597592117268  # Where the "Create Report" message will appear
CATEGORY_ID = 1431487885453819995        # Category for private report channels
STAFF_ROLE_ID = 1353804677195628574

# ---- BOT SETUP ----
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ---- BUTTON VIEW ----
class ReportButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Report", style=discord.ButtonStyle.danger, emoji="🚨")
    async def create_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        staff_role = guild.get_role(STAFF_ROLE_ID)
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)

        # Count existing reports in the category
        existing_reports = [c for c in category.channels if c.name.startswith("report-")]
        report_number = len(existing_reports) + 1
        channel_name = f"report-{report_number:03d}"

        # Create the private report channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            staff_role: discord.PermissionOverwrite(view_channel=True),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
        }

        new_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Report created by {interaction.user}"
        )

        await interaction.response.send_message(
            f"✅ Report channel created: {new_channel.mention}", ephemeral=True
        )

        await new_channel.send(
            f"🚨 New report created by {interaction.user.mention}.\n"
            f"Staff will assist you shortly."
        )


# ---- SEND INITIAL BUTTON MESSAGE ----
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(REPORT_CHANNEL_ID)

    embed = discord.Embed(
        title="📢 Report an Issue",
        description="Click below to create a private report channel.\n"
                    "Staff will assist you shortly.",
        color=discord.Color.red()
    )

    view = ReportButton()
    await channel.send(embed=embed, view=view)
    print("📨 Report button sent.")


# ---- RUN BOT ----
bot.run(TOKEN)
