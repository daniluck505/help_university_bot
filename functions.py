import asyncio
from aiogram import types
from middlewares import ThrottlingMiddleware
from loguru import logger
from loader import *
import datetime
import Markup


@logger.catch()
async def start_bot(dp):
    try:
        await bot.send_message(str(config.admin_id), 'Бот запущен')
    except:
        pass
    await setup(dp)
    logger.add('debug.log', format="{time} {level} {message}", level='DEBUG', rotation='45 MB', compression='zip')
    scheduler.add_job(send_statistic, 'cron',
                      day_of_week='mon-sun',
                      hour=config.hour_scheduler,
                      minute=config.minute_scheduler)
    scheduler.add_job(clear_to_do, 'cron',
                      day_of_week='mon-sun',
                      hour=22,
                      minute=5)
    # scheduler.add_job(subscrip_test_data, 'cron',
    #                   day_of_week='mon-sun',
    #                   hour=config.hour_scheduler,
    #                   minute=config.minute_scheduler+4)
    scheduler.add_job(make_dump, 'cron',
                      day_of_week='mon-sun',
                      hour=config.hour_scheduler,
                      minute=config.minute_scheduler + 6)
    scheduler.add_job(make_rating_func, "interval", minutes=60)
    # https://telegra.ph/Zapusk-funkcij-v-bote-po-tajmeru-11-28
    scheduler.start()


async def stop_bot(dp):
    """ Выключение бота """
    DB.close()
    await bot.send_message(str(config.admin_id), 'Бот выключен')


@logger.catch()
async def send_statistic():
    """ Отправка статистики  """
    mess = DB.statistic()
    await bot.send_message(config.STATISTIC_ID, mess)


async def make_rating_func():
    dict_refers = {}
    for i in DB.get_list_users_id():
        count = DB.get_count_referals(i)
        if count != 0:
            dict_refers[DB.get_user_name(i)] = count
    sorted_values = sorted(dict_refers.values())
    mess = 'Рейтинг:\n' \
           'Имя - рефералы:\n\n'
    for j, i in enumerate(sorted_values[::-1]):
        for k in dict_refers.keys():
            if dict_refers[k] == i:
                mess += f'{j+1}. {k} - {dict_refers[k]}\n'
                break
    mess += f'\nПоследнее обновление \n' \
            f'{str(datetime.datetime.now(tz=config.tz))[:19]}'
    await bot.edit_message_text(mess,
                                chat_id=config.STATISTIC_ID,
                                message_id=config.refer_rating_message_id)


async def admins_test(message):
    """ Проверка id на админа  """
    if message.from_user.id in config.admins_list:
        return True
    else:
        return False


async def main_admin_test(message):
    """ Проверка id на админов  """
    if message.from_user.id == config.admin_id:
        return True
    else:
        return False


async def keyboard_admin(message):
    """ Отправка клавиатуры для админа  """
    keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['/dump', '/statistics', '/keyboard_stop', '/restart_data', '/chat_info', '/testing']
    keyb.add(*buttons)
    await bot.send_message(message.from_user.id, 'Клавиатура команд', reply_markup=keyb)


@logger.catch()
async def give_date_subscription(date, delta):
    """ Создание даты оплаты  """
    return date + datetime.timedelta(days=delta)


@logger.catch()
async def ban_user(telegram_id, yes=False, no=False):
    """ Бан по id  """
    DB.ban(telegram_id, yes=yes, no=no)
    DB.ban_users_list = DB.ban_list()


@logger.catch()
async def ban_time(time, id):
    if id not in DB.ban_users_list:
        DB.ban_users_list.append(id)
        await asyncio.sleep(time)
        try:
            DB.ban_users_list.remove(id)
        except:
            pass


async def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())


@logger.catch()
async def clear_to_do():
    d_copy = DB.to_do.copy()
    for i in d_copy:
        if len(d_copy[i]) == 0:
            del DB.to_do[i]
        else:
            try:
                for x in d_copy[i]:
                    await bot.forward_message(chat_id=i, from_chat_id=i, message_id=x)
                    key = await Markup.dunno_clear(id_dunno=i, message_id=x)
                    await bot.send_message(chat_id=i, text='Вы нашли решалу?', reply_markup=key)

            except:
                del DB.to_do[i]


@logger.catch()
async def make_dump():
    mess = DB.backup()
    if mess:
        with open('backup_db.db', "rb") as f:
            await bot.send_document(config.DUMP_ID, f)
    else:
        bot.send_message(config.DUMP_ID, f"Ошибка при резервном копировании: \n {mess}")


async def give_profile_desider_text(user_id, chanel=False):
    user_dict, list_sub = DB.get_user_info(user_id)
    sub_text = ', '.join(['#'+x for x in list_sub])

    if chanel:
        text = f'<b>{user_dict["name"]}</b>\n' \
               f'ВУЗ - {user_dict["univer"]}\n' \
               f'Предметы:\n{sub_text}\n'
    else:
        # end_pay_date = datetime.datetime.strptime(str(params["end_pay_date"])[:10], "%Y-%m-%d")
        # pay_date = datetime.datetime.strptime(str(params["pay_date"])[:10], "%Y-%m-%d")
        text = f'Ваш профиль:\n' \
               f'<b>{user_dict["name"]}</b>\n' \
               f'ВУЗ - {user_dict["univer"]}\n' \
               f'Предметы:\n{sub_text}\n' \
               f'Связь - {user_dict["username"]}\n'
       # f'Дней до конца подписки - {(end_pay_date-pay_date).days}'
    return text


# async def subscrib_test_data():
#     global main_df, subjects_df
#     data_main_df = await main_df.return_data(copy=True)
#     data_subjects_df = await main_df.return_data(copy=True)
#     deciders = data_main_df[data_main_df['decider'] == True]
#
#     pay = deciders['pay_date'].apply(lambda x: datetime.datetime.strptime(str(x)[:10], "%Y-%m-%d"))
#     end = deciders['end_pay_date'].apply(lambda x: datetime.datetime.strptime(str(x)[:10], "%Y-%m-%d"))
#     deciders['delta'] = (end - pay)
#     for index, row in deciders.iterrows():
#         if row['delta'].days < 0:
#             n = await main_df.find_user(row['telegram_id'])
#             n['decider'], n['pay'] = False, False
#             n['subject_count'] = 0
#             await main_df.replace_user(row['telegram_id'], n.values)
#             await main_df.save()
#             subs = [False for x in range(len(config.all_subjects))]
#             subs[0] = int(row['telegram_id'])
#             await subjects_df.replace_user(row['telegram_id'], [subs])
#             await subjects_df.save()
#             await bot.send_message(row['telegram_id'], 'Срок подписки истек')
#             await bot.edit_message_text(chat_id=config.profile_id,
#                                         message_id=row['profile_id'],
#                                         text='Профиль закрыт')
#         elif row['delta'].days < 3:
#             await bot.send_message(row['telegram_id'], f'Дней до конца подписки: {row["delta"].days}\n'
#                                                        f'Можете продлить подписку через команду /my_profile')