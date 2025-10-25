import discord
from discord.ext import commands
from discord.ui import Button, View
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1353061334530396211
REPORT_CHANNEL_ID = 1431488597592117268
CATEGORY_ID = 1431487885453819995
STAFF_ROLE_ID = 1353804677195628574
HEX_COLOR = 0xBD73DE

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class CloseButton(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket closed. Deleting channel...", ephemeral=True)
        await self.channel.delete()

class TicketButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Report a Player", style=discord.ButtonStyle.secondary)
    async def player_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "player-report", "Player Report")

    @discord.ui.button(label="Report a Bug", style=discord.ButtonStyle.secondary)
    async def bug_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "bug-report", "Bug Report")

    async def create_ticket(self, interaction, prefix, title_name):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)
        existing = [c for c in category.channels if c.name.startswith(prefix)]
        ticket_number = len(existing) + 1
        channel_name = f"{prefix}-{ticket_number:03d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            staff_role: discord.PermissionOverwrite(view_channel=True),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"{title_name} created by {interaction.user}"
        )

        embed = discord.Embed(
            title=f"New {title_name} Created by {interaction.user.display_name}",
            description=(
                f"{staff_role.mention}\n\n"
                "Please describe the situation clearly and wait for a staff member to review and assist you. "
                "Note that responses may take some time, as staff are managing multiple tickets."
            ),
            color=HEX_COLOR
        )

        close_view = CloseButton(channel)
        await channel.send(embed=embed, view=close_view)
        await interaction.response.send_message(f"✅ {title_name} channel created: {channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(REPORT_CHANNEL_ID)

    embed = discord.Embed(
        title="Submit a Player or Bug Report",
        description=(
            "Please use the two buttons below to report a player or a bug. This ensures your concern is properly directed and handled by the team.\n\n"
            "Avoid submitting off-topic requests, such as asking to become staff or requesting free items. Off-topic tickets may be ignored to keep the system efficient.\n\n"
            "Be aware that ticket responses may take time, as staff manage reports alongside their other responsibilities. Your patience is appreciated while we review and resolve issues."
        ),
        color=HEX_COLOR
    )

    view = TicketButtonView()
    await channel.send(embed=embed, view=view)
    print("📨 Ticket buttons sent.")

bot.run(TOKEN)
