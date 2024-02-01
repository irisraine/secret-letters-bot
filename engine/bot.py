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
import engine.utils as utils
from engine.messages import Letter, MessageContainer

load_dotenv()
intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

event_settings = {}
launch_time = datetime.time(
    hour=config.SENDING_TARGET_TIME['hour'],
    minute=config.SENDING_TARGET_TIME['minute']
)
current_date = datetime.date.today()
sending_date = datetime.date(1970, 1, 1)
send_already_letters_count = 0


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
        await interaction.response.defer()
        recipient = nextcord.utils.get(interaction.guild.members, name=self.recipient_username.value)
        if not recipient:
            return await interaction.followup.send(
                embed=messages.recipient_error().embed, ephemeral=True
            )
        elif sql.is_letter_send_already(interaction.user.id, recipient.id):
            return await interaction.followup.send(
                embed=messages.send_already_error().embed, ephemeral=True
            )
        if recipient.id == interaction.user.id:
            return await interaction.followup.send(
                embed=messages.self_sending_error().embed, ephemeral=True
            )
        image_binary_data, image_filename = utils.image_download(self.image_url.value)
        if self.image_url.value and not image_binary_data:
            return await interaction.followup.send(
                embed=messages.attached_image_error().embed, ephemeral=True
            )
        sql.add_letter_db_record(
            recipient_discord_id=recipient.id,
            recipient_username=recipient.name,
            recipient_globalname=recipient.global_name,
            sender_discord_id=interaction.user.id,
            sender_username=interaction.user.name,
            sender_alias=self.sender_alias.value,
            body_content=self.body_content.value,
            image_binary_data=image_binary_data,
            image_filename=image_filename
        )
        sql.increment_count(interaction.user.id)
        logging.info(f'Письмо для {recipient.name} создано')
        return await interaction.followup.send(embed=messages.send_success().embed, ephemeral=True)


class MainMenuButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Тайно признаться", style=nextcord.ButtonStyle.blurple, emoji="💌")
    async def create_letter_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if current_date >= sending_date:
            return await interaction.response.send_message(
                embed=messages.expired_event().embed, ephemeral=True
            )
        count_by_current_user = sql.get_count(interaction.user.id)
        if not count_by_current_user:
            sql.set_count(interaction.user.id)
        elif count_by_current_user[0] > 24:
            return await interaction.response.send_message(
                embed=messages.max_count_error().embed, ephemeral=True
            )
        await interaction.response.send_modal(LetterForm())

    @nextcord.ui.button(label="Список отправленных писем", style=nextcord.ButtonStyle.blurple, emoji="📋")
    async def list_of_my_letters_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        letters_by_user_db_records = sql.get_letters_by_user_db_records(interaction.user.id)
        options = []
        for letter_db_record in letters_by_user_db_records:
            record_id = letter_db_record[0]
            recipient_username = letter_db_record[2]
            letter_preview = letter_db_record[7] if len(letter_db_record[7]) < 50 else f"{letter_db_record[7][:45]}..."
            option = nextcord.SelectOption(
                label=f"Письмо для {recipient_username}",
                value=record_id,
                description=letter_preview,
                emoji="💘"
            )
            options.append(option)
        if not options:
            return await interaction.response.send_message(
                embed=messages.empty_list_error().embed, ephemeral=True
            )
        await interaction.response.send_message(
            view=LettersList(options), ephemeral=True
        )


class LettersListDropdown(nextcord.ui.Select):
    def __init__(self, options):
        super().__init__(
            placeholder="Список отправленных писем",
            options=options
        )

    async def callback(self, interaction: Interaction) -> None:
        letter_db_record = sql.get_letter_db_record(self.values[0])
        if not letter_db_record:
            return await interaction.response.send_message(
                embed=messages.not_exist_error().embed, ephemeral=True
            )
        letter_message = Letter(letter_db_record)
        await interaction.response.defer()
        await interaction.edit_original_message(
            embed=letter_message.embed,
            file=letter_message.image,
            view=DeleteLetterButton(letter_db_record[0])
        )


