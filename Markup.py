from aiogram import Bot, types
from aiogram.utils.callback_data import CallbackData
import config
# from aiogram.dispatcher import Dispatcher
# from aiogram.utils import executor


choice_profile_1 = CallbackData('profile_make', 'action')
choice_1 = types.InlineKeyboardMarkup(row_width=2)
btn_yes_1 = types.InlineKeyboardButton(text='Да', callback_data=choice_profile_1.new(action='yes'))
btn_no_1 = types.InlineKeyboardButton(text='Нет', callback_data=choice_profile_1.new(action='no'))
btn_info_1 = types.InlineKeyboardButton(text='Информация', callback_data=choice_profile_1.new(action='info'))
choice_1.add(btn_yes_1, btn_no_1, btn_info_1)


choice_profile_2 = CallbackData('profile_make', 'action')
choice_2 = types.InlineKeyboardMarkup(row_width=2)
btn_yes_2 = types.InlineKeyboardButton(text='Да', callback_data=choice_profile_1.new(action='yes'))
btn_no_2 = types.InlineKeyboardButton(text='Нет', callback_data=choice_profile_1.new(action='no'))
choice_2.add(btn_yes_2, btn_no_2)


def keyboard_public():
    choice_public_data = CallbackData('choice_public', 'action')
    choice_public = types.InlineKeyboardMarkup(row_width=1)
    btn_all = types.InlineKeyboardButton(text='Всем', callback_data=choice_public_data.new(action='all'))
    btn_desider = types.InlineKeyboardButton(text='Решалам', callback_data=choice_public_data.new(action='desider'))
    btn_dunno = types.InlineKeyboardButton(text='Дунникам', callback_data=choice_public_data.new(action='dunno'))
    choice_public.add(btn_all, btn_desider, btn_dunno)
    return choice_public


async def keyboard_with_all_subjects_with_see(all_subjects_list):
    give_all_subjects = CallbackData('give_all_subjects', 'action')
    choice_give_all_subjects = types.InlineKeyboardMarkup(row_width=3)
    btn_see = types.InlineKeyboardButton(text='Информация о предметах',
                                         callback_data=give_all_subjects.new(action='see'))
    choice_give_all_subjects.add(btn_see)
    list_subs_btn = []
    for i in all_subjects_list:
        btn = types.InlineKeyboardButton(text=i, callback_data=give_all_subjects.new(action=i))
        list_subs_btn.append(btn)
    choice_give_all_subjects.add(*list_subs_btn)
    btn_stop = types.InlineKeyboardButton(text='Закончить регистрацию предметов',
                                          callback_data=give_all_subjects.new(action='stop'))
    choice_give_all_subjects.add(btn_stop)
    return choice_give_all_subjects


async def keyboard_with_all_subjects_with_hide(all_subjects_list):
    give_all_subjects = CallbackData('give_all_subjects', 'action')
    choice_give_all_subjects = types.InlineKeyboardMarkup(row_width=3)
    btn_hide = types.InlineKeyboardButton(text='Скрыть информацию',
                                          callback_data=give_all_subjects.new(action='hide'))
    choice_give_all_subjects.add(btn_hide)
    list_subs_btn = []
    for i in all_subjects_list:
        btn = types.InlineKeyboardButton(text=i, callback_data=give_all_subjects.new(action=i))
        list_subs_btn.append(btn)
    choice_give_all_subjects.add(*list_subs_btn)
    btn_stop = types.InlineKeyboardButton(text='Закончить регистрацию предметов',
                                          callback_data=give_all_subjects.new(action='stop'))
    choice_give_all_subjects.add(btn_stop)
    return choice_give_all_subjects


async def subjects_task_with_see(all_subjects_list):
    give_all_subjects_task = CallbackData('all_subjects_task', 'action')
    choice_subjects_task = types.InlineKeyboardMarkup(row_width=3)
    btn_see = types.InlineKeyboardButton(text='Информация о предметах',
                                         callback_data=give_all_subjects_task.new(action='see'))
    choice_subjects_task.add(btn_see)
    list_subs_btn = []
    for i in all_subjects_list:
        btn = types.InlineKeyboardButton(text=i, callback_data=give_all_subjects_task.new(action=i))
        list_subs_btn.append(btn)
    choice_subjects_task.add(*list_subs_btn)
    return choice_subjects_task


async def subjects_task_with_hide(all_subjects_list):
    give_all_subjects_task = CallbackData('all_subjects_task', 'action')
    choice_subjects_task = types.InlineKeyboardMarkup(row_width=3)
    btn_see = types.InlineKeyboardButton(text='Скрыть информацию',
                                         callback_data=give_all_subjects_task.new(action='hide'))
    choice_subjects_task.add(btn_see)
    list_subs_btn = []
    for i in all_subjects_list:
        btn = types.InlineKeyboardButton(text=i, callback_data=give_all_subjects_task.new(action=i))
        list_subs_btn.append(btn)
    choice_subjects_task.add(*list_subs_btn)
    return choice_subjects_task


confirm_task_data = CallbackData('confirm_task_from_user', 'action')
confirm_task = types.InlineKeyboardMarkup(row_width=1)
btn_confirm = types.InlineKeyboardButton(text='Подтвердить', callback_data=confirm_task_data.new(action='yes'))
btn_no_confirm = types.InlineKeyboardButton(text='Изменить задание', callback_data=confirm_task_data.new(action='no'))
btn_stop = types.InlineKeyboardButton(text='Отменить отправку задания',
                                      callback_data=confirm_task_data.new(action='stop'))
confirm_task.add(btn_confirm, btn_no_confirm, btn_stop)


