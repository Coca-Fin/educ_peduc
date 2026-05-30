import json
import logging
import sqlite3
import unittest
import sys
from datetime import datetime
from pathlib import Path
from copy import deepcopy
from dataclasses import FrozenInstanceError

from structs import *
from repositories import UserRepo, MessageChainRepo
from chat import ChatService

#logger section
logs_path = Path(__file__).parent.resolve() / "test_logs.log"
logging.basicConfig(filename=logs_path, level=logging.DEBUG)
logger = logging.getLogger("TEST")

#test constants section
TEST_USER_ID = -1
TEST_CHAIN_ID = -1
TEST_USER_DATA = {"loc": "Ню йорк"}
TEST_CHAIN_DATA = (Message("1", False, 1.0,
                           0), Message("2", False, 2.0,
                                       0), Message("3", False, 3.0, 0))

TEST_MESSAGE_CHAIN = MessageChain(TEST_CHAIN_ID, TEST_USER_ID, 0, TEST_CHAIN_DATA)
TEST_USER_OBJ = UserData(TEST_USER_ID, TEST_USER_DATA, NOT_CONNECTED)


class TestUserRepo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo: UserRepo = UserRepo()

    def setUp(self):
        self.context: UserData = UserData(1111, {"loc": "Лэс энджелс"},
                                          NOT_CONNECTED)

    def tearDown(self):
        self.repo.clear()

    def test_create_user(self):
        """ Сценарий: Сохранение нового пользователя """
        user: UserData | None = self.repo.create(self.context)
        self.assertIsNotNone(user)

        _user: UserData | None = self.repo.find_by_id(self.context.id)
        self.assertIsNotNone(_user)

    def test_retriev_null_user(self):
        """ Сценарий: Получение несуществующего пользователя возвращает None """
        user: UserData | None = self.repo.find_by_id(self.context.id)

        self.assertIsNone(user, f"User is not Nyan... {user}")

    # ✅
    def test_update_user_data(self):
        """ Сценарий: Обновление данных существующего пользователя """
        self.repo.create(self.context)
        self.repo.update_data(self.context.id, TEST_USER_DATA)
        user: UserData | None = self.repo.find_by_id(self.context.id)

        self.assertDictEqual(user.data, TEST_USER_DATA)

    # 🚨 WIU 🚨 WIU 🚨 WIU
    def test_edit_user_data_direct(self):
        """ Сценарий: Обновление данных существующего пользователя """
        # immutable structs can't be changed by direct access
        # if an exception is triggered, then all work is truly
        with self.assertRaises(FrozenInstanceError):
            _user: UserData | None
            user: UserData | None
            user = self.repo.create(self.context)

            user.data = TEST_USER_DATA
            _user = self.repo.find_by_id(self.context.id)

            self.assertNotEqual(user.data, _user.data,
                                "Immutable was violated")

    def test_delete_user(self):
        """ Сценарий: Удаление существующего пользователя """
        self.repo.create(self.context)
        self.repo.delete(self.context.id)

        user: UserData | None = self.repo.find_by_id(self.context.id)

        self.assertIsNone(user)

    def test_user_proximity(self):
        """ Сценарий: Проверка структурного равенства (seq) пользователей """
        user1: UserData = UserData(self.context.id, self.context.data,
                                   NOT_CONNECTED)

        # so, this cant affect to equality, full copy of mem
        user2: UserData = deepcopy(user1)

        self.assertNotEqual(id(user1), id(user2),
                            f"wtf, {id(user1)} ? {id(user2)}")

        self.assertEqual(user1, user2,
                         f"user {user1} is not seq to user {user2}")

    def test_existing_id_change(self):
        """ Сценарий: Смена ID пользователя на существующий """
        self.repo.create(TEST_USER_OBJ)
        self.repo.create(self.context)

        self.assertFalse(self.repo.update_id(self.context.id, TEST_USER_ID))

    def test_change_id(self):
        """ Сценарий: Смена ID пользователя """
        self.repo.create(self.context)

        self.repo.update_id(self.context.id, self.context.id + 1)
        user: UserData | None = self.repo.find_by_id(self.context.id + 1)

        self.assertIsNotNone(user)


