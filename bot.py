#!/usr/bin/python3
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from middlewares import rate_limit
from memory_profiler import memory_usage
import numpy as np
from functions import *
from loader import *


# ---------------------------------------------------- handlers ----------------------------------------------------
@dp.message_handler(content_types=['sticker'])
async def get_sticker_id(message: types.Message):
    if message.from_user.id in config.admins_list:
        await message.answer(message.sticker.file_id)


@dp.message_handler(commands=['get_mess_id'])
async def get_mess_id(message: types.Message):
    if message.from_user.id in config.admins_list:
        await message.answer(message.message_id)


@dp.message_handler(commands=['make_dot'])
async def return_message_id(message: types.Message):
    if message.from_user.id == config.admin_id:
        res = await bot.send_message(config.profile_id, '.')
        await bot.send_message(config.admin_id, res)


@dp.message_handler(commands=['make_rating'])
async def make_rating(message: types.Message):
    if message.from_user.id in config.admins_list:
        await make_rating_func()


@rate_limit(limit=3)
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        if not DB.user_exists(message.from_user.id):
            try:
                await bot.send_sticker(message.from_user.id,
                                       sticker='CAACAgIAAxkBAAIC2GKAGAP-qBGC5YInxh5PRu_8qJ_AAAKkHgAC1NEAAUgEnMSQXPUUySQE')
            except:
                pass

            mess = f"Здравствуй, {message.from_user.first_name} ! Приветствуем👋 вас в боте, " \
                   f"созданном для оперативного(быстрого) нахождения исполнителя какого-либо вузовского задания. " \
                   f"Будь то чертёж по начерталке✏️, или же расчётка по сопромату, ты точно найдёшь нужного тебе человека🤝." \
                   f"\n\nМы - те, кто не первый год помогаем ребятам с различным проблемами." \
                   f" И дабы облегчить вам процесс нахождения 🔎 помощника, мы создали этого бота." \
                   f"\n\nСоветую нажать /help ,чтобы разобраться в функционале."
            await bot.send_message(message.chat.id, mess)
            mess = 'P.S. <b>разработчики бота не несут ответственности за взаимоотношения между участниками</b>'
            await bot.send_message(message.chat.id, mess)
            DB.new_row_user_db(user_id=message.from_user.id, name=message.from_user.first_name)
            DB.all_users_list = DB.all_list()

            start_command = message.text
            refer_id = str(start_command[7:])
            if str(refer_id) != '':
                if str(refer_id) != str(message.from_user.id):
                    DB.update_in_user(user_id=message.from_user.id, dict_values={'refer_id': int(refer_id)})
                    try:
                        await bot.send_message(refer_id, 'По вашей ссылке зарегистровался новый пользователь!')
                    except:
                        pass
                else:
                    await message.answer('Нельзя регистрироваться по своей ссылке!')


