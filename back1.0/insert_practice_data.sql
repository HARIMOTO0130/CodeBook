-- 为练习题 ID 92 插入示例数据
-- 注意：请根据你的实际数据库名称和表结构调整

-- 设置字符集为 UTF-8
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

USE codebook_fixed;

-- 1. 更新 books_practice 表的 questions 字段，添加示例问题
-- 注意：使用 JSON_ARRAY 和 JSON_OBJECT 函数构建 JSON，避免转义问题
UPDATE books_practice 
SET questions = JSON_ARRAY(
    JSON_OBJECT(
        'id', 1,
        'type', 'choice',
        'title', '选择题1',
        'question', '计算机中最小的信息单位是？',
        'stem', '计算机中最小的信息单位是？',
        'content', '计算机中最小的信息单位是？',
        'description', '请选择正确的答案',
        'language', 'python',
        'difficulty', 1,
        'order', 1
    ),
    JSON_OBJECT(
        'id', 2,
        'type', 'true_false',
        'title', '判断题1',
        'question', '计算机的CPU主要由运算器和控制器组成。',
        'stem', '计算机的CPU主要由运算器和控制器组成。',
        'content', '计算机的CPU主要由运算器和控制器组成。',
        'description', '请判断正误',
        'correct_answer', TRUE,
        'language', 'python',
        'difficulty', 1,
        'order', 2
    ),
    JSON_OBJECT(
        'id', 3,
        'type', 'fill_blank',
        'title', '填空题1',
        'question', '请填写：计算机中1KB等于____字节。',
        'stem', '请填写：计算机中1KB等于____字节。',
        'content', '请填写：计算机中1KB等于____字节。',
        'description', '请填写正确答案',
        'language', 'python',
        'difficulty', 2,
        'order', 3
    ),
    JSON_OBJECT(
        'id', 4,
        'type', 'programming',
        'title', '编程题1',
        'question', '编写一个Python函数，计算两个数的和。',
        'stem', '编写一个Python函数，计算两个数的和。',
        'content', '编写一个Python函数，计算两个数的和。函数名为 add，接受两个参数 a 和 b，返回它们的和。',
        'description', '请完成以下编程练习',
        'code_template', CONCAT('def add(a, b):', CHAR(10), '    # 在这里编写你的代码', CHAR(10), '    return a + b'),
        'language', 'python',
        'difficulty', 2,
        'order', 4
    )
)
WHERE id = 92;

-- 2. 插入选择题选项到 books_practicechoiceoption
-- 注意：这些选项对应 questions 数组中的第一个问题（选择题）
INSERT INTO books_practicechoiceoption (practice_id, content, is_correct, `order`) VALUES
(92, '字节(Byte)', 0, 0),
(92, '位(bit)', 1, 1),
(92, '字(Word)', 0, 2),
(92, '双字(Double Word)', 0, 3);

-- 3. 插入填空题空位到 books_practicefillblank
-- 注意：这些空位对应 questions 数组中的第三个问题（填空题）
INSERT INTO books_practicefillblank (practice_id, prompt, placeholder, correct_answer, `order`) VALUES
(92, '请填写：计算机中1KB等于', '____', '1024', 0);

-- 4. 插入测试用例到 books_testcase
-- 注意：这些测试用例对应 questions 数组中的第四个问题（编程题）
INSERT INTO books_testcase (practice_id, input_data, expected_output, `order`) VALUES
(92, JSON_OBJECT('a', 2, 'b', 3), CAST('5' AS JSON), 0),
(92, JSON_OBJECT('a', 10, 'b', 20), CAST('30' AS JSON), 1),
(92, JSON_OBJECT('a', -5, 'b', 5), CAST('0' AS JSON), 2);

-- 验证插入的数据
SELECT 'Practice questions updated' AS status;
SELECT id, title, JSON_LENGTH(questions) AS question_count FROM books_practice WHERE id = 92;
SELECT COUNT(*) AS choice_options_count FROM books_practicechoiceoption WHERE practice_id = 92;
SELECT COUNT(*) AS fill_blanks_count FROM books_practicefillblank WHERE practice_id = 92;
SELECT COUNT(*) AS test_cases_count FROM books_testcase WHERE practice_id = 92;