class LettersList(nextcord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.add_item(LettersListDropdown(options=options))


class DeleteLetterButton(nextcord.ui.View):
    def __init__(self, record_id):
        super().__init__(timeout=None)
        self.record_id = record_id

    @nextcord.ui.button(label="Удалить письмо", style=nextcord.ButtonStyle.red, emoji="🔪")
    async def delete_letter_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        sql.delete_letter_db_record(self.record_id)
        sql.decrement_count(interaction.user.id)
        await interaction.response.defer()
        await interaction.edit_original_message(
            embed=messages.deletion().embed,
            attachments=[],
            view=None
        )


class NewEventCreationForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Создать новый ивент")

        self.event_name = nextcord.ui.TextInput(
            label="Название ивента",
            min_length=3,
            max_length=50,
            required=True,
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.event_name)
        self.event_description = nextcord.ui.TextInput(
            label="Текст приветственного сообщения",
            max_length=4000,
            required=True,
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.event_description)
        self.sending_date = nextcord.ui.TextInput(
            label="Дата отправки писем",
            required=True,
            placeholder="Дата в формате дд.мм.гггг",
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.sending_date)
        self.image_url = nextcord.ui.TextInput(
            label="URL изображения в приветственном сообщении",
            max_length=200,
            required=True,
            placeholder="В формате PNG или JPG",
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.image_url)

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        global event_settings
        new_sending_date = utils.get_parsed_date(self.sending_date.value)
        if not new_sending_date:
            return await interaction.followup.send(
                embed=messages.invalid_date_warning().embed, ephemeral=True
            )
        image_binary_data, _ = utils.image_download(self.image_url.value)
        if not image_binary_data:
            return await interaction.followup.send(
                embed=messages.attached_image_error().embed, ephemeral=True
            )
        event_settings = {
            "title": self.event_name.value,
            "description": self.event_description.value,
            "sending_date": new_sending_date
        }
        utils.save_event_settings(event_settings)
        utils.save_image_file(image_binary_data)
        apply_event_settings()
        global send_already_letters_count
        send_already_letters_count = 0
        return await interaction.followup.send(
            embed=messages.new_event_successful_created().embed, ephemeral=True
        )


class AdminMenuButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Новый ивент", style=nextcord.ButtonStyle.blurple, emoji="🪄")
    async def create_new_event_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(NewEventCreationForm())

    @nextcord.ui.button(label="Ручная рассылка", style=nextcord.ButtonStyle.blurple, emoji="📨")
    async def manual_send_letters_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        logging.info('Экстренная ручная рассылка писем начата')
        await interaction.followup.send(
            embed=messages.manual_sending_start().embed, ephemeral=True
        )
        await send_letters()

    @nextcord.ui.button(label="Статистика", style=nextcord.ButtonStyle.blurple, emoji="📈")
    async def stats_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        all_letters_count = sql.count_letters()
        stats = MessageContainer(
            title="Статистика",
            description=f"Общее количество писем, написанных участниками: **{all_letters_count}**\n"
                        f"Количество отправленных ботом писем: **{send_already_letters_count}**\n\n"
                        f"Дата отправки сообщений: {sending_date}"
        )
        await interaction.followup.send(
            embed=stats.embed, file=stats.image, ephemeral=True
        )

    @nextcord.ui.button(label="Стереть базу данных", style=nextcord.ButtonStyle.blurple, emoji="🔥")
    async def drop_database_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            embed=messages.database_deletion_warning().embed,
            file=messages.database_deletion_warning().image,
            view=DropDatabaseButton(),
            ephemeral=True
        )


class DropDatabaseButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Удалить содержимое", style=nextcord.ButtonStyle.red, emoji="🔪")
    async def drop_database_confirm_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        sql.drop_tables()
        logging.info('Все информация в базе данных стерта')
        await interaction.edit_original_message(
            embed=messages.database_deletion().embed,
            attachments=[],
            view=None
        )


def apply_event_settings():
    global event_settings
    global sending_date
    event_settings = utils.load_event_settings()
    if not event_settings:
        logging.error('Конфигурационный файл settings.json не найден. Работа бота невозможна!')
        return
    sending_date = datetime.date(
        day=event_settings['sending_date']['day'],
        month=event_settings['sending_date']['month'],
        year=event_settings['sending_date']['year']
    )


async def send_letters():
    global send_already_letters_count
    send_already_letters_count = 0
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
            send_already_letters_count += 1
            logging.info(f'Письмо для {recipient_username} отправлено!')
        except nextcord.Forbidden:
            logging.error(f'Письмо для {recipient_username} не отправлено, '
                          f'поскольку бот не имеет разрешений для отправки '
                          f'сообщений этому пользователю')
        except nextcord.HTTPException as e:
            logging.error(f'Письмо для {recipient_username} не отправлено, '
                          f'произошла ошибка класса HTTPException. '
                          f'Дополнительная информация: {e}')
        except Exception as e:
            logging.error(f'Письмо для {recipient_username} не отправлено, '
                          f'произошла неизвестная общая ошибка. '
                          f'Дополнительная информация: {e}')


@client.event
async def on_ready():
    logging.info(f'Бот залогинен под именем: {client.user.name}')
    if not os.path.exists('database'):
        os.makedirs('database')
    apply_event_settings()
    sql.create_tables()
    scheduled_send_letters.start()


@client.command()
@commands.has_permissions(administrator=True)
async def start_secret_letters(ctx):
    introduction = MessageContainer(
        title=f"**{event_settings['title']}**",
        description=event_settings['description'],
        image_path=config.INTRODUCTION_IMAGE_FILEPATH
    )
    await ctx.send(
        embeds=[introduction.embed, messages.instruction().embed],
        files=[introduction.image, messages.instruction().image],
        view=MainMenuButtons()
    )


@client.command()
@commands.has_permissions(administrator=True)
async def admin_secret_letters(ctx):
    await ctx.send(
        embed=messages.admin_instruction().embed,
        file=messages.admin_instruction().image,
        view=AdminMenuButtons()
    )


@admin_secret_letters.error
@start_secret_letters.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=messages.no_permission_error().embed)


@tasks.loop(time=launch_time)
async def scheduled_send_letters():
    global current_date
    current_date = datetime.date.today()
    if current_date != sending_date:
        logging.info(f'Ждем. До отправки осталось {(sending_date - current_date).days} дней')
        return
    logging.info('Назначенный день настал, и рассылка начата!')
    await send_letters()
