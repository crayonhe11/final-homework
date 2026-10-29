import unittest
import os
import json

def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_score(scores):
    if not scores:
        return 0
    return sum(scores) / len(scores)

class UserSubmission:
    def __init__(self, user_id, score):
        self.user_id = user_id
        self.score = score

    def is_passed(self, passing_score=60):
        return self.score >= passing_score


class TestHomeworkAssignment(unittest.TestCase):

    def setUp(self):
        """测试前准备：创建临时配置文件和初始数据"""
        self.test_config_path = "config.test.json"
        self.test_data = {"version": "1.0", "env": "testing"}
        with open(self.test_config_path, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f)

    def tearDown(self):
        """测试后清理：删除临时文件"""
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

    # --- 1. 配置加载测试 ---
    def test_load_config_success(self):
        """测试正确加载配置文件"""
        config = load_config(self.test_config_path)
        self.assertEqual(config["version"], "1.0")
        self.assertEqual(config["env"], "testing")

    def test_load_config_not_found(self):
        """测试配置文件不存在时的异常处理"""
        with self.assertRaises(FileNotFoundError):
            load_config("non_existent_config.json")

    # --- 2. 算术/逻辑功能测试 ---
    def test_calculate_score_average(self):
        """测试平均分计算逻辑"""
        scores = [80, 90, 100]
        self.assertAlmostEqual(calculate_score(scores), 90.0)

    def test_calculate_score_empty(self):
        """测试空列表得分计算"""
        self.assertEqual(calculate_score([]), 0)

    # --- 3. 提交与及格判定测试 ---
    def test_submission_passed(self):
        """测试提交成绩及格判定"""
        sub = UserSubmission(user_id=101, score=75)
        self.assertTrue(sub.is_passed(passing_score=60))

    def test_submission_failed(self):
        """测试提交成绩不及格判定"""
        sub = UserSubmission(user_id=102, score=45)
        self.assertFalse(sub.is_passed(passing_score=60))


if __name__ == "__main__":
    unittest.main()