@rate_limit(limit=3)
@dp.message_handler(commands=['my_profile'])
async def my_profile(message: types.Message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        if user_id in DB.ban_users_list:
            await message.answer('Вы забанены!')
            return
        count_refer = DB.get_count_referals(user_id=user_id)
        refer_info = f'Ваша реферальная ссылка:\n' \
                     f'https://t.me/{config.BOT_NICKNAME}?start={message.from_user.id}\n' \
                     f'Количество рефералов: {count_refer}\n'
        if DB.decider_exists(user_id):
            profile_id = DB.get_profile_id(user_id)
            await bot.forward_message(chat_id=user_id,
                                      from_chat_id=config.profile_id,
                                      message_id=profile_id)
            text = '\nНажмите:\n' \
                   '\n<b>Изменить профиль</b> - если Вы хотите поменять название ВУЗа, ' \
                   'добавить или удалить какой-либо предмет📖 \n\n' \
                   '<b>Закрыть профиль</b> - если Вы хотите прекратить быть Решалой как на какое-то время,' \
                   ' так и навсегда. Вы больше не сможете получать заказы, ' \
                   'пока снова не захотите вернуться в ряды Решал и открыть профиль💪🏻 ' \
                   '\nВсе ваши отзывы и оценки сохранятся.'
            await bot.send_message(user_id, text, reply_markup=Markup.key_profile_manage, parse_mode='HTML')
            await bot.send_message(user_id, refer_info)
        elif DB.dunno_exists(user_id):
            mess = 'Пока у вас обычный профиль заказчика.\n' \
                   'Хотите создать профиль исполнителя?'
            await bot.send_message(message.from_user.id, mess, reply_markup=Markup.choice_1)
            await bot.send_message(user_id, refer_info)
        else:
            await bot.send_message(message.from_user.id,
                                   'Хм... кажется вы пропустили начальную регистрацию, пожалуйста нажмите /start')


@dp.callback_query_handler(text_contains='profile_manage')
async def profile_manage(call: types.CallbackQuery):
    data_call = call.data.split(':')[-1]
    if data_call == 'make':
        await bot.send_message(call.from_user.id, "Напишите ваш университет(сокращенно)")
        await regist_decider.waiting_regist_univer.set()
    elif data_call == 'del':
        user_id = call.from_user.id
        profile_id = DB.get_profile_id(user_id)
        await bot.edit_message_text('Профиль закрыт', chat_id=config.profile_id, message_id=profile_id)
        DB.delete_user(user_id, sub=True)
        dict_values = {'decider': False,
                       'subject_count': 0}
        DB.update_in_user(user_id, dict_values)
        await call.message.edit_text('Ваш профиль решалы закрыт. Но вы всегда можете стать решалой, '
                                     'для этого нажмите команду /my_profile. \n'
                                     'Если вас не устроил сервис, то можете написать об этом админам через команду '
                                     '/help_me',
                                     reply_markup=None)


@dp.callback_query_handler(text_contains='profile_make', state="*")
async def new_profile_make(call: types.CallbackQuery):
    # await bot.delete_message(call.from_user.id, call.message.message_id)
    data_call = call.data.split(':')[-1]
    if data_call == 'info':
        mess = ' Исполнитель - проще говоря Решала💪🏻\n' \
               '📌Через бота заказчик отправляет задание, которое поступает Вам сообщением в чат 📨. ' \
               'Сообщения приходят только по тем предметам, которые отмечены в Вашем профиле. ' \
               'Далее Вы уже решаете - соглашаетесь или отказываетесь от работы 🛠\n\n' \
               'Если заказчик выбрал Вас как Решалу, ' \
               'то он напишет Вам в личном порядке и задаст вопросы, интересующие его🧐\n\n' \
               'Хотите стать Решалой?💪🏻'
        await call.message.edit_text(mess, reply_markup=Markup.choice_2)
    elif data_call == 'yes':
        await call.message.edit_text('Создание профиля', reply_markup=None)
        await call.message.answer("Напишите ваш университет(сокращенно)")
        await regist_decider.waiting_regist_univer.set()
    elif data_call == 'no':
        await call.message.edit_text('Вы отменили действие', reply_markup=None)


@rate_limit(limit=3)
@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    # в зависимости от профиля выдавать разную инфу
    if message.from_user.id in DB.ban_users_list:
        await message.answer('https://www.youtube.com/watch?v=2Q_ZzBGPdqE')
        return
    mess = '📌Спасибо, что нажали. По статистике 67% людей не читают инструкцию, но не будем о грустном. \n\n' \
           'Ниже приведены функции бота:\n\n' \
           '/send - основная функция бота для нахождения Решалы по какому-либо предмету 🤝\n\n' \
           '/my_profile - показывает ваш статус и даёт возможность стать Решалой💪\n\n' \
           '/info -  в этой функции представлена подробная инструкция по поиску Решалы🔎\n\n' \
           '/help_me - если у вас возникли проблемы, заметили ошибку или же просто хотите написать пожелания ' \
           'по улучшению бота🤖\n' \
           'Администраторы прочитают его и ответят, когда появится возможность❤️' \
           'А еще у нас есть свои стикеры https://t.me/addstickers/reshals'

    await bot.send_message(message.chat.id, mess, parse_mode='html')
    mess = f'''Для пожертвования средств разработчикам: \nтыкните для копирования \n`{config.card_num}`'''
    await bot.send_message(message.chat.id, mess, parse_mode='markdown')


@rate_limit(limit=3)
@dp.message_handler(commands=['info'])
async def info(message: types.Message):
    if message.from_user.id in DB.ban_users_list:
        await message.answer('https://www.youtube.com/watch?v=2Q_ZzBGPdqE')
        return
    mess = 'Инструкция по работе с ботом:\n\n' \
           'Для нахождения Решалы по Вашему предмету, необходимо отправить задание боту:\n\n' \
           '1. Нажмите на кнопку Меню и отправьте команду /send\n' \
           '2. Выберите предмет, по которому Вы хотите получить помощь🤝\n' \
           '3. Подробно распишите боту задание, интересующее Вас, ' \
           'и оправьте. При необходимости приложите фотографию или файл с заданием✉️\n' \
           '4. Как только на Ваше задание откликнутся ⏰ один или несколько Решал, ' \
           'Вам придет обратная связь с их ссылками, профилями и, возможно, комментарием по заданию.\n' \
           '5. Когда вы определились с Решалой, то нажмите Выбрать Решалу🚀\n' \
           '6. Вам необходимо перейти по ссылке выбранного Решалы🙋🏼 и, ' \
           'непосредственно, узнать все интересующие Вас вопросы напрямую.'
    if DB.decider_exists(message.from_user.id):
        mess += '\n\n\nИнструкция для решал:\n\n' \
                'Когда к вам приходит заказ:\n' \
                '- Вы можете откликнуться, чтобы Вашу заявку могли рассмотреть. \n' \
                '<em>При отклике, Вы можете оставить свой комментарий по поводу заказа.</em>\n' \
                '- Пожаловаться, если обнаружили неподобающий контент.\n' \
                '<em>Жалоба придет к администраторам и они её рассмотрят</em>\n\n' \
                'После отправки Вашего профиля, к вам могут обратиться в личном сообщении'
        await bot.send_message(message.chat.id, mess, parse_mode='html')
        return
    mess += '\n\nТак же у вас есть возможность самому стать Решалой, ' \
            'для этого нажмите /my_profile и следуйте дальнейшим инструкциям'
    await bot.send_message(message.chat.id, mess, parse_mode='html')


@dp.message_handler(commands=['helpa'])
async def helpa(message: types.Message):
    if await main_admin_test(message):
        await keyboard_admin(message)
    if await admins_test(message):
        mess = 'Команды для админов:\n' \
               '- Ответ определенному пользователю по id \n' \
               '/answer_user [id пользователя] текст сообщения \n' \
               '- Бан пользователя\n' \
               '/ban_user [id пользователя] \n' \
               '- Рассылка \n' \
               '/public \n' \
               '- Удаление пользователя \n' \
               '/delete_user id_user  \n' \
               '- Получение статистики \n' \
               '/statistics'
        await message.answer(mess)


class send_help_me_state(StatesGroup):
    send_help = State()


@rate_limit(limit=3)
@dp.message_handler(commands=['help_me'])
async def help_me(message: types.Message):
    if message.from_user.id in DB.ban_users_list:
        await message.answer('Вы забанены!')
        return
    keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Отмена']
    keyb.add(*buttons)
    await message.answer('Напишите сообщение техподдержке. Если хотите отменить отправку, напишите "Отмена"',
                         reply_markup=keyb)
    await send_help_me_state.send_help.set()


@dp.message_handler(state=send_help_me_state.send_help, content_types=['text'])
async def send_help_me(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await bot.send_message(message.chat.id, 'Отправка отменена', reply_markup=types.ReplyKeyboardRemove())
    else:
        print(1)
        key = await Markup.ban_user(message.from_user.id)
        print(2)
        print(3)
        await bot.send_message(config.SUPPORT_ID,
                               text=f'@{message.from_user.username} {message.from_user.id}',
                               parse_mode='html',
                               reply_markup=key)
        print(4)
        await bot.forward_message(chat_id=config.SUPPORT_ID,
                                  from_chat_id=message.from_user.id,
                                  message_id=message.message_id)
        print(5)
        await message.answer('Ваше сообщение отправлено админам,'
                             'в ближайшее время постараемся решить вашу проблему',
                             reply_markup=types.ReplyKeyboardRemove())

    await state.finish()


class send_task(StatesGroup):
    choice_sub = State()
    give_task = State()


@logger.catch()
@rate_limit(limit=config.limit_send)
@dp.message_handler(commands=['send'])
async def send(message: types.Message):
    if message.from_user.id in DB.ban_users_list:
        await message.answer('Вы забанены!')
        return
    elif not DB.user_exists(message.from_user.id):
        await bot.send_message(message.from_user.id,
                               'Хм... кажется вы пропустили начальную регистрацию, пожалуйста нажмите /start')
    elif message.chat.type == 'private':
        key = await Markup.subjects_task_with_see(config.all_subjects[1:])
        await message.answer('Выберите предмет', reply_markup=key)
        await send_task.choice_sub.set()
    else:
        await message.answer('Писать боту можно только в личку')


@dp.callback_query_handler(text_contains='all_subjects_task', state=send_task.choice_sub)
async def keyboard_subjects_task(call: types.CallbackQuery, state: FSMContext):
    data_call = call.data.split(':')[-1]
    if data_call == 'see':
        keyboard_hide = await Markup.subjects_task_with_hide(config.all_subjects[1:])
        mess = config.info_subs_mess
        await call.message.edit_text(mess, reply_markup=keyboard_hide)
    elif data_call == 'hide':
        keyboard_see = await Markup.subjects_task_with_see(config.all_subjects[1:])
        mess = 'Выберите предмет'
        await call.message.edit_text(mess, reply_markup=keyboard_see)
    else:
        await state.update_data(sub=data_call)
        await call.message.edit_text(f'Вы выбрали {data_call}', reply_markup=None)
        await bot.send_message(call.from_user.id, 'Теперь пришлите задание <b>одним сообщением</b>. \n'
                                                  'К сообщению можно прикрепить фотографию, документ, '
                                                  'или обойтись просто текстом с описанием задания.')
        await send_task.next()


@dp.message_handler(state=send_task.give_task, content_types=['text', 'photo', 'document'])
async def give_task(message: types.Message, state: FSMContext):
    await state.update_data(task_message=message)
    await message.reply('Подтвердите отправку задания', reply_markup=Markup.confirm_task)


@logger.catch()
@dp.callback_query_handler(text_contains='confirm_task_from_user', state=send_task.give_task)
async def keyboard_subjects_task(call: types.CallbackQuery, state: FSMContext):
    data_call = call.data.split(':')[-1]
    user_id = call.from_user.id
    task_data = await state.get_data()
    if data_call == 'yes':
        send_list_id = DB.get_list_desiders(task_data['sub'])
        if len(send_list_id) == 0:
            mess = 'К сожалению, не нашлось решалы по этому предмету. '
            await call.message.edit_text(mess, reply_markup=None)
        else:
            DB.activity_users_dict['send'] += 1
            mess = f'Количество решал по вашему предмету: {len(send_list_id)} \n' \
                   f'Как только кто-то отклинется на вашу задачу, я сразу же вам сообщу. ' \
                   f'На основе отзывов в канале вы сможете выбрать для себя лучшего решалу. \n' \
                   f'Когда вы договоритесь с одним из решал, нажмите на кнопку "Выбрать решалу", ' \
                   f'чтобы сообщений по вашему заданию больше не приходило'
            await call.message.edit_text(mess, reply_markup=None)
            for i in send_list_id:
                if i not in DB.ban_users_list:
                    try:
                        key = await Markup.deciders_answer(id_dunno=task_data['task_message'].from_user.id,
                                                           message_id=task_data['task_message'].message_id)
                        await bot.send_message(chat_id=i, text=f'Задание по #{task_data["sub"]}')
                        await task_data['task_message'].send_copy(chat_id=i, reply_markup=key)
                        await asyncio.sleep(0.1)
                    except:
                        pass
            if user_id in DB.to_do:
                DB.to_do[user_id].append(task_data['task_message'].message_id)
            else:
                DB.to_do[user_id] = [task_data['task_message'].message_id]

        await state.finish()
    elif data_call == 'no':
        await call.message.edit_text('Пришлите задание одним сообщением', reply_markup=None)
        return
    elif data_call == 'stop':
        await call.message.edit_text('Вы отменили отправку задния', reply_markup=None)
        await state.finish()


@dp.callback_query_handler(text_contains='dunno_answer_data')
async def dunno_answer(call: types.CallbackQuery):
    data_call = call.data.split(':')
    task_message = int(data_call[3])
    id_dunno = int(data_call[2])
    action = data_call[1]
    if action == 'yes':
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer('По этому заданию вас больше не потревожат')
        DB.activity_users_dict['close'] += 1
        if task_message in DB.to_do[id_dunno]:
            DB.to_do[id_dunno].remove(task_message)
    pass


class deciders_answer_states(StatesGroup):
    send_comment = State()


@dp.callback_query_handler(text_contains='deciders_answer_data')
async def deciders_answer(call: types.CallbackQuery, state: FSMContext):
    data_call = call.data.split(':')
    task_message = int(data_call[3])
    id_dunno = int(data_call[2])
    action = data_call[1]
    await state.update_data(task_message=task_message)
    await state.update_data(id_dunno=id_dunno)
    if action == 'yes':
        if bool(DB.to_do.get(id_dunno)):
            if task_message in DB.to_do.get(id_dunno):
                await call.message.edit_reply_markup(None)
                keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
                buttons = ['Пропустить']
                keyb.add(*buttons)
                await call.message.answer('Напишите комментарий к отклику.\n'
                                          'Если не хотите писать комментарий, то напишите "Пропустить"',
                                          reply_markup=keyb)
                await deciders_answer_states.send_comment.set()
            else:
                await call.message.edit_text('К сожалению по этому заданию уже нашелся решала', reply_markup=None)
        else:
            await call.message.edit_text('К сожалению по этому заданию уже нашелся решала', reply_markup=None)

    elif action == 'prob':
        res = await call.message.edit_reply_markup(reply_markup=None)
        key = await Markup.ban_user(id_dunno)
        await bot.send_message(config.SUPPORT_ID, f'#Жалоба на `{id_dunno}`', parse_mode='markdown', reply_markup=key)
        await bot.forward_message(chat_id=config.SUPPORT_ID,
                                  from_chat_id=call.from_user.id,
                                  message_id=res.message_id)
        await call.message.edit_text('Сообщение с жалобой отправлено админам.')


@dp.message_handler(state=deciders_answer_states.send_comment, content_types=['text'])
async def send_comment_decider(message: types.Message, state: FSMContext):
    keyb = types.ReplyKeyboardRemove()
    if message.text.lower() == 'пропустить':
        await message.answer('Ваш профиль отправлен пользователю', reply_markup=keyb)
        mess = f'@{message.from_user.username} откликнулся'
    else:
        await message.answer('Ваш комментарий и профиль отправлены пользователю', reply_markup=keyb)
        mess = f'@{message.from_user.username} откликнулся: \n' \
               f'{message.text}'
    user_data = await state.get_data()

    task_message = user_data.get('task_message')
    id_dunno = user_data.get('id_dunno')
    profile_id = DB.get_profile_id(message.from_user.id)
    await bot.forward_message(chat_id=id_dunno,
                              from_chat_id=config.profile_id,
                              message_id=int(profile_id))
    key = await Markup.dunno_answer(id_dunno=id_dunno, message_id=task_message)
    await bot.send_message(id_dunno,
                           mess,
                           reply_markup=key,
                           reply_to_message_id=task_message)
    await state.finish()


@dp.callback_query_handler(text_contains='dunno_clear_data')
async def dunno_clear_data(call: types.CallbackQuery):
    data_call = call.data.split(':')
    task_message = int(data_call[3])
    id_dunno = int(data_call[2])
    action = data_call[1]
    DB.to_do[id_dunno].remove(task_message)
    if action == 'yes':
        DB.activity_users_dict['close'] += 1
    elif action == 'think':
        DB.activity_users_dict['cancel'] += 1
    elif action == 'no':
        DB.activity_users_dict['no close'] += 1
    await call.message.edit_text('Спасибо за ответ', reply_markup=None)


@dp.callback_query_handler(text_contains='ban_user_data')
async def make_ban_handler(call: types.CallbackQuery):
    data_call = call.data.split(':')
    id_dunno = int(data_call[2])
    action = data_call[1]
    key_ban = await Markup.ban_user(id_dunno)
    if action == 'ban':
        if id_dunno not in DB.ban_users_list:
            DB.ban(id_dunno, yes=True)
            key = await Markup.no_ban_user(id_dunno)
            await call.message.edit_text(f'Пользователь {id_dunno} забанен', reply_markup=key)
        else:
            await call.message.edit_text(f'Пользователь {id_dunno} забанен ', reply_markup=None)
    elif action == 'noban':
        DB.ban(id_dunno, no=True)
        await call.message.edit_text(f'Пользователь {id_dunno} разбанен', reply_markup=key_ban)
    elif action == 'ban_30':
        if id_dunno not in DB.ban_users_list:
            await call.message.edit_text(f'Пользователь {id_dunno} забанен на 30 минут', reply_markup=None)
            await bot.send_message(id_dunno, 'Вы забанены на 30 минут')
            await ban_time(1800, id_dunno)
            await call.message.edit_text(f'Пользователь {id_dunno} разбанен', reply_markup=key_ban)
        else:
            await call.message.edit_text(f'Пользователь {id_dunno} забанен ', reply_markup=None)
    elif action == 'ban_1':
        if id_dunno not in DB.ban_users_list:
            await call.message.edit_text(f'Пользователь {id_dunno} забанен на 1 час', reply_markup=None)
            await bot.send_message(id_dunno, 'Вы забанены на 1 час ')
            await ban_time(3600, id_dunno)
            await call.message.edit_text(f'Пользователь {id_dunno} разбанен', reply_markup=key_ban)
        else:
            await call.message.edit_text(f'Пользователь {id_dunno} забанен ', reply_markup=None)
    elif action == 'ban_1_day':
        if id_dunno not in DB.ban_users_list:
            await call.message.edit_text(f'Пользователь {id_dunno} забанен на 1 день', reply_markup=None)
            await bot.send_message(id_dunno, 'Вы забанены на 1 день ')
            await ban_time(36000, id_dunno)
            await ban_time(36000, id_dunno)
            await call.message.edit_text(f'Пользователь {id_dunno} разбанен', reply_markup=key_ban)
        else:
            await call.message.edit_text(f'Пользователь {id_dunno} забанен ', reply_markup=None)
    elif action == 'ban_1_week':
        if id_dunno not in DB.ban_users_list:
            await call.message.edit_text(f'Пользователь {id_dunno} забанен на неделю', reply_markup=None)
            await bot.send_message(id_dunno, 'Вы забанены на неделю ')
            for i in range(13):
                await ban_time(36000, id_dunno)
            await call.message.edit_text(f'Пользователь {id_dunno} разбанен', reply_markup=key_ban)
        else:
            await call.message.edit_text(f'Пользователь {id_dunno} забанен ', reply_markup=None)


@dp.message_handler(content_types=['poll'])
async def regist_univer(message: types.Message):
    if message.chat.id == -1001785673732:
        if message.from_user.id == 136817688:
            for i in DB.all_list():
                try:
                    await message.forward(chat_id=i)
                    await asyncio.sleep(0.1)
                except:
                    pass
            await message.answer('Сообщения разосланы')
        else:
            await message.answer('Вы не бог, я тут бот')


# ------------------- regist -------------------
class regist_decider(StatesGroup):
    waiting_regist_univer = State()
    waiting_regist_username = State()
    waiting_regist_subjects = State()
    waiting_end_regist = State()


@dp.message_handler(state=regist_decider.waiting_regist_univer, content_types=types.ContentTypes.TEXT)
async def regist_univer(message: types.Message, state: FSMContext):
    if len(message.text) > 15:
        await message.answer('Текст не должен превышать 15 символов')
        return
    for i in ['!', '/', '@', '.', ',', '#', '$', '%', '*', '№']:
        if i in message.text:
            await message.answer('Текст не должен содержать лишних символов')
            return
    await state.update_data(univer=message.text)
    if message.from_user.username is None:
        key_regist = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['Сделал']
        key_regist.add(*buttons)
        await message.answer("Кажется у вас нет имени пользователя в telegram. "
                             "Зайдите в настройки профиля и внесите имя пользователя, "
                             "после этого можно продолжить регистрацию."
                             "\n\nИмя пользователя нужно для возможности связи с вами, "
                             "если к вам обратятся за помощью по предмету.",
                             reply_markup=key_regist)
    else:
        key_regist = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ['ДА', 'НЕТ']
        key_regist.add(*buttons)
        await message.answer(f'Ваше имя пользователя @{message.from_user.username},'
                             f'Если вы согласны продолжить с ним, то нажмите кнопку "ДА". '
                             f'Если желаете изменить, нажмите "НЕТ".',
                             reply_markup=key_regist)
    await regist_decider.next()


@dp.message_handler(state=regist_decider.waiting_regist_username, content_types=types.ContentTypes.TEXT)
async def regist_username(message: types.Message, state: FSMContext):
    key_regist = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Сделал']
    key_regist.add(*buttons)
    if message.text.lower() == 'нет':
        await message.answer("Чтобы изменить имя пользователя в telegram. "
                             "Зайдите в настройки профиля и смените имя пользователя, "
                             "после этого можно продолжить регистрацию."
                             "\n\nИмя пользователя нужно для возможности связи с вами, "
                             "если к вам обратятся за помощью по предмету.",
                             reply_markup=key_regist)
        return
    if message.from_user.username is None:

        await message.answer(f"Сделайте имя пользователя. После этого напишите 'сделал'."
                             f"\nОно будет исползоваться для возможности связи с вами, "
                             f"если к вам обратятся за помощью по предмету.",
                             reply_markup=key_regist)
    else:
        keyboard_with_all_subjects = await Markup.keyboard_with_all_subjects_with_see(config.all_subjects[1:])
        keyb = types.ReplyKeyboardRemove()
        await message.answer(f"Имя пользователя: @{message.from_user.username}", reply_markup=keyb)
        await state.update_data(username='@' + message.from_user.username)
        await regist_decider.next()
        await state.update_data(subjects=[])
        await message.answer('Теперь выберите предметы, которые вам интересны. \n'
                             'Выбирайте с умом, т.к. по выбранным предметам вам будут приходить уведомления'
                             'Также можете посмотреть расшифровку предметов👇',
                             reply_markup=keyboard_with_all_subjects)


@dp.callback_query_handler(text_contains='give_all_subjects', state=regist_decider.waiting_regist_subjects)
async def give_subjects_info(call: types.CallbackQuery, state: FSMContext):
    data_call = call.data.split(':')[-1]
    if data_call == 'see':
        keyboard_hide = await Markup.keyboard_with_all_subjects_with_hide(config.all_subjects[1:])
        mess = config.info_subs_mess
        await call.message.edit_text(mess, reply_markup=keyboard_hide)
    elif data_call == 'hide':
        keyboard_see = await Markup.keyboard_with_all_subjects_with_see(config.all_subjects[1:])
        mess = 'Теперь выберите предметы, которые вам интересны. \n' \
               'Также можете посмотреть расшифровку предметов👇'
        await call.message.edit_text(mess, reply_markup=keyboard_see)
    elif data_call == 'stop':
        user_data = await state.get_data()
        if len(user_data.get('subjects')) == 0:
            await call.answer(f'Пожалуйста выберите предмет')
        else:
            key_regist = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = ['Подтвердить', 'Начать заново', 'Отменить']
            key_regist.add(*buttons)
            await bot.send_message(call.from_user.id,
                                   f"- Универ\n{user_data.get('univer')} \n"
                                   f"- Предметы\n{', '.join(set(user_data.get('subjects')))} \n"
                                   f"- Никнейм\n{user_data.get('username')} \n",
                                   reply_markup=key_regist)
            await state.update_data(subjects=set(user_data.get('subjects')))
            await regist_decider.next()
    else:
        await call.answer(f'{data_call} добавлен')
        user_data = await state.get_data()
        subs = user_data.get('subjects')
        subs.append(data_call)
        await state.update_data(subjects=subs)


# @dp.message_handler(state=regist_decider.waiting_regist_subjects, content_types=types.ContentTypes.TEXT)
# async def regist_subjects(message: types.Message, state: FSMContext):
#     all_subjects = config.all_subjects[1:]
#     subs = message.text.lower().replace(' ', '').split(',')
#     for i in subs:
#         if i not in all_subjects:
#             await message.answer('Выберите предметы, нажав на кнопки')
#             return

@logger.catch()
@dp.message_handler(state=regist_decider.waiting_end_regist, content_types=types.ContentTypes.TEXT)
async def stop_regist(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    keyb = types.ReplyKeyboardRemove()
    if message.text.lower() == 'подтвердить':
        # добалве пользователя в базу
        profile_id = DB.get_profile_id(user_id)
        if bool(profile_id):
            res = profile_id
            were_decider = True
        else:
            res = await bot.send_message(config.profile_id, 'Создание нового профиля')
            res = res.message_id
            were_decider = False
        user_data = await state.get_data()
        dt = datetime.datetime.now(tz=config.tz)
        dict_values = {'decider': True,
                       'pay_date': dt,
                       'username': user_data.get('username'),
                       'end_pay_date': await give_date_subscription(dt, config.prob_pereod),
                       'univer': user_data.get('univer'),
                       'subject_count': len(user_data.get('subjects')),
                       'profile_id': int(res)}
        DB.update_in_user(user_id, dict_values)
        sub = user_data.get('subjects')
        if were_decider:
            DB.delete_user(user_id=user_id, sub=True)
        DB.new_row_subject_db(user_id, *sub)
        text = await give_profile_desider_text(user_id=user_id, chanel=True)
        await bot.edit_message_text(text, chat_id=config.profile_id, message_id=res)
        await bot.send_message(message.chat.id,
                               text='Отлично! Ваш профиль сохранен. '
                                    'Теперь вы официально Решала! '
                                    'Когда кому-то понадобится помощь '
                                    'по вашим предметам, мы обязательно сообщим об этом.',
                               reply_markup=keyb)
        await message.answer('А это ваш профиль в канале решал. '
                             'Когда вы будете откликаться на задания, '
                             'бот отправит ваш профиль заказчику для возможности связи с вами. '
                             'После успешной сделки, заказчик может оставить комментирий и реакцию под вашим профилем.')
        await bot.forward_message(chat_id=message.from_user.id,
                                  from_chat_id=config.profile_id,
                                  message_id=res, )
        await state.finish()
    elif message.text.lower() == 'начать заново':
        await bot.send_message(message.chat.id,
                               text='Регистрация началась заново.\n'
                                    'Напишите ваш университет(сокращенно)',
                               reply_markup=keyb)
        await regist_decider.waiting_regist_univer.set()
    elif message.text.lower() == 'отменить':
        await message.answer("Регистрация отменена", reply_markup=keyb)
        await state.reset_state(with_data=False)
        await state.finish()
    else:
        await message.answer('Пожалуйста введите одно из предлагаемых вариантов')
        await regist_decider.waiting_regist_univer.set()


# ---------------------------------------------------- admins  ----------------------------------------------------
@dp.message_handler(commands=['chat_info'])  # main admin
async def chat_info(message: types.Message):
    if await main_admin_test(message):
        await bot.send_message(message.chat.id, message.chat.id)


@dp.message_handler(commands=['dump'])  # main admin
async def dump(message: types.Message):
    if await main_admin_test(message):
        await make_dump()


@logger.catch()
@dp.message_handler(commands=['restart_data'])  # main admin
async def restart_data(message: types.Message):
    if await main_admin_test(message):
        DB.ban_users_list = DB.ban_list
        try:
            DB.close()
            DB.connect()
            await bot.send_message(config.admin_id, 'Перезагрузка завершена')
        except:
            await bot.send_message(config.admin_id, 'Ошибка перезагрузки')


@dp.message_handler(commands=['answer_user'])  # admins
async def answer_user(message: types.Message):
    if await admins_test(message):
        text = message.text.split()
        id_user = text[1]
        await bot.send_message(id_user, 'Сообщение от админов: ' + ' '.join(text[2:]))


@logger.catch()
@dp.message_handler(commands=['ban_user'])  # admins
async def ban_user_command(message: types.Message):
    if await admins_test(message):
        text = message.text.split()
        id_user = text[1]
        key = await Markup.ban_user(id_user)
        await bot.send_message(config.SUPPORT_ID, f'Пользователь {id_user}', reply_markup=key)


class send_public(StatesGroup):
    choice_users = State()
    send_publication = State()
    confirm_publication = State()


@dp.message_handler(commands=['public'])
async def public(message: types.Message):
    if await admins_test(message):
        keyb = Markup.keyboard_public()
        await message.answer('Кому отправить?', reply_markup=keyb)
        await send_public.choice_users.set()


@dp.callback_query_handler(text_contains='choice_public', state=send_public.choice_users)
async def keyboard_choice_public(call: types.CallbackQuery, state: FSMContext):
    data_call = call.data.split(':')[-1]
    await call.message.edit_text(f'Вы выбрали {data_call}', reply_markup=None)
    await state.update_data(choice_users=data_call)
    await bot.send_message(call.from_user.id, 'Отправь публикацию')
    await send_public.send_publication.set()


@dp.message_handler(state=send_public.send_publication, content_types=['text', 'photo', 'document'])
async def give_task(message: types.Message, state: FSMContext):
    await state.update_data(task_message=message)
    await message.reply('Подтвердите отправку', reply_markup=Markup.confirm_public)
    await send_public.confirm_publication.set()


@dp.callback_query_handler(text_contains='confirm_public_from_user', state=send_public.confirm_publication)
async def keyboard_subjects_task(call: types.CallbackQuery, state: FSMContext):
    data_call = call.data.split(':')[-1]
    task_data = await state.get_data()
    if data_call == 'yes':
        await call.message.edit_text('Отправка', reply_markup=None)
        send_list_id = 0
        if task_data['choice_users'] == 'all':
            send_list_id = DB.all_list()
        elif task_data['choice_users'] == 'desider':
            deciders_list = (DB.cursor.execute('SELECT telegram_id FROM user WHERE decider = True')).fetchall()
            send_list_id = [x[0] for x in deciders_list]
        elif task_data['choice_users'] == 'dunno':
            dunnos_list = (DB.cursor.execute('SELECT telegram_id FROM user WHERE dunno = True AND decider = False')).fetchall()
            send_list_id = [x[0] for x in dunnos_list]
        # from tqdm.contrib.telegram import tqdm
        # for i in tqdm(send_list_id, token=config.token, chat_id=call.from_user.id):
        for i in send_list_id:
            try:
                await task_data['task_message'].send_copy(chat_id=i)
                await asyncio.sleep(0.1)
            except:
                pass
        await bot.send_message(call.from_user.id, 'Сообщения разосланы')
        await state.finish()
    elif data_call == 'no':
        await call.message.edit_text('Отправь публикацию', reply_markup=None)
        await send_public.send_publication.set()
    elif data_call == 'stop':
        await call.message.edit_text('Вы отменили отправку публикации', reply_markup=None)
        await state.finish()


@dp.message_handler(commands=['statistics'])  # admins
async def statistics(message: types.Message):
    if await admins_test(message):
        await send_statistic()


@dp.message_handler(commands=['keyboard_stop'])  # main admin
async def keyboard_stop(message: types.Message):
    if await main_admin_test(message):
        keyb = types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, text='Выключение клавиатуры', reply_markup=keyb)


@dp.message_handler(commands=['testing'])  # main admin
async def testing(message: types.Message):
    if await main_admin_test(message):
        # await message.answer(f'[+]')
        # mem = memory_usage(-1, include_children=True, multiprocess=True)
        # mess = f'{mem} \n\n' \
        #        f'all = {np.sum(mem)}'
        # await message.answer(mess)
        for i in trange(1000000, token=config.token, chat_id=message.from_user.id):
            print(i)


        # all_list = DB.all_list()
        # for i in all_list:
        #     DB.cursor.execute('DELETE FROM user WHERE telegram_id = ?', (i, ))
        #     DB.cursor.execute('DELETE FROM subject WHERE telegram_id = ?', (i, ))
        # DB.conn.commit()
        # await bot.send_message(config.admin_id, 'База очищена')

        # await clear_to_do()
        # while True:
        #     await asyncio.sleep(5)
        #     await message.answer(f'{message.from_user.username} прошло не меньше 5 секунд')


@logger.catch()
@dp.message_handler(commands=['delete_user'])  # admins
async def delete_user_command(message: types.Message):
    if await admins_test(message):
        text = message.text.split()
        id_user = int(text[1])
        profile_id = DB.get_profile_id(id_user)
        await bot.edit_message_text('Профиль удален', chat_id=config.profile_id, message_id=profile_id)
        DB.delete_user(user_id=id_user, user=True)
        if DB.decider_exists(message.from_user.id):
            DB.delete_user(user_id=id_user, sub=True)
        await bot.send_message(config.SUPPORT_ID, f'Пользователь {id_user} удален')


# ---------------------------------------------------- RUN ----------------------------------------------------

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=start_bot, on_shutdown=stop_bot, skip_updates=False)
