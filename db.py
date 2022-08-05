import config
import sqlite3
import itertools
import datetime


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.name_db = db_file
        ban_users = self.cursor.execute("SELECT `telegram_id` FROM `user` WHERE `ban` = True")
        self.ban_users_list = [x[0] for x in ban_users.fetchall()]
        self.to_do = {}
        self.activity_users_dict = {'send': 0, 'close': 0, 'cancel': 0, 'no close': 0}
        self.session_date = datetime.datetime.now(tz=config.tz).date()

    def user_exists(self, user_id):
        """Проверяем, есть ли пользователь БД True/False"""
        result = self.cursor.execute("SELECT `id` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def decider_exists(self, user_id):
        """Проверяем, есть ли решала в БД True/False"""
        result = self.cursor.execute("SELECT `id` FROM `user` WHERE `telegram_id` = ? AND `decider` = True", (user_id,))
        return bool(len(result.fetchall()))

    def dunno_exists(self, user_id):
        """Проверяем, есть ли незнала в БД True/False"""
        result = self.cursor.execute("SELECT `id` FROM `user` WHERE `telegram_id` = ? AND `dunno` = True", (user_id,))
        return bool(len(result.fetchall()))

    def ban_list(self):
        """ Достает список забанненых пользователей """
        result = self.cursor.execute("SELECT `telegram_id` FROM `user` WHERE `ban` = False")
        return [x[0] for x in result.fetchall()]

    def all_list(self):
        """ Достает список всех пользователей """
        result = self.cursor.execute("SELECT `telegram_id` FROM `user`")
        return [x[0] for x in result.fetchall()]

    def ban(self, user_id, yes=False, no=False):
        """ Бан или разбан по id """
        if yes:
            self.cursor.execute('UPDATE user SET ban = True WHERE telegram_id = ?', (user_id,))
        elif no:
            self.cursor.execute('UPDATE user SET ban = False WHERE telegram_id = ?', (user_id,))

        ban_users = (self.cursor.execute("SELECT `telegram_id` FROM `user` WHERE `ban` = True"))
        self.ban_users_list = [x[0] for x in ban_users.fetchall()]

        return self.conn.commit()

    def new_row_user_db(self, user_id, name):
        """Добавляем юзера в таблицу user"""
        self.cursor.execute("INSERT INTO `user` (`telegram_id`, `name`) VALUES (?, ?)",
                            (user_id, name,))
        return self.conn.commit()

    def new_row_subject_db(self, user_id, *subjects):
        """Добавляем юзера в таблицу subject; принимает telegram_id и *[предметы]"""
        self.cursor.execute(f"INSERT INTO `subject` {('telegram_id', *subjects)} VALUES {(user_id, *[True for i in subjects])}")
        return self.conn.commit()

    def backup(self):
        backup_con = sqlite3.connect('backup_db.db')
        try:
            with backup_con:
                self.conn.backup(backup_con, pages=3)
            mess = True
        except sqlite3.Error as error:
            mess = error
        finally:
            if (backup_con):
                backup_con.close()
        return mess

    def get_user_id(self, user_id):
        """ Достаем id юзера в базе по его user_id """
        result = self.cursor.execute("SELECT `id` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        return result.fetchone()[0]

    def get_user_name(self, user_id):
        """ Выдает имя пользователя по user_id """
        result = self.cursor.execute("SELECT `name` FROM `user` WHERE `telegram_id` = ?", (user_id,))
        return result.fetchone()[0]

    def get_user_info(self, user_id):
        """ Возваращет словарь с профилем и список предметов """
        user_dict = {'name': (self.cursor.execute('SELECT `name` FROM `user` WHERE telegram_id = ?', (user_id,))).fetchall()[0][0],
                     'username': (self.cursor.execute('SELECT `username` FROM `user` WHERE telegram_id = ?', (user_id,))).fetchall()[0][0],
                     'univer': (self.cursor.execute('SELECT `univer` FROM `user` WHERE telegram_id = ?', (user_id,))).fetchall()[0][0]}
        list_sub = []
        for i in config.all_subjects[1:]:
            res = (self.cursor.execute(f'SELECT `{i}` FROM `subject` WHERE telegram_id = ?', (user_id,))).fetchall()[0][0]
            if res == 1:
                list_sub.append(i)

        return user_dict, list_sub

    def get_list_desiders(self, sub):
        """ Выдаёт списко решал по заданному предмету """
        res = self.cursor.execute(f'SELECT `telegram_id` FROM subject WHERE {sub} = True')
        return [x[0] for x in res.fetchall()]

    def get_list_users_id(self):
        """ Выдаёт списко telegram_id всех пользователей """
        res = self.cursor.execute(f'SELECT `telegram_id` FROM user')
        return [x[0] for x in res.fetchall()]

    def get_profile_id(self, user_id):
        res = self.cursor.execute(f'SELECT `profile_id` FROM user WHERE telegram_id = {user_id}')
        return res.fetchall()[0][0]

    def get_count_referals(self, user_id):
        return self.cursor.execute('SELECT COUNT(`id`) as count FROM `user` WHERE `refer_id` = ?', (user_id, )).fetchone()[0]

    def delete_user(self, user_id, user=False, sub=False):
        """ Удаление по id """
        if user:
            self.cursor.execute(f"DELETE FROM user WHERE telegram_id = {user_id}")
        if sub:
            self.cursor.execute(f"DELETE FROM subject WHERE telegram_id = {user_id}")
        return self.conn.commit()

    def update_in_user(self, user_id, dict_values):
        """ Изменяет значения в user по id; принимает словарь """
        for i in dict_values:
            self.cursor.execute(f'UPDATE user SET {i} = ? WHERE telegram_id = ?',
                                (dict_values[i], user_id, ))
        return self.conn.commit()

    def update_in_subject(self, user_id, dict_values):
        """ Изменяет значения в subject по id; принимает словарь """
        for i in dict_values:
            self.cursor.execute(f'UPDATE subject SET {i} = {dict_values[i]} WHERE telegram_id = {user_id}')
        return self.conn.commit()

    def statistic(self):
        """Выдает статистику по всем таблицам"""
        d = {}
        res = self.cursor.execute('SELECT COUNT(*) FROM `user`')
        d['all_users'] = res.fetchall()[0][0]
        mess = f'Всего: {d["all_users"]}\n'
        # for i in ['decider', 'dunno', 'ban']:
        #     res = self.cursor.execute(f'SELECT COUNT(*) FROM `user` WHERE {i} = True')
        #     mess += f'{i}: {res.fetchall()[0][0]}\n'
        res_decider = self.cursor.execute(f'SELECT COUNT(*) FROM `user` WHERE `decider` = True')
        d['decider'] = res_decider.fetchall()[0][0]
        res_ban = self.cursor.execute(f'SELECT COUNT(*) FROM `user` WHERE `ban` = True')
        d['ban'] = res_ban.fetchall()[0][0]
        mess += f'Решалы: {d["decider"]}\n' \
                f'Дунники: {int(d["all_users"]) - int(d["decider"])}\n' \
                f'Бан: {d["ban"]}\n'
        mess += '\n'
        for i in config.all_subjects[1:]:
            res = self.cursor.execute(f'SELECT COUNT(*) FROM `subject` WHERE {i} = True')
            mess += f'{i}: {res.fetchall()[0][0]}\n'
        mess += '\n'
        for i in self.activity_users_dict:
            mess += f'{i}: {self.activity_users_dict[i]} \n'
        mess += f'Начало работы: \n' \
                f'{self.session_date}'
        return mess

    def close(self):
        """ Закрываем соединение с БД """
        self.conn.close()

    def connect(self):
        """ Подключаемся к БД """
        self.conn = sqlite3.connect(self.name_db)
        self.cursor = self.conn.cursor()




