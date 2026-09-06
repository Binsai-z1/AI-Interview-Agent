import json
import unittest
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from app.tools.question_tool import QUESTION_DATA_PATH, QuestionBank, get_interview_question


class QuestionBankTests(unittest.TestCase):
    def test_catalog_has_balanced_coverage(self):
        payload = json.loads(QUESTION_DATA_PATH.read_text(encoding="utf-8"))
        questions = payload["questions"]
        self.assertEqual(len(questions), 99)

        topics = {question["topic"] for question in questions}
        self.assertEqual(len(topics), 11)
        distribution = Counter((question["topic"], question["difficulty"]) for question in questions)
        self.assertTrue(all(count == 3 for count in distribution.values()))

    def test_filters_are_case_insensitive_and_exclusions_are_strict(self):
        bank = QuestionBank(chooser=lambda candidates: candidates[-1])
        selected = bank.get_question(topic="rag", difficulty="medium")
        self.assertIsNotNone(selected)
        self.assertEqual(selected.topic, "RAG")
        self.assertEqual(selected.difficulty, "medium")

        remaining = bank.get_question(
            topic="RAG",
            difficulty="medium",
            excluded_questions=[question.question for question in bank.questions if question.topic == "RAG" and question.difficulty == "medium"],
        )
        self.assertIsNone(remaining)

    def test_selection_uses_configured_random_chooser_not_first_candidate(self):
        bank = QuestionBank(chooser=lambda candidates: candidates[-1])
        candidates = [question for question in bank.questions if question.topic == "RAG"]
        self.assertEqual(bank.get_question(topic="RAG"), candidates[-1])

    def test_data_validation_rejects_invalid_difficulty(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "questions.json"
            path.write_text(json.dumps([{"question": "q", "topic": "t", "difficulty": "unknown"}]), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "unsupported difficulty"):
                QuestionBank(path)

    def test_public_api_reports_exhausted_candidates(self):
        rag_easy = [question.question for question in QuestionBank().questions if question.topic == "RAG" and question.difficulty == "easy"]
        result = get_interview_question("RAG", "easy", rag_easy)
        self.assertEqual(result["found"], False)
        self.assertIsNone(result["question"])


if __name__ == "__main__":
    unittest.main()
