import nextcord
import engine.config as config
import io


class MessageContainer:
    def __init__(self, title=None, description=None, image_path=None, image_binary_data=None, has_author=False):
        self.__embed = nextcord.Embed(
            title=title,
            description=description,
            colour=nextcord.Colour.from_rgb(*config.BASIC_COLOR_CODE),
        )
        if image_binary_data:
            fp = io.BytesIO(image_binary_data)
        else:
            if not image_path:
                image_path = config.SEPARATOR_FILEPATH
            fp = image_path
        image_filename = image_path.split('/')[-1]
        image_attachment = f'attachment://{image_filename}'
        self.__embed.set_image(url=image_attachment)
        self.__image = nextcord.File(fp=fp, filename=image_filename)
        if has_author:
            self.__embed.set_author(name=config.HEADER_BOT_NAME, icon_url=config.HEADER_BOT_AVATAR_STATIC_URL)
            self.__embed.set_footer(text=config.FOOTER_TEXTLINE)

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
        letter_greeting = f"✨ ***Приветствую, {recipient_globalname}.*** ✨"
        if sender_alias:
            notify = f"Тебе отправил(а) секретное послание {sender_alias}!"
        else:
            notify = "Тебе отправили секретное послание!"
        body_content = f"💌 **{notify}**\n\n" + db_record[7]
        super().__init__(
            title=letter_greeting,
            description=body_content,
            image_binary_data=image_binary_data,
            image_path=image_filename,
            has_author=True,
        )


ERROR_HEADER = "Ошибка! :("


def introduction(event_title, event_description):
    return MessageContainer(
        title=f"**{event_title}**",
        description=event_description,
        image_path=config.INTRODUCTION_IMAGE_FILEPATH
    )


def instruction():
    return MessageContainer(
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
                    "По нажатию кнопки *список отправленных писем* будет вызван полный список написанных "
                    "вами писем, стоящих в очередь на отправку. Вы можете просмотреть их содержимое, а также "
                    "удалить, однако помните - **удаление является необратимым!**\n"
                    "Вы можете отправить пользователю только одно письмо. Общее количество отправляемых "
                    "писем не должно превышать 25 штук."
    )


def no_permission_error():
    return MessageContainer(
        title=ERROR_HEADER,
        description="У вас нет прав для использования этой команды!"
    )


def recipient_error(username):
    return MessageContainer(
        title=ERROR_HEADER,
        description=f"Пользователь с именем {username} отсутствует на сервере."
    )


def send_already_error():
    return MessageContainer(
        title=ERROR_HEADER,
        description="Вы уже отправили письмо этому пользователю!"
    )


def attached_image_error():
    return MessageContainer(
        title=ERROR_HEADER,
        description="Ссылка битая, либо это не изображение."
    )


def self_sending_error():
    return MessageContainer(
        title=ERROR_HEADER,
        description="Конечно, технически вы могли бы отправить письмо сами себе, но это грустно, "
                    "поэтому давайте оставим эту затею."
    )


def send_success(username):
    return MessageContainer(
        title="Готово!",
        description=f"Письмо создано! Оно будет отправлено пользователю {username} в назначенный срок, указанный в "
                    "описании ивента."
    )


def expired_event():
    return MessageContainer(
        title="Поезд ушел",
        description="Ивент завершен. Вы больше не можете втайне делиться кошачьими нежностями. "
                    "Все ранее созданные вами письма были отправлены адресатам."
    )


def old_event():
    return MessageContainer(
        title="Поезд ушел",
        description="Этот ивент уже давно завершен. Просмотр ранее созданных писем недоступен."
    )


def max_count_error():
    return MessageContainer(
        title=ERROR_HEADER,
        description="Вы уже отправили 25 писем разным людям. Это максимально возможное число!"
    )


def empty_list_error():
    return MessageContainer(
        title=ERROR_HEADER,
        description="Вы еще не отправили ни одного письма."
    )


def not_exist_error():
    return MessageContainer(
        title=ERROR_HEADER,
        description="Этого письма не существует. Перезагрузите список писем, и попробуйте снова."
    )


def deletion():
    return MessageContainer(
        title="Под нож!",
        description="Письмо удалено :("
    )


