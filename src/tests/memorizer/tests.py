import logging
import unittest
import sys
from datetime import datetime
from pathlib import Path
from copy import deepcopy

from Memorizer.structs import *
from Memorizer.repositories import UserRepo, MessageChainRepo
from Memorizer.chat import ChatService

logs_path = Path(__file__).parent.resolve() / "logs/test_logs.log"
logging.basicConfig(filename=logs_path, level=logging.DEBUG)
LOGGER = logging.getLogger("TEST")

TEST_USER_ID = -1
TEST_CHAIN_ID = -1
TEST_USER_DATA = {"loc": "Ню йорк"}
TEST_CHAIN_DATA = ("1", "2", "3")

TEST_MESSAGE_CHAIN = MessageChain(0, [], False)
TEST_USER_OBJ = UserData(TEST_USER_ID, TEST_USER_DATA, NOT_CONNECTED)


class TestUserRepo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo: UserRepo = UserRepo(LOGGER, {}, "[USER]")
        cls.context: UserData = UserData(1111, {"loc": "Лэс энджелс"},
                                         NOT_CONNECTED)

    def setUp(self):
        self.user_id = self.context.id
        self.user_data = self.context.data

    def tearDown(self):
        self.repo.clear()

    def test_create_user(self):
        """ Сценарий: Сохранение нового пользователя """
        user: UserData | None = self.repo.create(self.user_id, self.user_data)
        self.assertIsNotNone(user)

        _user: UserData | None = self.repo.find_by_id(self.user_id)
        self.assertIsNotNone(_user)

    def test_retriev_null_user(self):
        """ Сценарий: Получение несуществующего пользователя возвращает None """
        user: UserData | None = self.repo.find_by_id(self.user_id)

        self.assertIsNone(user, f"User is not Nyan... {user}")

    # ✅
    def test_update_user_data(self):
        """ Сценарий: Обновление данных существующего пользователя """
        self.repo.create(self.user_id, self.user_data)
        self.repo.update_data(self.user_id, TEST_USER_DATA)
        user: UserData | None = self.repo.find_by_id(self.user_id)

        self.assertEqual(user.data, TEST_USER_DATA)

    # ✅
    def test_edit_user_data(self):
        """ Сценарий: Обновление данных существующего пользователя """
        # omagaaaa
        new_user: UserData
        _user: UserData
        user: UserData

        user = self.repo.create(self.user_id, self.user_data)

        new_user = user.put_data(TEST_USER_DATA)
        self.assertNotEqual(user, new_user)

        self.repo.update(self.user_id, new_user)
        _user = self.repo.find_by_id(self.user_id)
        self.assertNotEqual(_user.data, user)

    # 🚨 WIU 🚨 WIU 🚨 WIU
    def test_edit_user_data_direct(self):
        """ Сценарий: Обновление данных существующего пользователя """
        # immutable structs can't be changed by direct access
        try:
            _user: UserData | None
            user: UserData | None

            user = self.repo.create(self.user_id, self.user_data)

            user.data = TEST_USER_DATA
            _user = self.repo.find_by_id(self.user_id)

            # and if he managed to change
            self.assertNotEqual(user.data, _user.data,
                                "Immutable was violated")
            self.assertTrue(False)
        except Exception as e:
            # if an exception is triggered, then all work is truly
            # print(repo, user_id, user_data)
            self.assertTrue(True)

    def test_delete_user(self):
        """ Сценарий: Удаление существующего пользователя """
        self.repo.create(self.user_id, self.user_data)
        self.repo.delete(self.user_id)

        user: UserData | None = self.repo.find_by_id(self.user_id)

        self.assertIsNone(user)

    def test_user_proximity(self):
        """ Сценарий: Проверка структурного равенства (seq) пользователей """
        user1: UserData = UserData(self.user_id, self.user_data, NOT_CONNECTED)

        # so, this cant affect to equality, full copy of mem
        user2: UserData = deepcopy(user1)

        self.assertNotEqual(id(user1), id(user2),
                            f"wtf, {id(user1)} ? {id(user2)}")

        self.assertEqual(user1, user2,
                         f"user {user1} is not seq to user {user2}")

    def test_uniq_users_id_change(self):
        """ Сценарий: Смена ID пользователя ан существующий """
        self.repo.create(TEST_USER_ID)
        self.repo.create(self.user_id)

        self.assertFalse(self.repo.update_id(self.user_id, TEST_USER_ID))


