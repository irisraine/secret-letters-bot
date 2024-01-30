import nextcord
from nextcord import Interaction
from nextcord.ext import commands, tasks
from dotenv import load_dotenv
import logging
import datetime
import os
import engine.sql as sql
import engine.config as config
import engine.messages as messages
from engine.utils import image_download
from engine.messages import Letter

load_dotenv()
intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

launch_time = datetime.time(
    hour=config.SENDING_TARGET_TIME['hour'],
    minute=config.SENDING_TARGET_TIME['minute']
)
current_date = datetime.date.today()
launch_date = datetime.date(
    day=config.SENDING_TARGET_DATE['day'],
    month=config.SENDING_TARGET_DATE['month'],
    year=config.SENDING_TARGET_DATE['year']
)


class LetterForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Тайное признание в теплых чувствах!")

        self.recipient_username = nextcord.ui.TextInput(
            label="Адресат",
            min_length=3,
            max_length=100,
            required=True,
            placeholder="Уникальное Discord-имя адресата",
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.recipient_username)
        self.sender_alias = nextcord.ui.TextInput(
            label="Мой псевдоним",
            max_length=100,
            required=False,
            placeholder="Тайный поклонник",
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.sender_alias)
        self.body_content = nextcord.ui.TextInput(
            label="Текст письма",
            max_length=4000,
            required=True,
            placeholder="Текст послания, полный кошачьего мурчания",
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.body_content)
        self.image_url = nextcord.ui.TextInput(
            label="Открытка",
            max_length=200,
            required=False,
            placeholder="URL поздравительной открытки",
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.image_url)

    async def callback(self, interaction: Interaction) -> None:
        recipient = nextcord.utils.get(interaction.guild.members, name=self.recipient_username.value)
        if not recipient:
            return await interaction.response.send_message(
                embed=messages.recipient_error.embed, ephemeral=True
            )
        elif sql.is_letter_scheduled_already(interaction.user.id, recipient.id):
            return await interaction.response.send_message(
                embed=messages.scheduled_already_error.embed, ephemeral=True
            )
        if self.image_url.value:
            image_attachment_path = image_download(self.image_url.value)
            if not image_attachment_path:
                return await interaction.response.send_message(
                    embed=messages.attached_image_error.embed, ephemeral=True
                )
        else:
            image_attachment_path = None
        if recipient.id == interaction.user.id:
            return await interaction.response.send_message(
                embed=messages.self_sending_error.embed, ephemeral=True
            )
        sql.add_letter_db_record(
            recipient_discord_id=recipient.id,
            recipient_username=recipient.name,
            recipient_globalname=recipient.global_name,
            sender_discord_id=interaction.user.id,
            sender_username=interaction.user.name,
            sender_alias=self.sender_alias.value,
            body_content=self.body_content.value,
            image_attachment_path=image_attachment_path
        )
        sql.increment_count(interaction.user.id)
        logging.info(f'Валентинка для {recipient.name} создана')
        return await interaction.response.send_message(embed=messages.scheduled_success.embed, ephemeral=True)


class ButtonMainMenu(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Тайно признаться", style=nextcord.ButtonStyle.blurple, emoji="💌")
    async def create_letter_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if current_date > launch_date:
            return await interaction.response.send_message(
                embed=messages.expired_event.embed, ephemeral=True
            )
        count_by_current_user = sql.get_count(interaction.user.id)
        if not count_by_current_user:
            sql.set_count(interaction.user.id)
        elif count_by_current_user[0] > 24:
            return await interaction.response.send_message(
                embed=messages.max_count_error.embed, ephemeral=True
            )
        await interaction.response.send_modal(LetterForm())

    @nextcord.ui.button(label="Список отправленных валентинок", style=nextcord.ButtonStyle.blurple, emoji="📋")
    async def list_of_my_letters_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        letters_by_user_db_records = sql.get_letters_by_user_db_records(interaction.user.id)
        options = []
        for letter_db_record in letters_by_user_db_records:
            record_id = letter_db_record[0]
            recipient_username = letter_db_record[2]
            letter_preview = letter_db_record[7] if len(letter_db_record[7]) < 50 else f"{letter_db_record[7][:45]}..."
            option = nextcord.SelectOption(
                label=f"Валентинка для {recipient_username}",
                value=record_id,
                description=letter_preview,
                emoji="💘"
            )
            options.append(option)
        if not options:
            return await interaction.response.send_message(
                embed=messages.empty_list_error.embed, ephemeral=True
            )
        await interaction.response.send_message(
            view=LettersList(options), ephemeral=True
        )


class LettersListDropdown(nextcord.ui.Select):
    def __init__(self, options):
        super().__init__(
            placeholder="Список отправленных валентинок",
            options=options
        )

    async def callback(self, interaction: Interaction) -> None:
        letter_db_record = sql.get_letter_db_record(self.values[0])
        letter_message = Letter(letter_db_record)
        await interaction.response.defer()
        await interaction.edit_original_message(
            embed=letter_message.embed,
            file=letter_message.image,
            view=ButtonDeleteLetter(letter_db_record[0])
        )


class LettersList(nextcord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.add_item(LettersListDropdown(options=options))


class ButtonDeleteLetter(nextcord.ui.View):
    def __init__(self, record_id):
        super().__init__(timeout=None)
        self.record_id = record_id

    @nextcord.ui.button(label="Удалить валентинку", style=nextcord.ButtonStyle.red, emoji="🔪")
    async def delete_letter_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        sql.delete_letter_db_record(self.record_id)
        sql.decrement_count(interaction.user.id)
        await interaction.response.defer()
        await interaction.edit_original_message(
            embed=messages.deletion.embed,
            attachments=[],
            view=None
        )


@client.event
async def on_ready():
    logging.info(f'Бот залогинен под именем: {client.user.name}')
    if not os.path.exists('database/postcards'):
        os.makedirs('database/postcards')
    sql.create_tables()
    send_letters.start()


@client.command()
async def start(ctx):
    await ctx.send(
        embed=messages.introduction.embed,
        file=messages.introduction.image
    )
    await ctx.send(
        embed=messages.instruction.embed,
        file=messages.instruction.image,
        view=ButtonMainMenu()
    )


@tasks.loop(time=launch_time)
async def send_letters():
    global current_date
    current_date = datetime.date.today()
    if current_date == launch_date:
        logging.info(f'Назначенный день настал, и рассылка начата!')
        letters_db_records = sql.get_letters_db_records()
        for letter_db_record in letters_db_records:
            recipient_discord_id = letter_db_record[1]
            recipient_username = letter_db_record[2]
            try:
                recipient = client.get_user(recipient_discord_id)
                letter_message = Letter(letter_db_record)
                await recipient.send(
                    embed=letter_message.embed,
                    file=letter_message.image
                )
                logging.info(f'Валентинка для {recipient_username} отправлена!')
            except nextcord.Forbidden:
                logging.error(f'Валентинка для {recipient_username} не отправлена, '
                              f'поскольку бот не имеет разрешений для отправки '
                              f'сообщений этому пользователю')
            except nextcord.HTTPException as e:
                logging.error(f'Валентинка для {recipient_username} не отправлена, '
                              f'произошла ошибка класса HTTPException. '
                              f'Дополнительная информация: {e}')
            except Exception as e:
                logging.error(f'Валентинка для {recipient_username} не отправлена, '
                              f'произошла неизвестная общая ошибка. '
                              f'Дополнительная информация: {e}')
