from django.core.management.base import BaseCommand
from apps.books.models import Practice, Chapter, Book


class Command(BaseCommand):
    """
    系统性修复 Practice.questions 中不完整或缺失的信息：
    - 确保每道题都有完整的 title / question（题干）/ type / order
    - 补上判断题的题干与正确答案
    - 补上填空题 blanks 中的占位提示
    - 为缺失 question 的记录根据书名/章节名生成描述性题干
    """
    help = "修复练习题 JSON 数据中缺失或不完整的题干/内容"

    def handle(self, *args, **options):
        practices = Practice.objects.select_related("chapter__book").all()
        if not practices.exists():
            self.stdout.write(self.style.WARNING("未找到任何 Practice 记录"))
            return

        fixed_practices = 0
        fixed_questions = 0

        for practice in practices:
            chapter: Chapter = practice.chapter
            book: Book = chapter.book
            changed = False

            questions = practice.questions or []
            if not isinstance(questions, list):
                self.stdout.write(
                    self.style.WARNING(
                        f"[{practice.id}] {practice.title} 的 questions 字段不是数组，跳过"
                    )
                )
                continue

            for idx, q in enumerate(questions):
                if not isinstance(q, dict):
                    continue

                before = q.copy()

                # 题目基础信息
                q.setdefault("id", idx + 1)
                q.setdefault("order", idx + 1)
                q_type = (q.get("type") or "choice").strip()

                # 标题缺失时，用章节名 + 题号补齐
                if not q.get("title"):
                    type_label = {
                        "choice": "选择题",
                        "true_false": "判断题",
                        "fill": "填空题",
                        "code_completion": "代码补全题",
                        "programming": "编程题",
                    }.get(q_type, "练习题")
                    q["title"] = f"{chapter.title} - {type_label}（第{idx + 1}题）"

                # 题干 question 缺失时，根据类型和章节信息补齐
                if not q.get("question"):
                    if q_type == "choice":
                        q["question"] = (
                            f"在《{book.title}》中，关于“{chapter.title}”的描述，以下哪项是正确的？"
                        )
                    elif q_type == "true_false":
                        q["question"] = (
                            f"判断下列关于《{book.title}》“{chapter.title}”内容的说法是否正确。"
                        )
                    elif q_type == "fill":
                        q["question"] = (
                            f"根据《{book.title}》“{chapter.title}”的内容，完成下面的填空。"
                        )
                    elif q_type == "code_completion":
                        q["question"] = (
                            f"补全代码，实现本章“{chapter.title}”中的核心示例功能。"
                        )
                    elif q_type == "programming":
                        q["question"] = (
                            f"结合《{book.title}》“{chapter.title}”的知识，完成下列编程任务。"
                        )

                # 判断题：如果只有布尔 correct_answer，没有 options，则构造“正确/错误”选项
                if q_type == "true_false":
                    if "correct_answer" not in q:
                        # 没有显式答案时，默认认为陈述为“正确”
                        q["correct_answer"] = True
                    if not q.get("options"):
                        q["options"] = [
                            {"id": 1, "content": "正确", "is_correct": bool(q["correct_answer"])},
                            {"id": 2, "content": "错误", "is_correct": not bool(q["correct_answer"])},
                        ]

                # 填空题：补齐 blanks 中的 prompt / placeholder
                if q_type == "fill" and isinstance(q.get("blanks"), list):
                    for b_index, blank in enumerate(q["blanks"]):
                        if not isinstance(blank, dict):
                            continue
                        blank.setdefault("id", b_index + 1)
                        # 正确答案字段统一为 correct_answer
                        if "correct_answer" not in blank and "correctAnswer" in blank:
                            blank["correct_answer"] = blank["correctAnswer"]
                        blank.setdefault("prompt", f"第 {b_index + 1} 空")
                        blank.setdefault("placeholder", "请输入答案")

                if q != before:
                    changed = True
                    fixed_questions += 1

            if changed:
                practice.questions = questions
                practice.save(update_fields=["questions", "updated_at"])
                fixed_practices += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"已修复练习题集 [{practice.id}] {practice.title} 的题目数据"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"修复完成：共更新 {fixed_practices} 个练习题集，修复 {fixed_questions} 道题目。"
            )
        )


