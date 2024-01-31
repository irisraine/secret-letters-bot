import nextcord
import engine.config as config
import io


class MessageContainer:
    def __init__(self, title=None, description=None, image_path=None, image_data=None, author=False):
        self.__embed = nextcord.Embed(
            title=title,
            description=description,
            colour=nextcord.Colour.from_rgb(48, 213, 200),
        )
        if image_data:
            image_filename = image_data[1]
            fp = io.BytesIO(image_data[0])
        else:
            if not image_path:
                image_path = config.SEPARATOR_FILEPATH
            image_filename = image_path.split('/')[-1]
            fp = image_path
        image_attachment = f'attachment://{image_filename}'
        self.__embed.set_image(url=image_attachment)
        self.__image = nextcord.File(fp=fp, filename=image_filename)
        if author:
            self.__embed.set_author(name="Олень Вениамин", icon_url=config.BOT_AVATAR_STATIC_URL)
            self.__embed.set_footer(text="Сообщение отправлено ботом-оленем с сервера ⋆˙₊𝚆𝚎𝚜𝚝 𝚠𝚘𝚕𝚟𝚎𝚜₊˙⋆")

    @property
    def embed(self):
        return self.__embed

    @property
    def image(self):
        return self.__image


class Letter(MessageContainer):
    def __init__(self, db_record):
        recipient_globalname = db_record[3]
        sender_alias = db_record[6]
        image_binary_data = db_record[8]
        image_filename = db_record[9]
        image_data = (image_binary_data, image_filename) if image_binary_data else None
        letter_greeting = f"✨ ***Приветствую, {recipient_globalname}.*** ✨"
        if sender_alias:
            notify = f"Тебе отправил(а) секретное послание {sender_alias}!"
        else:
            notify = "Тебе отправили секретное послание!"
        body_content = f"💌 **{notify}**\n\n" + db_record[7]
        super().__init__(
            title=letter_greeting,
            description=body_content,
            image_data=image_data,
            author=True,
        )


ERROR_HEADER = "Ошибка! :("

introduction = MessageContainer(
    title="**Олень Валентин**",
    description="С давних времен существует легенда о прекрасном быстроногом олене, который странствует по миру и "
                "приносит людям тёплые послания в письмах от других людей. Имя этого оленя — Валентин, и на этот "
                "раз он забрёл и к нам в гости. Давайте встретим гостя как положено, не пожалев ему писем и "
                "открыток, чтобы 14 февраля где-то на другом конце планеты он вручил эти послания адресатам, "
                "и в мире стало чуточку светлей.",
    image_path=config.INTRODUCTION_IMAGE_FILEPATH
)
instruction = MessageContainer(
    title="**Инструкция**",
    description="- В поле ***имя адресата*** укажите имя пользователя, которому хотите написать "
                "(например: bibster). Оно находится в профиле человека ПОД отображаемым именем.\n"
                "- Получатель не узнает, кто вы. "
                "Однако в поле ***мой псевдоним*** вы можете назвать себя тайным именем.\n"
                "- В поле ***текст письма*** напишите свое письмо.\n- "
                "В поле ***открытка*** укажите ссылку на изображение, которое хотите прикрепить к письму "
                "(в формате JPG, PNG или GIF). Если вы хотите отправить свою пикчу, то её надо залить куда-нибудь "
                "(можно другу в лс) потом скопировать ссылку на неё, вставить в форму, и "
                "после отправки формы можно эту картинку удалять.\n\n"
                "В случае неверных имени пользователя или ссылки на картинку произойдёт ошибка и вам придётся "
                "заново все заполнять. Поэтому лучше заранее наберите текст в другом месте, "
                "и затем вставьте его в форму.\n"
                "По нажатию кнопки *список отправленных валентинок* будет вызван полный список написанных "
                "вами валентинок, стоящих в очередь на отправку. Вы можете просмотреть их содержимое, а также "
                "удалить, однако помните - **удаление является необратимым!**\n"
                "Вы можете отправить пользователю только одну валентинку. Общее количество отправляемых "
                "валентинок не должно превышать 25 штук."
)
no_permission_error = MessageContainer(
    title=ERROR_HEADER,
    description="У вас нет прав для использования этой команды!"
)
recipient_error = MessageContainer(
    title=ERROR_HEADER,
    description="Пользователь с таким именем отсутствует на сервере."
)
send_already_error = MessageContainer(
    title=ERROR_HEADER,
    description="Вы уже отправили валентинку этому пользователю!"
)
attached_image_error = MessageContainer(
    title=ERROR_HEADER,
    description="Ссылка битая, либо это не изображение."
)
self_sending_error = MessageContainer(
    title=ERROR_HEADER,
    description="Конечно, технически вы могли бы отправить валентинку сами себе, но это грустно, "
                "поэтому давайте оставим эту затею."
)
send_success = MessageContainer(
    title="Отправлено!",
    description="Валентинка создана! Она будет отправлена указанному пользователю 14 февраля."
)
expired_event = MessageContainer(
    title="Поезд ушел",
    description="Ивент завершен. Вы больше не можете втайне делиться кошачьими нежностями. "
                "Все ранее созданные вами валентинки сегодня были отправлены адресатам."
)
max_count_error = MessageContainer(
    title=ERROR_HEADER,
    description="Вы уже отправили 25 валентинок разным людям. Это максимально возможное число!"
)
empty_list_error = MessageContainer(
    title=ERROR_HEADER,
    description="Вы еще не отправили ни одной валентинки."
)
not_exist_error = MessageContainer(
    title=ERROR_HEADER,
    description="Этой валентинки не существует. Перезагрузите список валентинок, и попробуйте снова"
)
deletion = MessageContainer(
    title="Под нож!",
    description="Валентинка удалена :("
)