confirm_public_data = CallbackData('confirm_public_from_user', 'action')
confirm_public = types.InlineKeyboardMarkup(row_width=1)
btn_confirm = types.InlineKeyboardButton(text='Подтвердить', callback_data=confirm_public_data.new(action='yes'))
btn_no_confirm = types.InlineKeyboardButton(text='Изменить', callback_data=confirm_public_data.new(action='no'))
btn_stop = types.InlineKeyboardButton(text='Отменить отправку',
                                      callback_data=confirm_public_data.new(action='stop'))
confirm_public.add(btn_confirm, btn_no_confirm, btn_stop)


profile_manage_data = CallbackData('profile_manage', 'action')
key_profile_manage = types.InlineKeyboardMarkup(row_width=1)
btn_make = types.InlineKeyboardButton(text='Изменить профиль', callback_data=profile_manage_data.new(action='make'))
btn_del = types.InlineKeyboardButton(text='Закрыть профиль', callback_data=profile_manage_data.new(action='del'))
# btn_prod = types.InlineKeyboardButton(text='Продлить подписку', callback_data=profile_manage_data.new(action='prod'))
key_profile_manage.add(btn_make, btn_del)


admin_add_new_col_data = CallbackData('admin_add_new_col', 'action')
add_new_col_keyboard = types.InlineKeyboardMarkup(row_width=2)
btn_main_df = types.InlineKeyboardButton(text='main_df', callback_data=admin_add_new_col_data.new(action='main_df'))
btn_subs = types.InlineKeyboardButton(text='sudjects_df', callback_data=admin_add_new_col_data.new(action='sudjects_df'))
btn_stop = types.InlineKeyboardButton(text='Отмена', callback_data=admin_add_new_col_data.new(action='stop'))
add_new_col_keyboard.add(btn_main_df, btn_subs, btn_stop)


async def deciders_answer(id_dunno, message_id):
    deciders_answer_data = CallbackData('deciders_answer_data', 'action', 'dunno', 'task_message')
    key_deciders_answer = types.InlineKeyboardMarkup(row_width=2)
    btn_answer_yes = types.InlineKeyboardButton(text='Откликнуться',
                                                callback_data=deciders_answer_data.new(action='yes',
                                                                                       dunno=id_dunno,
                                                                                       task_message=message_id))
    btn_answer_porblem = types.InlineKeyboardButton(text='Жалоба на контент',
                                                    callback_data=deciders_answer_data.new(action='prob',
                                                                                           dunno=id_dunno,
                                                                                           task_message=message_id))
    key_deciders_answer.add(btn_answer_yes, btn_answer_porblem)
    return key_deciders_answer


async def dunno_answer(id_dunno, message_id):
    dunno_answer_data = CallbackData('dunno_answer_data', 'action', 'dunno', 'task_message')
    key_dunno_answer = types.InlineKeyboardMarkup(row_width=1)
    btn_answer_yes = types.InlineKeyboardButton(text='Выбрать решалу',
                                                callback_data=dunno_answer_data.new(action='yes',
                                                                                    dunno=id_dunno,
                                                                                    task_message=message_id))
    key_dunno_answer.add(btn_answer_yes)
    return key_dunno_answer


async def dunno_clear(id_dunno, message_id):
    dunno_clear_data = CallbackData('dunno_clear_data', 'action', 'dunno', 'task_message')
    key_dunno_answer = types.InlineKeyboardMarkup(row_width=2)
    btn_answer_yes = types.InlineKeyboardButton(text='Да',
                                                callback_data=dunno_clear_data.new(action='yes',
                                                                                    dunno=id_dunno,
                                                                                    task_message=message_id))
    btn_answer_no = types.InlineKeyboardButton(text='Нет',
                                                callback_data=dunno_clear_data.new(action='no',
                                                                                   dunno=id_dunno,
                                                                                   task_message=message_id))
    btn_answer_think = types.InlineKeyboardButton(text='Отменить задание',
                                                callback_data=dunno_clear_data.new(action='think',
                                                                                   dunno=id_dunno,
                                                                                   task_message=message_id))
    key_dunno_answer.add(btn_answer_yes, btn_answer_no, btn_answer_think)
    return key_dunno_answer


async def ban_user(telegarm_id):
    ban_user_data = CallbackData('ban_user_data', 'action', 'id')
    key = types.InlineKeyboardMarkup(row_width=2)
    btn_ban = types.InlineKeyboardButton(text='Бан', callback_data=ban_user_data.new(action='ban', id=telegarm_id))
    key.add(btn_ban)
    btn_ban_30 = types.InlineKeyboardButton(text='Бан 30 минут', callback_data=ban_user_data.new(action='ban_30', id=telegarm_id))
    btn_ban_1 = types.InlineKeyboardButton(text='Бан 1 час', callback_data=ban_user_data.new(action='ban_1', id=telegarm_id))
    btn_ban_1_day = types.InlineKeyboardButton(text='Бан 1 день', callback_data=ban_user_data.new(action='ban_1_day', id=telegarm_id))
    btn_ban_1_week = types.InlineKeyboardButton(text='Бан неделю', callback_data=ban_user_data.new(action='ban_1_week', id=telegarm_id))
    key.add(btn_ban_30, btn_ban_1, btn_ban_1_day, btn_ban_1_week)
    return key


async def no_ban_user(telegarm_id):
    ban_user_data = CallbackData('ban_user_data', 'action', 'id')
    key = types.InlineKeyboardMarkup(row_width=1)
    btn_ban = types.InlineKeyboardButton(text='Разбанить', callback_data=ban_user_data.new(action='noban', id=telegarm_id))
    key.add(btn_ban)
    return key