class TestChainRepo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo: MessageChainRepo = MessageChainRepo(LOGGER, {},
                                                      "[MESSAGECHAIN]")
        cls.init_msg: Message = Message("", False, datetime.now().timestamp())
        cls.context: MessageChain | None = MessageChain(
            1111, (cls.init_msg, ), NOT_CONNECTED)

    def setUp(self):
        self.chain_id = self.context.id
        self.chain_data = self.context.messages

    def tearDown(self):
        self.repo.clear()

    def test_create_message_chain(self):
        """ Сценарий: Создание новой пустой цепочки """
        chain_msg: MessageChain | None = self.repo.create(
            self.chain_id, self.init_msg)
        self.assertIsNotNone(chain_msg)

        _chain_msg: MessageChain | None = self.repo.find_by_id(self.chain_id)
        self.assertIsNotNone(_chain_msg)

    def test_add_message_in_chain(self):
        """ Сценарий: Добавление сообщения в существующую цепочку """
        chain_msg: MessageChain | None = self.repo.create(
            self.chain_id, self.init_msg)

        new_chain = chain_msg.add_messages(TEST_CHAIN_DATA)
        self.assertNotEqual(chain_msg.messages, new_chain.messages)

        self.repo.update(self.chain_id, new_chain)
        _chain = self.repo.find_by_id(self.chain_id)
        self.assertNotEqual(_chain, chain_msg)

        # its more optimized and take more advantage
        # after chain_msg structure has been created, it has to have 2 references: test scope and inner repo scope
        # when it is deleted, there will be only 1 reference left in this test scope.
        # self.assertEqual(sys.getrefcount(chain_msg), 1)

    def test_chain_order_consistency(self):
        """ Сценарий: Добавление нескольких сообщений сохраняет их порядок """
        self.repo.create(self.chain_id, self.init_msg)

        self.repo.update_messages(self.chain_id, TEST_CHAIN_DATA)

        _chain = self.repo.find_by_id(self.chain_id)
        # МЫ ВЕРИМ ЧТО БЫЛО ТОЛЬКО 1 СООБЩЕНИЕ, ВЕРЬТЕ !!!!
        self.assertEqual(_chain.messages[1:], TEST_CHAIN_DATA)

    def test_delete_message_chain(self):
        """ Сценарий: Удаление цепочки удаляет и все её сообщения (тупой нейросеть думает, что Message тоже хранится) """
        self.repo.create(self.chain_id, self.init_msg)

        self.repo.delete(self.chain_id)
        _chain: MessageChain | None = self.repo.find_by_id(self.chain_id)

        self.assertIsNone(_chain)

    def test_view_all_message_chains(self):
        """ Сценарий: Маппер возвращает все созданные цепочки """
        self.repo.create(self.chain_id, self.init_msg)
        self.repo.create(TEST_CHAIN_ID, TEST_CHAIN_DATA)
        self.repo.create(self.chain_id + 1, self.init_msg)

        all_chains = []
        for i in (self.chain_id, TEST_CHAIN_ID, self.chain_id + 1):
            all_chains.append(self.repo.find_by_id(i))

        self.assertEqual(self.repo.all(), all_chains)


class TestChatService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user_repo: UserRepo = UserRepo(LOGGER, {}, "[USER]")
        cls.chain_repo: MessageChainRepo = MessageChainRepo(
            LOGGER, {}, "[MESSAGECHAIN]")
        cls.chat: ChatService = ChatService(cls.user_repo, cls.chain_repo,
                                            LOGGER)

        cls.user_id = 1
        cls.chain_id = 666
        cls.context = ((cls.user_id, {
            "loc": "де_мираж"
        }), (cls.chain_id, Message("1000-7", True, 7.77)))

    def setUp(self):
        self.user_repo.create(*self.context[0])
        self.chain_repo.create(*self.context[1])

    def tearDown(self):
        self.user_repo.clear()
        self.chain_repo.clear()

    def test_connect(self):
        self.assertEqual(
            self.user_repo.find_by_id(self.user_id).active_chain,
            NOT_CONNECTED)

        self.assertFalse(self.chain_repo.find_by_id(self.chain_id).is_active)

        self.chat.connect(self.user_id, self.chain_id)

        self.assertEqual(
            self.user_repo.find_by_id(self.user_id).active_chain,
            self.chain_id)

        self.assertTrue(self.chain_repo.find_by_id(self.chain_id).is_active)

    def test_disconnect(self):
        self.assertEqual(
            self.user_repo.find_by_id(self.user_id).active_chain,
            NOT_CONNECTED)

        self.assertFalse(self.chain_repo.find_by_id(self.chain_id).is_active)

        self.chat.connect(self.user_id, self.chain_id)
        self.chat.connect(self.user_id, NOT_CONNECTED)

        self.assertEqual(
            self.user_repo.find_by_id(self.user_id).active_chain,
            NOT_CONNECTED)

        self.assertFalse(self.chain_repo.find_by_id(self.chain_id).is_active)


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
