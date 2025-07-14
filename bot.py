import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === KONFIGURACJA ===
GUILD_ID = 1324179274273652867  # <--- ID twojego serwera
CHAN_LEGITYMOWANIE = 1324428098200142035  # <--- ID kanału #legitymowanie
CHAN_ZGLOSZENIA = 1324880217621139507     # <--- ID kanału #zgloszenia
CHAN_INTERWENCJE = 1324870507044274318     # <--- ID kanału #interwencje
CHAN_STATUSY = 1324872383970021398        # <--- ID kanału #statusy-patrolu
CHAN_997 = 1340366184083886080  # ID kanału z informacjami o decyzjach

@bot.event
async def on_ready():
    print(f"Zalogowano jako: {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Zsynchronizowano {len(synced)} komend.")
    except Exception as e:
        print(e)

from discord import app_commands
import discord

# === KOMENDA /997 ===
GUILD_ID = 1324179274273652867  # podmień na swoje ID serwera
CHAN_ZGLOSZENIA = 1324880217621139507  # podmień na ID kanału zgłoszeń
CHAN_INFO_997 = 1340366184083886080  # <-- tutaj wstaw ID kanału 997, gdzie chcesz wysyłać info o zaakceptowaniu/odrzuceniu

class PowodModal(discord.ui.Modal, title="Podaj powód odrzucenia"):
    powod = discord.ui.TextInput(label="Powód", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        kanal_info = interaction.guild.get_channel(CHAN_INFO_997)
        kanal_zgloszenia = interaction.guild.get_channel(CHAN_ZGLOSZENIA)

        embed = discord.Embed(
            title="❌ Zgłoszenie odrzucone",
            description=f"Zgłoszenie zostało odrzucone przez {interaction.user.mention}.",
            color=discord.Color.red()
        )
        embed.add_field(name="Powód odrzucenia:", value=self.powod.value, inline=False)

        await kanal_info.send(embed=embed)
        await kanal_zgloszenia.send(embed=embed)
        await interaction.response.send_message("Odrzuciłeś zgłoszenie.", ephemeral=True)

class ZgloszenieView(discord.ui.View):
    def __init__(self, embed):
        super().__init__(timeout=None)
        self.embed = embed

    @discord.ui.button(label="Zaakceptuj", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        kanal_info = interaction.guild.get_channel(CHAN_INFO_997)
        kanal_zgloszenia = interaction.guild.get_channel(CHAN_ZGLOSZENIA)

        embed = discord.Embed(
            title="✅ Zgłoszenie zaakceptowane",
            description=f"Zgłoszenie zostało zaakceptowane przez {interaction.user.mention}.\n\nProszę czekać na przyjazd patrolu policji.",
            color=discord.Color.green()
        )

        await kanal_info.send(embed=embed)
        await kanal_zgloszenia.send(embed=embed)
        await interaction.response.send_message("Zaakceptowałeś zgłoszenie.", ephemeral=True)

    @discord.ui.button(label="Odrzuć", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PowodModal()
        await interaction.response.send_modal(modal)

@bot.tree.command(name="997", description="Zgłoszenie", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    imie_nazwisko="Podaj swoje Imię i Nazwisko do zgłoszenia. Jeśli chcesz pozostać anonimowy wpisz Anonimowe zgłoszenie.",
    co_sie_stalo="Opisz szczegółowo co się stało.",
    lokalizacja="Podaj adres zgłoszenia lub dobrze opisany punkt dzięki któremu patrol trafi na miejsce.",
    osoby_poszkodowane="Czy są osoby poszkodowane? TAK/NIE"
)
async def zgloszenie(interaction: discord.Interaction, imie_nazwisko: str, co_sie_stalo: str, lokalizacja: str, osoby_poszkodowane: str):
    kanal = bot.get_channel(CHAN_ZGLOSZENIA)
    embed = discord.Embed(title="📢 Nowe Zgłoszenie", color=discord.Color.red())
    embed.add_field(name="Imię i nazwisko", value=imie_nazwisko, inline=False)
    embed.add_field(name="Co się stało", value=co_sie_stalo, inline=False)
    embed.add_field(name="Lokalizacja", value=lokalizacja, inline=False)
    embed.add_field(name="Osoby poszkodowane", value=osoby_poszkodowane, inline=False)
    embed.set_footer(text=f"Zgłoszone przez: {interaction.user}")

    view = ZgloszenieView(embed)
    await kanal.send(embed=embed, view=view)

    # Wiadomość dla użytkownika w niebieskiej ramce, widoczna dla wszystkich
    wyslane_embed = discord.Embed(
        title="Zgłoszenie zostało wysłane❗",
        description="Twoje zgłoszenie zostało pomyślnie wysłane.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=wyslane_embed, ephemeral=False)

# === KOMENDA /status ===
@bot.tree.command(name="status", description="Zmień status patrolu", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    status="Podaj nowy status (np. Patroluje, Interwencja)"
)
async def status(interaction: discord.Interaction, status: str):
    kanal = bot.get_channel(CHAN_STATUSY)
    embed = discord.Embed(title="🚓 Status Patrolu", color=discord.Color.blue())
    embed.add_field(name="Status", value=status, inline=False)
    embed.set_footer(text=f"Zgłoszone przez: {interaction.user}")
    await kanal.send(embed=embed)
    await interaction.response.send_message("Status zmieniony!", ephemeral=True)

# === KOMENDA /legitymuj ===
@bot.tree.command(name="legitymuj", description="Nowe legitymowanie", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    imie_nazwisko="Imię i nazwisko osoby",
    data_urodzenia="Data urodzenia (dd.mm.rrrr)",
    adres_zamieszkania="Dokładny adres zamieszkania osoby legitymowanej",
    powod_legitymowania="Powód legitymowania",
    miejsce_legitymowania="Dkładną ulice gdzie dokonano legitymowania",
    dokument="Rodzaj dokumentu (Dowód, Prawo Jazdy, Legitymacja, Paszport, Legitymowanie ręczne)"
)
async def legitymowanie(interaction: discord.Interaction, imie_nazwisko: str, data_urodzenia: str, adres_zamieszkania: str, powod_legitymowania: str, miejsce_legitymowania: str, dokument: str):
    kanal = bot.get_channel(CHAN_LEGITYMOWANIE)
    embed = discord.Embed(title="🪪 Nowe Legitymowanie", color=discord.Color.blue())
    embed.add_field(name="Imię i nazwisko", value=imie_nazwisko, inline=False)
    embed.add_field(name="Data urodzenia", value=data_urodzenia, inline=True)
    embed.add_field(name="Adres zamieszkania", value=adres_zamieszkania, inline=False)
    embed.add_field(name="Powód legitymowania", value=powod_legitymowania, inline=False)
    embed.add_field(name="Miejsce legitymowania", value=miejsce_legitymowania, inline=False)
    embed.add_field(name="Dokument", value=dokument, inline=False)
    embed.set_footer(text=f"Funkcjonariusz: {interaction.user.display_name}")
    await kanal.send(embed=embed)
    await interaction.response.send_message("Legitymowanie zapisane!", ephemeral=True)

# === KOMENDA /interwencja_własna ===
@bot.tree.command(name="interwencja_własna", description="Dodaj interwencję własną", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    miejsce_interwencji="Adres interwencji",
    powod_interwencji="Powód dla którego została podjęta interwencja",
    interwencja_dotyczy="Wymień osoby legitymowane wobec których została podjęta interwencja",
    dzialania_podjete="Opisz działania podjęte na miejscu np. Wylegiymowanie, aresztowanie, przeszukanie itp.",
    osoby_poszkodowane="Czy są osoby poszkodowane jeśli TAK podaj imie i nazwisko",
    notatka_z_interwencji="Napisz krótką notatke z interwencji - opisz ją dokładnie"
)
async def interwencja_wlasna(interaction: discord.Interaction, miejsce_interwencji: str, powod_interwencji: str, interwencja_dotyczy: str, dzialania_podjete: str, osoby_poszkodowane: str, notatka_z_interwencji: str):
    kanal = bot.get_channel(CHAN_INTERWENCJE)
    embed = discord.Embed(title="🚓 Interwencja Własna", color=discord.Color.blue())
    embed.add_field(name="Miejsce interwencji", value=miejsce_interwencji, inline=False)
    embed.add_field(name="Powód interwencji", value=powod_interwencji, inline=False)
    embed.add_field(name="Interwencja dotyczy", value=interwencja_dotyczy, inline=False)
    embed.add_field(name="Działania podjęte", value=dzialania_podjete, inline=False)
    embed.add_field(name="Osoby poszkodowane", value=osoby_poszkodowane, inline=False)
    embed.add_field(name="Notatka", value=notatka_z_interwencji, inline=False)
    embed.set_footer(text=f"Funkcjonariusz: {interaction.user.display_name}")
    await kanal.send(embed=embed)
    await interaction.response.send_message("Interwencja własna zgłoszona!", ephemeral=True)

# === KOMENDA /interwencja_zlecona ===
@bot.tree.command(name="interwencja_zlecona", description="Zgłoś interwencję zleconą", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    opis="Opis interwencji",
    miejsce="Miejsce interwencji"
)
async def interwencja_zlecona(interaction: discord.Interaction, opis: str, miejsce: str):
    kanal = bot.get_channel(CHAN_INTERWENCJE)
    embed = discord.Embed(title="📨 Interwencja Zlecona", color=discord.Color.purple())
    embed.add_field(name="Opis", value=opis, inline=False)
    embed.add_field(name="Miejsce", value=miejsce, inline=False)
    embed.set_footer(text=f"Funkcjonariusz: {interaction.user}")
    await kanal.send(embed=embed)
    await interaction.response.send_message("Interwencja zlecona zgłoszona!", ephemeral=True)

# === URUCHOMIENIE BOTA ===
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