class TestChainRepo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo: MessageChainRepo = MessageChainRepo()

    def setUp(self):
        self.init_msg = Message("", False, datetime.now().timestamp(), 0)
        self.context: MessageChain = MessageChain(1111, 0, 0,
                                                  (self.init_msg, ))

    def tearDown(self):
        self.repo.clear()

    def test_create_message_chain(self):
        """ Сценарий: Создание новой пустой цепочки """
        chain_msg: MessageChain | None = self.repo.create(self.context)
        self.assertIsNotNone(chain_msg)

        _chain_msg: MessageChain | None = self.repo.find_by_id(self.context.id)
        self.assertIsNotNone(_chain_msg)

    def test_add_message_in_chain(self):
        """ Сценарий: Добавление сообщения в существующую цепочку """
        chain_msg: MessageChain | None = self.repo.create(self.context)

        self.repo.update_messages(self.context.id, TEST_CHAIN_DATA)
        _chain = self.repo.find_by_id(self.context.id)
        self.assertNotEqual(_chain, chain_msg)

        # its more optimized and take more advantage
        # after chain_msg structure has been created, it has to have 2 references: test scope and inner repo scope
        # when it is deleted, there will be only 1 reference left in this test scope.
        # self.assertEqual(sys.getrefcount(chain_msg), 1)

    def test_chain_order_consistency(self):
        """ Сценарий: Добавление нескольких сообщений сохраняет их порядок """
        self.repo.create(self.context)

        self.repo.update_messages(self.context.id, TEST_CHAIN_DATA)

        _chain = self.repo.find_by_id(self.context.id)
        self.assertEqual(_chain.messages[1:], TEST_CHAIN_DATA)

    def test_delete_message_chain(self):
        """ Сценарий: Удаление цепочки удаляет и все её сообщения (тупой нейросеть думает, что Message тоже хранится) """
        self.repo.create(self.context)

        self.repo.delete(self.context.id)
        _chain: MessageChain | None = self.repo.find_by_id(self.context.id)

        self.assertIsNone(_chain)

    def test_view_all_message_chains(self):
        """ Сценарий: Маппер возвращает все созданные цепочки """
        self.repo.create(self.context)
        self.repo.create(TEST_MESSAGE_CHAIN)
        self.repo.create(self.context.set_id(self.context.id + 1))

        all_chains = []
        for i in (self.context.id, TEST_CHAIN_ID, self.context.id + 1):
            all_chains.append(self.repo.find_by_id(i))

        self.assertEqual(set(self.repo.all()), set(all_chains))


class TestChatService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user_repo: UserRepo = UserRepo()
        cls.chain_repo: MessageChainRepo = MessageChainRepo()
        cls.chat: ChatService = ChatService(cls.user_repo, cls.chain_repo)

        cls.user_ctx = UserData(1, {"loc": "де_мираж"}, NOT_CONNECTED)
        cls.chain_ctx = MessageChain(666, 0, 0,
                                     Message("1000-7", True, 7.77, 0))

    def setUp(self):
        self.user_repo.create(self.user_ctx)
        self.chain_repo.create(self.chain_ctx)

    def tearDown(self):
        self.user_repo.clear()
        self.chain_repo.clear()

    def test_connect(self):
        self.assertEqual(
            self.user_repo.find_by_id(self.user_ctx.id).active_chain,
            NOT_CONNECTED)

        self.assertEqual(
            self.chain_repo.find_by_id(self.chain_ctx.id).user_id, 0)

        self.chat.connect(self.user_ctx.id, self.chain_ctx.id)

        self.assertEqual(
            self.user_repo.find_by_id(self.user_ctx.id).active_chain,
            self.chain_ctx.id)

        self.assertEqual(
            self.chain_repo.find_by_id(self.chain_ctx.id).user_id,
            self.user_ctx.id)

    def test_disconnect(self):
        self.assertEqual(
            self.user_repo.find_by_id(self.user_ctx.id).active_chain,
            NOT_CONNECTED)

        self.assertEqual(
            self.chain_repo.find_by_id(self.chain_ctx.id).user_id, 0)

        self.chat.connect(self.user_ctx.id, self.chain_ctx.id)
        self.chat.connect(self.user_ctx.id, NOT_CONNECTED)

        self.assertEqual(
            self.user_repo.find_by_id(self.user_ctx.id).active_chain,
            NOT_CONNECTED)
        
        # id чата должно соответсоввать первоначальному владельцу
        # Странно было бы, если бы чат можно было захватить)))
        # К вам в чат вторгнулся другой пользователь!!!
        self.assertEqual(
            self.chain_repo.find_by_id(self.chain_ctx.id).user_id, 1)


if __name__ == "__main__":
    """
        1. Подумать о любимом стиле кода, о его эстетике (сейчас полу 
        декларативный + явный, - нет rollback/commit при exception/err)
        2. Сделать weakref для объектов (по желанию)
        3. Паттерн спецификация для поиска по репозиторию
        4. Стоит тщательно перепроектировать, если возникнут задачи:
        а) расширения, б) масштабирования, в) массовые данные (не big 
        data) г) статистика, д) интеграция - это основные признаки
        5. Замена словарей на нормальное безопасное хранилище данных,
        соответствующее MemoryProtocol.
        6. Обновление данных не по отдельным методам, а также со 
        смежным паттерном спецификации, более глобально - это 
        стратегия.
        7. Изучение мест дублирования ссылок на данные, например:
        создание переменной ссылки на значение из репозитория
        в глобальном скопе
    """
    unittest.main()
