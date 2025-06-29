import unittest
from utils import state_manager

class TestStateManager(unittest.TestCase):
    def test_set_and_get_user_state(self):
        user_id = "123"
        state_manager.set_user_state(user_id, {"foo": "bar"}, "test")
        state = state_manager.get_user_state(user_id, "test")
        self.assertEqual(state, {"foo": "bar"})

    def test_delete_user_state(self):
        user_id = "456"
        state_manager.set_user_state(user_id, {"baz": "qux"}, "test")
        state_manager.delete_user_state(user_id, "test")
        state = state_manager.get_user_state(user_id, "test")
        self.assertIsNone(state) 