def admin_instruction():
    return MessageContainer(
        title="Админка",
        description="Панель управления ботом содержит опции, инструкция по использованию которых приведена ниже.\n\n"
                    "- **Новый ивент**\n"
                    "Заполните появившуюся форму. Придумайте название нового ивента и подробно опишите его содержание "
                    "и смысл в соответствующих двух первых полях формы. Прикрепите картинку для приветственного "
                    "сообщения бота и укажите дату, когда будет осуществляться автоматическая рассылка собранных "
                    "писем. *Внимание!* Имейте в виду, что после отправки данных настройки текущего ивента будут "
                    "необратимо перезаписаны, а все содержимое базы данных - автоматически стерто!\n"
                    "- **Ручная рассылка**\n"
                    "Опция для ручной рассылки писем. Содержит два варианта действий.\nПервый вариант позволяет "
                    "разослать все содержащиеся в базе данных письма. Используйте эту функцию только в "
                    "экстренных случаях, когда что-то пошло не так и автоматическая рассылка не сработала - например "
                    "в ситуации, когда у вашего хостера отключилось электричество именно в те часы, на которые "
                    "была назначена отправка.\nВторой вариант дает возможность разослать письма, которые не были "
                    "доставлены в ходе плановой отправки. По умолчанию функция неактивна, доступ к ней открвается "
                    "только в том случае, если кто-то не получил свое письмо. Обычно такое происходит из-за закрытой "
                    "лички у пользователя. Попросите соответствующих пользователей открыть личку и используйте "
                    "данную функцию для доотправки писем им.\n"
                    "- **Статистика**\n"
                    "Позволяет посмотреть общее количество писем, созданное участниками в ходе ивента, и количество "
                    "успешно разосланных писем в день отправки. Эти два числа должны совпасть, если это не так, "
                    "просмотрите логи бота и убедитесь, в чем причина того, что часть писем не была отправлена.\n"
                    "Если некоторые участники не получили письма, их количество и имена будут перечислены строкой "
                    "ниже. В случае, если вы видите такой список, используйте ручную рассылку для того, чтобы "
                    "попытаться отправить им письма заново.\n"
                    "- **Стереть базу данных**\n"
                    "Уничтожение текущей базы данных с письмами, собранными в ходе текущего ивента.\n\n"
                    "После того, как будут указаны параметры нового ивента, запускайте его "
                    "командой `!start_secret_letters`."
    )


def admin_option_only_warning():
    return MessageContainer(
        title=ERROR_HEADER,
        description="Использовать опции админ-панели могут только администраторы сервера."
    )


def new_event_successful_created():
    return MessageContainer(
        title="Успех!",
        description="Новый ивент благополучно создан! Теперь вы можете запустить его с помощью стартовой команды."
    )


def manual_sending_warning(days_before_scheduled_start):
    description = "Вы уверены, что хотите начать ручную рассылку писем?"
    if days_before_scheduled_start > 0:
        description += f" Осталось еще {days_before_scheduled_start} дней до планового начала ивента!"
    elif days_before_scheduled_start < 0:
        description += f" Прошло уже {-days_before_scheduled_start} дней с окончания ивента!"
    return MessageContainer(
        title="Экстренная ситуация!",
        description=description
    )


def stats(all_letters_count, send_already_letters_count, sending_date, send_failure_recipients):
    description = (f"Общее количество писем, написанных участниками: **{all_letters_count}**"
                   f"\nКоличество отправленных ботом писем в ходе последней рассылки: **{send_already_letters_count}**"
                   f"\n\nДата отправки сообщений: {sending_date}")

    if send_failure_recipients:
        description += (f"\n\nВ ходе рассылки {len(send_failure_recipients)} пользователей не получили письма из-за "
                        f"закрытой лички либо сетевых ошибок (для более подробной информации о причине ошибок "
                        f"смотрите логи). Список этих пользователей: "
                        f"**{', '.join([user[1] for user in send_failure_recipients])}**. Для того, чтобы попытаться "
                        f"повторно отправить им письма, используйте соответствующую опцию в меню ручной рассылки.")

    return MessageContainer(
        title="Статистика",
        description=description
    )


def manual_sending_start():
    return MessageContainer(
        title="Поехали!",
        description="Ручная рассылка писем начинается. В зависимости от их количества, этот процесс может занять от "
                    "нескольких секунд до минут."
    )


def database_deletion_warning():
    return MessageContainer(
        title="Предупреждение",
        description="Внимание! Данное действие необратимо! Все равно желаете стереть базу данных?"
    )


def database_deletion():
    return MessageContainer(
        title="Под нож!",
        description="База данных удалена."
    )


def invalid_date_warning():
    return MessageContainer(
        title=ERROR_HEADER,
        description="Дата указана неправильно, либо неверный формат, либо вы указали уже прошедший день."
    )
