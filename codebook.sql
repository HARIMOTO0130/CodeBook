/*
Navicat MySQL Data Transfer

Source Server         : localhost_3306
Source Server Version : 80016
Source Host           : localhost:3306
Source Database       : codebook

Target Server Type    : MYSQL
Target Server Version : 80016
File Encoding         : 65001

Date: 2026-01-05 17:09:00
*/

SET FOREIGN_KEY_CHECKS=0;
-- ----------------------------
-- Table structure for `authtoken_token`
-- ----------------------------
DROP TABLE IF EXISTS `authtoken_token`;
CREATE TABLE `authtoken_token` (
  `key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_35299eff_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of authtoken_token
-- ----------------------------
INSERT INTO authtoken_token VALUES ('078c938d74d80976d26027b6af8d5762b0a84e84', '2026-01-05 09:04:53.412421', '2');

-- ----------------------------
-- Table structure for `auth_group`
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of auth_group
-- ----------------------------

-- ----------------------------
-- Table structure for `auth_group_permissions`
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of auth_group_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for `auth_permission`
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=181 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of auth_permission
-- ----------------------------
INSERT INTO auth_permission VALUES ('1', 'Can add log entry', '1', 'add_logentry');
INSERT INTO auth_permission VALUES ('2', 'Can change log entry', '1', 'change_logentry');
INSERT INTO auth_permission VALUES ('3', 'Can delete log entry', '1', 'delete_logentry');
INSERT INTO auth_permission VALUES ('4', 'Can view log entry', '1', 'view_logentry');
INSERT INTO auth_permission VALUES ('5', 'Can add permission', '2', 'add_permission');
INSERT INTO auth_permission VALUES ('6', 'Can change permission', '2', 'change_permission');
INSERT INTO auth_permission VALUES ('7', 'Can delete permission', '2', 'delete_permission');
INSERT INTO auth_permission VALUES ('8', 'Can view permission', '2', 'view_permission');
INSERT INTO auth_permission VALUES ('9', 'Can add group', '3', 'add_group');
INSERT INTO auth_permission VALUES ('10', 'Can change group', '3', 'change_group');
INSERT INTO auth_permission VALUES ('11', 'Can delete group', '3', 'delete_group');
INSERT INTO auth_permission VALUES ('12', 'Can view group', '3', 'view_group');
INSERT INTO auth_permission VALUES ('13', 'Can add content type', '4', 'add_contenttype');
INSERT INTO auth_permission VALUES ('14', 'Can change content type', '4', 'change_contenttype');
INSERT INTO auth_permission VALUES ('15', 'Can delete content type', '4', 'delete_contenttype');
INSERT INTO auth_permission VALUES ('16', 'Can view content type', '4', 'view_contenttype');
INSERT INTO auth_permission VALUES ('17', 'Can add session', '5', 'add_session');
INSERT INTO auth_permission VALUES ('18', 'Can change session', '5', 'change_session');
INSERT INTO auth_permission VALUES ('19', 'Can delete session', '5', 'delete_session');
INSERT INTO auth_permission VALUES ('20', 'Can view session', '5', 'view_session');
INSERT INTO auth_permission VALUES ('21', 'Can add Token', '6', 'add_token');
INSERT INTO auth_permission VALUES ('22', 'Can change Token', '6', 'change_token');
INSERT INTO auth_permission VALUES ('23', 'Can delete Token', '6', 'delete_token');
INSERT INTO auth_permission VALUES ('24', 'Can view Token', '6', 'view_token');
INSERT INTO auth_permission VALUES ('25', 'Can add token', '7', 'add_tokenproxy');
INSERT INTO auth_permission VALUES ('26', 'Can change token', '7', 'change_tokenproxy');
INSERT INTO auth_permission VALUES ('27', 'Can delete token', '7', 'delete_tokenproxy');
INSERT INTO auth_permission VALUES ('28', 'Can view token', '7', 'view_tokenproxy');
INSERT INTO auth_permission VALUES ('29', 'Can add 用户', '8', 'add_user');
INSERT INTO auth_permission VALUES ('30', 'Can change 用户', '8', 'change_user');
INSERT INTO auth_permission VALUES ('31', 'Can delete 用户', '8', 'delete_user');
INSERT INTO auth_permission VALUES ('32', 'Can view 用户', '8', 'view_user');
INSERT INTO auth_permission VALUES ('33', 'Can add 用户偏好设置', '9', 'add_userpreferences');
INSERT INTO auth_permission VALUES ('34', 'Can change 用户偏好设置', '9', 'change_userpreferences');
INSERT INTO auth_permission VALUES ('35', 'Can delete 用户偏好设置', '9', 'delete_userpreferences');
INSERT INTO auth_permission VALUES ('36', 'Can view 用户偏好设置', '9', 'view_userpreferences');
INSERT INTO auth_permission VALUES ('37', 'Can add 教材', '10', 'add_book');
INSERT INTO auth_permission VALUES ('38', 'Can change 教材', '10', 'change_book');
INSERT INTO auth_permission VALUES ('39', 'Can delete 教材', '10', 'delete_book');
INSERT INTO auth_permission VALUES ('40', 'Can view 教材', '10', 'view_book');
INSERT INTO auth_permission VALUES ('41', 'Can add 章节', '11', 'add_chapter');
INSERT INTO auth_permission VALUES ('42', 'Can change 章节', '11', 'change_chapter');
INSERT INTO auth_permission VALUES ('43', 'Can delete 章节', '11', 'delete_chapter');
INSERT INTO auth_permission VALUES ('44', 'Can view 章节', '11', 'view_chapter');
INSERT INTO auth_permission VALUES ('45', 'Can add 练习题', '12', 'add_practice');
INSERT INTO auth_permission VALUES ('46', 'Can change 练习题', '12', 'change_practice');
INSERT INTO auth_permission VALUES ('47', 'Can delete 练习题', '12', 'delete_practice');
INSERT INTO auth_permission VALUES ('48', 'Can view 练习题', '12', 'view_practice');
INSERT INTO auth_permission VALUES ('49', 'Can add 测试用例', '13', 'add_testcase');
INSERT INTO auth_permission VALUES ('50', 'Can change 测试用例', '13', 'change_testcase');
INSERT INTO auth_permission VALUES ('51', 'Can delete 测试用例', '13', 'delete_testcase');
INSERT INTO auth_permission VALUES ('52', 'Can view 测试用例', '13', 'view_testcase');
INSERT INTO auth_permission VALUES ('53', 'Can add Jupyter单元格', '14', 'add_jupytercell');
INSERT INTO auth_permission VALUES ('54', 'Can change Jupyter单元格', '14', 'change_jupytercell');
INSERT INTO auth_permission VALUES ('55', 'Can delete Jupyter单元格', '14', 'delete_jupytercell');
INSERT INTO auth_permission VALUES ('56', 'Can view Jupyter单元格', '14', 'view_jupytercell');
INSERT INTO auth_permission VALUES ('57', 'Can add Jupyter输出', '15', 'add_jupyteroutput');
INSERT INTO auth_permission VALUES ('58', 'Can change Jupyter输出', '15', 'change_jupyteroutput');
INSERT INTO auth_permission VALUES ('59', 'Can delete Jupyter输出', '15', 'delete_jupyteroutput');
INSERT INTO auth_permission VALUES ('60', 'Can view Jupyter输出', '15', 'view_jupyteroutput');
INSERT INTO auth_permission VALUES ('61', 'Can add Jupyter笔记本', '16', 'add_jupyternotebook');
INSERT INTO auth_permission VALUES ('62', 'Can change Jupyter笔记本', '16', 'change_jupyternotebook');
INSERT INTO auth_permission VALUES ('63', 'Can delete Jupyter笔记本', '16', 'delete_jupyternotebook');
INSERT INTO auth_permission VALUES ('64', 'Can view Jupyter笔记本', '16', 'view_jupyternotebook');
INSERT INTO auth_permission VALUES ('65', 'Can add 选择题选项', '17', 'add_practicechoiceoption');
INSERT INTO auth_permission VALUES ('66', 'Can change 选择题选项', '17', 'change_practicechoiceoption');
INSERT INTO auth_permission VALUES ('67', 'Can delete 选择题选项', '17', 'delete_practicechoiceoption');
INSERT INTO auth_permission VALUES ('68', 'Can view 选择题选项', '17', 'view_practicechoiceoption');
INSERT INTO auth_permission VALUES ('69', 'Can add 填空题空位', '18', 'add_practicefillblank');
INSERT INTO auth_permission VALUES ('70', 'Can change 填空题空位', '18', 'change_practicefillblank');
INSERT INTO auth_permission VALUES ('71', 'Can delete 填空题空位', '18', 'delete_practicefillblank');
INSERT INTO auth_permission VALUES ('72', 'Can view 填空题空位', '18', 'view_practicefillblank');
INSERT INTO auth_permission VALUES ('73', 'Can add 学习热力图数据', '19', 'add_heatmapdata');
INSERT INTO auth_permission VALUES ('74', 'Can change 学习热力图数据', '19', 'change_heatmapdata');
INSERT INTO auth_permission VALUES ('75', 'Can delete 学习热力图数据', '19', 'delete_heatmapdata');
INSERT INTO auth_permission VALUES ('76', 'Can view 学习热力图数据', '19', 'view_heatmapdata');
INSERT INTO auth_permission VALUES ('77', 'Can add 学习记录', '20', 'add_learningrecord');
INSERT INTO auth_permission VALUES ('78', 'Can change 学习记录', '20', 'change_learningrecord');
INSERT INTO auth_permission VALUES ('79', 'Can delete 学习记录', '20', 'delete_learningrecord');
INSERT INTO auth_permission VALUES ('80', 'Can view 学习记录', '20', 'view_learningrecord');
INSERT INTO auth_permission VALUES ('81', 'Can add 练习记录', '21', 'add_practicerecord');
INSERT INTO auth_permission VALUES ('82', 'Can change 练习记录', '21', 'change_practicerecord');
INSERT INTO auth_permission VALUES ('83', 'Can delete 练习记录', '21', 'delete_practicerecord');
INSERT INTO auth_permission VALUES ('84', 'Can view 练习记录', '21', 'view_practicerecord');
INSERT INTO auth_permission VALUES ('85', 'Can add 错题', '22', 'add_wrongquestion');
INSERT INTO auth_permission VALUES ('86', 'Can change 错题', '22', 'change_wrongquestion');
INSERT INTO auth_permission VALUES ('87', 'Can delete 错题', '22', 'delete_wrongquestion');
INSERT INTO auth_permission VALUES ('88', 'Can view 错题', '22', 'view_wrongquestion');
INSERT INTO auth_permission VALUES ('89', 'Can add 路线图阶段', '23', 'add_roadmapstage');
INSERT INTO auth_permission VALUES ('90', 'Can change 路线图阶段', '23', 'change_roadmapstage');
INSERT INTO auth_permission VALUES ('91', 'Can delete 路线图阶段', '23', 'delete_roadmapstage');
INSERT INTO auth_permission VALUES ('92', 'Can view 路线图阶段', '23', 'view_roadmapstage');
INSERT INTO auth_permission VALUES ('93', 'Can add 路线图模板', '24', 'add_roadmaptemplate');
INSERT INTO auth_permission VALUES ('94', 'Can change 路线图模板', '24', 'change_roadmaptemplate');
INSERT INTO auth_permission VALUES ('95', 'Can delete 路线图模板', '24', 'delete_roadmaptemplate');
INSERT INTO auth_permission VALUES ('96', 'Can view 路线图模板', '24', 'view_roadmaptemplate');
INSERT INTO auth_permission VALUES ('97', 'Can add 用户学习路径', '25', 'add_userlearningpath');
INSERT INTO auth_permission VALUES ('98', 'Can change 用户学习路径', '25', 'change_userlearningpath');
INSERT INTO auth_permission VALUES ('99', 'Can delete 用户学习路径', '25', 'delete_userlearningpath');
INSERT INTO auth_permission VALUES ('100', 'Can view 用户学习路径', '25', 'view_userlearningpath');
INSERT INTO auth_permission VALUES ('101', 'Can add 路线图书籍', '26', 'add_roadmapbook');
INSERT INTO auth_permission VALUES ('102', 'Can change 路线图书籍', '26', 'change_roadmapbook');
INSERT INTO auth_permission VALUES ('103', 'Can delete 路线图书籍', '26', 'delete_roadmapbook');
INSERT INTO auth_permission VALUES ('104', 'Can view 路线图书籍', '26', 'view_roadmapbook');
INSERT INTO auth_permission VALUES ('105', 'Can add 用户路径阶段', '27', 'add_userpathstage');
INSERT INTO auth_permission VALUES ('106', 'Can change 用户路径阶段', '27', 'change_userpathstage');
INSERT INTO auth_permission VALUES ('107', 'Can delete 用户路径阶段', '27', 'delete_userpathstage');
INSERT INTO auth_permission VALUES ('108', 'Can view 用户路径阶段', '27', 'view_userpathstage');
INSERT INTO auth_permission VALUES ('109', 'Can add 笔记', '28', 'add_note');
INSERT INTO auth_permission VALUES ('110', 'Can change 笔记', '28', 'change_note');
INSERT INTO auth_permission VALUES ('111', 'Can delete 笔记', '28', 'delete_note');
INSERT INTO auth_permission VALUES ('112', 'Can view 笔记', '28', 'view_note');
INSERT INTO auth_permission VALUES ('113', 'Can add 练习题', '29', 'add_exercise');
INSERT INTO auth_permission VALUES ('114', 'Can change 练习题', '29', 'change_exercise');
INSERT INTO auth_permission VALUES ('115', 'Can delete 练习题', '29', 'delete_exercise');
INSERT INTO auth_permission VALUES ('116', 'Can view 练习题', '29', 'view_exercise');
INSERT INTO auth_permission VALUES ('117', 'Can add 练习题记录', '30', 'add_exerciserecord');
INSERT INTO auth_permission VALUES ('118', 'Can change 练习题记录', '30', 'change_exerciserecord');
INSERT INTO auth_permission VALUES ('119', 'Can delete 练习题记录', '30', 'delete_exerciserecord');
INSERT INTO auth_permission VALUES ('120', 'Can view 练习题记录', '30', 'view_exerciserecord');
INSERT INTO auth_permission VALUES ('121', 'Can add 练习题测试用例', '31', 'add_exercisetestcase');
INSERT INTO auth_permission VALUES ('122', 'Can change 练习题测试用例', '31', 'change_exercisetestcase');
INSERT INTO auth_permission VALUES ('123', 'Can delete 练习题测试用例', '31', 'delete_exercisetestcase');
INSERT INTO auth_permission VALUES ('124', 'Can view 练习题测试用例', '31', 'view_exercisetestcase');
INSERT INTO auth_permission VALUES ('125', 'Can add Jupyter文档', '32', 'add_jupyterdocument');
INSERT INTO auth_permission VALUES ('126', 'Can change Jupyter文档', '32', 'change_jupyterdocument');
INSERT INTO auth_permission VALUES ('127', 'Can delete Jupyter文档', '32', 'delete_jupyterdocument');
INSERT INTO auth_permission VALUES ('128', 'Can view Jupyter文档', '32', 'view_jupyterdocument');
INSERT INTO auth_permission VALUES ('129', 'Can add 学习风格', '33', 'add_learningstyle');
INSERT INTO auth_permission VALUES ('130', 'Can change 学习风格', '33', 'change_learningstyle');
INSERT INTO auth_permission VALUES ('131', 'Can delete 学习风格', '33', 'delete_learningstyle');
INSERT INTO auth_permission VALUES ('132', 'Can view 学习风格', '33', 'view_learningstyle');
INSERT INTO auth_permission VALUES ('133', 'Can add 学习推荐', '34', 'add_learningrecommendation');
INSERT INTO auth_permission VALUES ('134', 'Can change 学习推荐', '34', 'change_learningrecommendation');
INSERT INTO auth_permission VALUES ('135', 'Can delete 学习推荐', '34', 'delete_learningrecommendation');
INSERT INTO auth_permission VALUES ('136', 'Can view 学习推荐', '34', 'view_learningrecommendation');
INSERT INTO auth_permission VALUES ('137', 'Can add 学习偏好', '35', 'add_learningpreference');
INSERT INTO auth_permission VALUES ('138', 'Can change 学习偏好', '35', 'change_learningpreference');
INSERT INTO auth_permission VALUES ('139', 'Can delete 学习偏好', '35', 'delete_learningpreference');
INSERT INTO auth_permission VALUES ('140', 'Can view 学习偏好', '35', 'view_learningpreference');
INSERT INTO auth_permission VALUES ('141', 'Can add 知识掌握度', '36', 'add_knowledgemastery');
INSERT INTO auth_permission VALUES ('142', 'Can change 知识掌握度', '36', 'change_knowledgemastery');
INSERT INTO auth_permission VALUES ('143', 'Can delete 知识掌握度', '36', 'delete_knowledgemastery');
INSERT INTO auth_permission VALUES ('144', 'Can view 知识掌握度', '36', 'view_knowledgemastery');
INSERT INTO auth_permission VALUES ('145', 'Can add 笔记附件', '37', 'add_noteattachment');
INSERT INTO auth_permission VALUES ('146', 'Can change 笔记附件', '37', 'change_noteattachment');
INSERT INTO auth_permission VALUES ('147', 'Can delete 笔记附件', '37', 'delete_noteattachment');
INSERT INTO auth_permission VALUES ('148', 'Can view 笔记附件', '37', 'view_noteattachment');
INSERT INTO auth_permission VALUES ('149', 'Can add 笔记分享', '38', 'add_noteshare');
INSERT INTO auth_permission VALUES ('150', 'Can change 笔记分享', '38', 'change_noteshare');
INSERT INTO auth_permission VALUES ('151', 'Can delete 笔记分享', '38', 'delete_noteshare');
INSERT INTO auth_permission VALUES ('152', 'Can view 笔记分享', '38', 'view_noteshare');
INSERT INTO auth_permission VALUES ('153', 'Can add 笔记标签', '39', 'add_notetag');
INSERT INTO auth_permission VALUES ('154', 'Can change 笔记标签', '39', 'change_notetag');
INSERT INTO auth_permission VALUES ('155', 'Can delete 笔记标签', '39', 'delete_notetag');
INSERT INTO auth_permission VALUES ('156', 'Can view 笔记标签', '39', 'view_notetag');
INSERT INTO auth_permission VALUES ('157', 'Can add 笔记标签关联', '40', 'add_notetagrelation');
INSERT INTO auth_permission VALUES ('158', 'Can change 笔记标签关联', '40', 'change_notetagrelation');
INSERT INTO auth_permission VALUES ('159', 'Can delete 笔记标签关联', '40', 'delete_notetagrelation');
INSERT INTO auth_permission VALUES ('160', 'Can view 笔记标签关联', '40', 'view_notetagrelation');
INSERT INTO auth_permission VALUES ('161', 'Can add 笔记版本历史', '41', 'add_noteversion');
INSERT INTO auth_permission VALUES ('162', 'Can change 笔记版本历史', '41', 'change_noteversion');
INSERT INTO auth_permission VALUES ('163', 'Can delete 笔记版本历史', '41', 'delete_noteversion');
INSERT INTO auth_permission VALUES ('164', 'Can view 笔记版本历史', '41', 'view_noteversion');
INSERT INTO auth_permission VALUES ('165', 'Can add 工具', '42', 'add_tool');
INSERT INTO auth_permission VALUES ('166', 'Can change 工具', '42', 'change_tool');
INSERT INTO auth_permission VALUES ('167', 'Can delete 工具', '42', 'delete_tool');
INSERT INTO auth_permission VALUES ('168', 'Can view 工具', '42', 'view_tool');
INSERT INTO auth_permission VALUES ('169', 'Can add 工具分类', '43', 'add_toolcategory');
INSERT INTO auth_permission VALUES ('170', 'Can change 工具分类', '43', 'change_toolcategory');
INSERT INTO auth_permission VALUES ('171', 'Can delete 工具分类', '43', 'delete_toolcategory');
INSERT INTO auth_permission VALUES ('172', 'Can view 工具分类', '43', 'view_toolcategory');
INSERT INTO auth_permission VALUES ('173', 'Can add 工具参数', '44', 'add_toolparameter');
INSERT INTO auth_permission VALUES ('174', 'Can change 工具参数', '44', 'change_toolparameter');
INSERT INTO auth_permission VALUES ('175', 'Can delete 工具参数', '44', 'delete_toolparameter');
INSERT INTO auth_permission VALUES ('176', 'Can view 工具参数', '44', 'view_toolparameter');
INSERT INTO auth_permission VALUES ('177', 'Can add 执行历史', '45', 'add_executionhistory');
INSERT INTO auth_permission VALUES ('178', 'Can change 执行历史', '45', 'change_executionhistory');
INSERT INTO auth_permission VALUES ('179', 'Can delete 执行历史', '45', 'delete_executionhistory');
INSERT INTO auth_permission VALUES ('180', 'Can view 执行历史', '45', 'view_executionhistory');

-- ----------------------------
-- Table structure for `books_book`
-- ----------------------------
DROP TABLE IF EXISTS `books_book`;
CREATE TABLE `books_book` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `author` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cover` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `tags` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `chapter_count` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `pdf_file` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `owner_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `books_book_owner_id_6abfd7ae_fk_users_user_id` (`owner_id`),
  CONSTRAINT `books_book_owner_id_6abfd7ae_fk_users_user_id` FOREIGN KEY (`owner_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of books_book
-- ----------------------------
INSERT INTO books_book VALUES ('1', '大学计算机基础与应用', '计算机基础教育研究组', '', '本书专为非计算机专业学生设计，系统介绍计算机基础知识、操作系统使用、办公软件应用和互联网基础。通过实际案例和操作指导，帮助学生掌握必备的计算机应用技能。', '[]', '0', '2026-01-05 09:01:21.736759', '2026-01-05 09:01:21.736759', '', null);
INSERT INTO books_book VALUES ('2', '数据分析与可视化入门', '数据科学教育团队', '', '本书面向非计算机专业学生，介绍数据分析的基本概念、方法和工具。内容涵盖数据收集、清洗、分析和可视化的全过程，通过Python语言实践，培养学生的数据素养和分析能力。', '[]', '0', '2026-01-05 09:01:21.738479', '2026-01-05 09:01:21.738479', '', null);
INSERT INTO books_book VALUES ('3', '人工智能与机器学习基础', 'AI教育研究中心', '', '本书为非计算机专业学生提供人工智能和机器学习的入门知识，以通俗易懂的方式解释复杂概念，通过案例教学展示AI技术在各领域的应用，帮助学生了解AI发展趋势和应用前景。', '[]', '0', '2026-01-05 09:01:21.740030', '2026-01-05 09:01:21.740030', '', null);

-- ----------------------------
-- Table structure for `books_chapter`
-- ----------------------------
DROP TABLE IF EXISTS `books_chapter`;
CREATE TABLE `books_chapter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `duration` int(11) NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext COLLATE utf8mb4_unicode_ci,
  `code` longtext COLLATE utf8mb4_unicode_ci,
  `language` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `book_id` int(11) NOT NULL,
  `video_url` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `jupyter_content` longtext COLLATE utf8mb4_unicode_ci,
  `merged_content` longtext COLLATE utf8mb4_unicode_ci,
  `level` int(11) NOT NULL,
  `is_main_chapter` tinyint(1) NOT NULL,
  `parent_chapter_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `books_chapter_book_id_109cb672_fk_books_book_id` (`book_id`),
  KEY `books_chapter_parent_chapter_id_c11577e1_fk_books_chapter_id` (`parent_chapter_id`),
  CONSTRAINT `books_chapter_book_id_109cb672_fk_books_book_id` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `books_chapter_parent_chapter_id_c11577e1_fk_books_chapter_id` FOREIGN KEY (`parent_chapter_id`) REFERENCES `books_chapter` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of books_chapter
-- ----------------------------
INSERT INTO books_chapter VALUES ('1', '第1章 计算机基础知识', 'reading', '60', '本章介绍计算机的基本概念、发展历程和系统组成，帮助读者建立对计算机的整体认识。', null, null, 'python', '1', '2026-01-05 09:01:21.741650', '2026-01-05 09:01:21.741650', '1', null, 'jupyter', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 1.1 计算机系统概述\\n\\n计算机系统由硬件系统和软件系统两大部分组成。硬件系统是计算机的物理组成部分，包括中央处理器(CPU)、内存、存储设备、输入设备和输出设备等。软件系统则是运行在硬件之上的程序和数据，包括系统软件和应用软件。\\n\\n对于非计算机专业学生来说，了解计算机的基本组成和工作原理有助于我们更好地使用计算机。计算机的基本工作原理是存储程序和程序控制，即程序和数据存储在计算机的存储器中，由CPU依次取出并执行指令，完成预定的任务。\\n\\n随着计算机技术的发展，计算机的性能不断提升，应用领域也不断扩大。从最初的科学计算，到现在的人工智能、大数据分析等，计算机已经渗透到我们生活和工作的方方面面。\"}, {\"cell_type\": \"markdown\", \"source\": \"## 1.2 计算机中的数制与编码\\n\\n计算机内部采用二进制进行数据存储和处理。二进制只有0和1两个数字，运算规则简单，便于用电子元件实现。除了二进制，计算机中还常用到十进制、八进制和十六进制等数制，它们之间可以相互转换。\\n\\n在计算机中，各种信息（如文字、图像、声音等）都需要转换为二进制形式进行存储和处理。文字的编码是指用二进制数表示文字的规则，常见的编码标准有ASCII码、GB2312、UTF-8等。了解这些编码标准有助于我们正确地处理和显示各种文字信息。\\n\\n对于非计算机专业学生来说，掌握基本的数制转换方法和了解常见的编码标准是很有必要的，这有助于我们更好地理解计算机是如何处理信息的。\"}, {\"cell_type\": \"code\", \"source\": \"# 计算机存储单位换算示例\\ndef storage_conversion(bytes_value):\\n    units = [\'B\', \'KB\', \'MB\', \'GB\', \'TB\']\\n    index = 0\\n    value = float(bytes_value)\\n    while value >= 1024 and index < len(units) - 1:\\n        value /= 1024\\n        index += 1\\n    return f\\\"{value:.2f} {units[index]}\\\"\\n\\n# 测试函数\\nprint(storage_conversion(1024))  # 1 KB\\nprint(storage_conversion(1048576))  # 1 MB\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 1.1 \\u8ba1\\u7b97\\u673a\\u7cfb\\u7edf\\u6982\\u8ff0\\n\\n\\u8ba1\\u7b97\\u673a\\u7cfb\\u7edf\\u7531\\u786c\\u4ef6\\u7cfb\\u7edf\\u548c\\u8f6f\\u4ef6\\u7cfb\\u7edf\\u4e24\\u5927\\u90e8\\u5206\\u7ec4\\u6210\\u3002\\u786c\\u4ef6\\u7cfb\\u7edf\\u662f\\u8ba1\\u7b97\\u673a\\u7684\\u7269\\u7406\\u7ec4\\u6210\\u90e8\\u5206\\uff0c\\u5305\\u62ec\\u4e2d\\u592e\\u5904\\u7406\\u5668(CPU)\\u3001\\u5185\\u5b58\\u3001\\u5b58\\u50a8\\u8bbe\\u5907\\u3001\\u8f93\\u5165\\u8bbe\\u5907\\u548c\\u8f93\\u51fa\\u8bbe\\u5907\\u7b49\\u3002\\u8f6f\\u4ef6\\u7cfb\\u7edf\\u5219\\u662f\\u8fd0\\u884c\\u5728\\u786c\\u4ef6\\u4e4b\\u4e0a\\u7684\\u7a0b\\u5e8f\\u548c\\u6570\\u636e\\uff0c\\u5305\\u62ec\\u7cfb\\u7edf\\u8f6f\\u4ef6\\u548c\\u5e94\\u7528\\u8f6f\\u4ef6\\u3002\\n\\n\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u4e86\\u89e3\\u8ba1\\u7b97\\u673a\\u7684\\u57fa\\u672c\\u7ec4\\u6210\\u548c\\u5de5\\u4f5c\\u539f\\u7406\\u6709\\u52a9\\u4e8e\\u6211\\u4eec\\u66f4\\u597d\\u5730\\u4f7f\\u7528\\u8ba1\\u7b97\\u673a\\u3002\\u8ba1\\u7b97\\u673a\\u7684\\u57fa\\u672c\\u5de5\\u4f5c\\u539f\\u7406\\u662f\\u5b58\\u50a8\\u7a0b\\u5e8f\\u548c\\u7a0b\\u5e8f\\u63a7\\u5236\\uff0c\\u5373\\u7a0b\\u5e8f\\u548c\\u6570\\u636e\\u5b58\\u50a8\\u5728\\u8ba1\\u7b97\\u673a\\u7684\\u5b58\\u50a8\\u5668\\u4e2d\\uff0c\\u7531CPU\\u4f9d\\u6b21\\u53d6\\u51fa\\u5e76\\u6267\\u884c\\u6307\\u4ee4\\uff0c\\u5b8c\\u6210\\u9884\\u5b9a\\u7684\\u4efb\\u52a1\\u3002\\n\\n\\u968f\\u7740\\u8ba1\\u7b97\\u673a\\u6280\\u672f\\u7684\\u53d1\\u5c55\\uff0c\\u8ba1\\u7b97\\u673a\\u7684\\u6027\\u80fd\\u4e0d\\u65ad\\u63d0\\u5347\\uff0c\\u5e94\\u7528\\u9886\\u57df\\u4e5f\\u4e0d\\u65ad\\u6269\\u5927\\u3002\\u4ece\\u6700\\u521d\\u7684\\u79d1\\u5b66\\u8ba1\\u7b97\\uff0c\\u5230\\u73b0\\u5728\\u7684\\u4eba\\u5de5\\u667a\\u80fd\\u3001\\u5927\\u6570\\u636e\\u5206\\u6790\\u7b49\\uff0c\\u8ba1\\u7b97\\u673a\\u5df2\\u7ecf\\u6e17\\u900f\\u5230\\u6211\\u4eec\\u751f\\u6d3b\\u548c\\u5de5\\u4f5c\\u7684\\u65b9\\u65b9\\u9762\\u9762\\u3002\"}, {\"cell_type\": \"markdown\", \"source\": \"## 1.2 \\u8ba1\\u7b97\\u673a\\u4e2d\\u7684\\u6570\\u5236\\u4e0e\\u7f16\\u7801\\n\\n\\u8ba1\\u7b97\\u673a\\u5185\\u90e8\\u91c7\\u7528\\u4e8c\\u8fdb\\u5236\\u8fdb\\u884c\\u6570\\u636e\\u5b58\\u50a8\\u548c\\u5904\\u7406\\u3002\\u4e8c\\u8fdb\\u5236\\u53ea\\u67090\\u548c1\\u4e24\\u4e2a\\u6570\\u5b57\\uff0c\\u8fd0\\u7b97\\u89c4\\u5219\\u7b80\\u5355\\uff0c\\u4fbf\\u4e8e\\u7528\\u7535\\u5b50\\u5143\\u4ef6\\u5b9e\\u73b0\\u3002\\u9664\\u4e86\\u4e8c\\u8fdb\\u5236\\uff0c\\u8ba1\\u7b97\\u673a\\u4e2d\\u8fd8\\u5e38\\u7528\\u5230\\u5341\\u8fdb\\u5236\\u3001\\u516b\\u8fdb\\u5236\\u548c\\u5341\\u516d\\u8fdb\\u5236\\u7b49\\u6570\\u5236\\uff0c\\u5b83\\u4eec\\u4e4b\\u95f4\\u53ef\\u4ee5\\u76f8\\u4e92\\u8f6c\\u6362\\u3002\\n\\n\\u5728\\u8ba1\\u7b97\\u673a\\u4e2d\\uff0c\\u5404\\u79cd\\u4fe1\\u606f\\uff08\\u5982\\u6587\\u5b57\\u3001\\u56fe\\u50cf\\u3001\\u58f0\\u97f3\\u7b49\\uff09\\u90fd\\u9700\\u8981\\u8f6c\\u6362\\u4e3a\\u4e8c\\u8fdb\\u5236\\u5f62\\u5f0f\\u8fdb\\u884c\\u5b58\\u50a8\\u548c\\u5904\\u7406\\u3002\\u6587\\u5b57\\u7684\\u7f16\\u7801\\u662f\\u6307\\u7528\\u4e8c\\u8fdb\\u5236\\u6570\\u8868\\u793a\\u6587\\u5b57\\u7684\\u89c4\\u5219\\uff0c\\u5e38\\u89c1\\u7684\\u7f16\\u7801\\u6807\\u51c6\\u6709ASCII\\u7801\\u3001GB2312\\u3001UTF-8\\u7b49\\u3002\\u4e86\\u89e3\\u8fd9\\u4e9b\\u7f16\\u7801\\u6807\\u51c6\\u6709\\u52a9\\u4e8e\\u6211\\u4eec\\u6b63\\u786e\\u5730\\u5904\\u7406\\u548c\\u663e\\u793a\\u5404\\u79cd\\u6587\\u5b57\\u4fe1\\u606f\\u3002\\n\\n\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u638c\\u63e1\\u57fa\\u672c\\u7684\\u6570\\u5236\\u8f6c\\u6362\\u65b9\\u6cd5\\u548c\\u4e86\\u89e3\\u5e38\\u89c1\\u7684\\u7f16\\u7801\\u6807\\u51c6\\u662f\\u5f88\\u6709\\u5fc5\\u8981\\u7684\\uff0c\\u8fd9\\u6709\\u52a9\\u4e8e\\u6211\\u4eec\\u66f4\\u597d\\u5730\\u7406\\u89e3\\u8ba1\\u7b97\\u673a\\u662f\\u5982\\u4f55\\u5904\\u7406\\u4fe1\\u606f\\u7684\\u3002\"}, {\"cell_type\": \"code\", \"source\": \"# \\u8ba1\\u7b97\\u673a\\u5b58\\u50a8\\u5355\\u4f4d\\u6362\\u7b97\\u793a\\u4f8b\\ndef storage_conversion(bytes_value):\\n    units = [\'B\', \'KB\', \'MB\', \'GB\', \'TB\']\\n    index = 0\\n    value = float(bytes_value)\\n    while value >= 1024 and index < len(units) - 1:\\n        value /= 1024\\n        index += 1\\n    return f\\\"{value:.2f} {units[index]}\\\"\\n\\n# \\u6d4b\\u8bd5\\u51fd\\u6570\\nprint(storage_conversion(1024))  # 1 KB\\nprint(storage_conversion(1048576))  # 1 MB\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python\", \"language\": \"python\", \"name\": \"python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '0', '1', null);
INSERT INTO books_chapter VALUES ('2', '第2章 操作系统基础', 'reading', '60', '本章详细讲解操作系统的基本原理、功能和常用操作，包括文件管理和系统设置。', null, null, 'python', '2', '2026-01-05 09:01:21.744756', '2026-01-05 09:01:21.744756', '1', null, 'jupyter', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 2.1 操作系统概述\\n\\n操作系统是管理计算机硬件与软件资源的系统软件，为用户提供了一个操作计算机的界面。常见的操作系统有Windows、macOS和Linux等。对于非计算机专业学生来说，熟悉操作系统的基本操作是使用计算机的前提。\\n\\n操作系统的主要功能包括进程管理、内存管理、文件管理和设备管理等。进程管理负责调度和控制程序的执行；内存管理负责分配和回收内存资源；文件管理负责组织和存取文件；设备管理负责管理和控制各种硬件设备。了解这些功能有助于我们更好地理解和使用操作系统。\"}, {\"cell_type\": \"markdown\", \"source\": \"## 2.2 文件与文件夹管理\\n\\n文件是存储在计算机中的一组相关信息的集合，通常具有特定的扩展名来标识文件类型。文件夹则是用于组织和管理文件的容器，可以嵌套创建子文件夹。合理地组织文件和文件夹结构有助于提高工作效率。\\n\\n在Windows操作系统中，文件系统采用树形结构，以驱动器盘符为根目录，向下延伸出多个层次的文件夹和文件。我们可以通过资源管理器来浏览、创建、移动、复制和删除文件和文件夹。学会这些基本操作对于日常的文件管理非常重要。\"}, {\"cell_type\": \"code\", \"source\": \"# 文件大小统计示例\\nimport os\\ndef get_directory_size(directory):\\n    total_size = 0\\n    for path, dirs, files in os.walk(directory):\\n        for file in files:\\n            try:\\n                filepath = os.path.join(path, file)\\n                total_size += os.path.getsize(filepath)\\n            except OSError:\\n                continue\\n    return total_size\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# 简单的文件重命名工具\\nimport os\\ndef batch_rename(directory, prefix):\\n    count = 1\\n    for filename in os.listdir(directory):\\n        if os.path.isfile(os.path.join(directory, filename)):\\n            file_ext = os.path.splitext(filename)[1]\\n            new_name = f\\\"{prefix}_{count:03d}{file_ext}\\\"\\n            os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))\\n            count += 1\\n    return count - 1\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 2.1 \\u64cd\\u4f5c\\u7cfb\\u7edf\\u6982\\u8ff0\\n\\n\\u64cd\\u4f5c\\u7cfb\\u7edf\\u662f\\u7ba1\\u7406\\u8ba1\\u7b97\\u673a\\u786c\\u4ef6\\u4e0e\\u8f6f\\u4ef6\\u8d44\\u6e90\\u7684\\u7cfb\\u7edf\\u8f6f\\u4ef6\\uff0c\\u4e3a\\u7528\\u6237\\u63d0\\u4f9b\\u4e86\\u4e00\\u4e2a\\u64cd\\u4f5c\\u8ba1\\u7b97\\u673a\\u7684\\u754c\\u9762\\u3002\\u5e38\\u89c1\\u7684\\u64cd\\u4f5c\\u7cfb\\u7edf\\u6709Windows\\u3001macOS\\u548cLinux\\u7b49\\u3002\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u719f\\u6089\\u64cd\\u4f5c\\u7cfb\\u7edf\\u7684\\u57fa\\u672c\\u64cd\\u4f5c\\u662f\\u4f7f\\u7528\\u8ba1\\u7b97\\u673a\\u7684\\u524d\\u63d0\\u3002\\n\\n\\u64cd\\u4f5c\\u7cfb\\u7edf\\u7684\\u4e3b\\u8981\\u529f\\u80fd\\u5305\\u62ec\\u8fdb\\u7a0b\\u7ba1\\u7406\\u3001\\u5185\\u5b58\\u7ba1\\u7406\\u3001\\u6587\\u4ef6\\u7ba1\\u7406\\u548c\\u8bbe\\u5907\\u7ba1\\u7406\\u7b49\\u3002\\u8fdb\\u7a0b\\u7ba1\\u7406\\u8d1f\\u8d23\\u8c03\\u5ea6\\u548c\\u63a7\\u5236\\u7a0b\\u5e8f\\u7684\\u6267\\u884c\\uff1b\\u5185\\u5b58\\u7ba1\\u7406\\u8d1f\\u8d23\\u5206\\u914d\\u548c\\u56de\\u6536\\u5185\\u5b58\\u8d44\\u6e90\\uff1b\\u6587\\u4ef6\\u7ba1\\u7406\\u8d1f\\u8d23\\u7ec4\\u7ec7\\u548c\\u5b58\\u53d6\\u6587\\u4ef6\\uff1b\\u8bbe\\u5907\\u7ba1\\u7406\\u8d1f\\u8d23\\u7ba1\\u7406\\u548c\\u63a7\\u5236\\u5404\\u79cd\\u786c\\u4ef6\\u8bbe\\u5907\\u3002\\u4e86\\u89e3\\u8fd9\\u4e9b\\u529f\\u80fd\\u6709\\u52a9\\u4e8e\\u6211\\u4eec\\u66f4\\u597d\\u5730\\u7406\\u89e3\\u548c\\u4f7f\\u7528\\u64cd\\u4f5c\\u7cfb\\u7edf\\u3002\"}, {\"cell_type\": \"markdown\", \"source\": \"## 2.2 \\u6587\\u4ef6\\u4e0e\\u6587\\u4ef6\\u5939\\u7ba1\\u7406\\n\\n\\u6587\\u4ef6\\u662f\\u5b58\\u50a8\\u5728\\u8ba1\\u7b97\\u673a\\u4e2d\\u7684\\u4e00\\u7ec4\\u76f8\\u5173\\u4fe1\\u606f\\u7684\\u96c6\\u5408\\uff0c\\u901a\\u5e38\\u5177\\u6709\\u7279\\u5b9a\\u7684\\u6269\\u5c55\\u540d\\u6765\\u6807\\u8bc6\\u6587\\u4ef6\\u7c7b\\u578b\\u3002\\u6587\\u4ef6\\u5939\\u5219\\u662f\\u7528\\u4e8e\\u7ec4\\u7ec7\\u548c\\u7ba1\\u7406\\u6587\\u4ef6\\u7684\\u5bb9\\u5668\\uff0c\\u53ef\\u4ee5\\u5d4c\\u5957\\u521b\\u5efa\\u5b50\\u6587\\u4ef6\\u5939\\u3002\\u5408\\u7406\\u5730\\u7ec4\\u7ec7\\u6587\\u4ef6\\u548c\\u6587\\u4ef6\\u5939\\u7ed3\\u6784\\u6709\\u52a9\\u4e8e\\u63d0\\u9ad8\\u5de5\\u4f5c\\u6548\\u7387\\u3002\\n\\n\\u5728Windows\\u64cd\\u4f5c\\u7cfb\\u7edf\\u4e2d\\uff0c\\u6587\\u4ef6\\u7cfb\\u7edf\\u91c7\\u7528\\u6811\\u5f62\\u7ed3\\u6784\\uff0c\\u4ee5\\u9a71\\u52a8\\u5668\\u76d8\\u7b26\\u4e3a\\u6839\\u76ee\\u5f55\\uff0c\\u5411\\u4e0b\\u5ef6\\u4f38\\u51fa\\u591a\\u4e2a\\u5c42\\u6b21\\u7684\\u6587\\u4ef6\\u5939\\u548c\\u6587\\u4ef6\\u3002\\u6211\\u4eec\\u53ef\\u4ee5\\u901a\\u8fc7\\u8d44\\u6e90\\u7ba1\\u7406\\u5668\\u6765\\u6d4f\\u89c8\\u3001\\u521b\\u5efa\\u3001\\u79fb\\u52a8\\u3001\\u590d\\u5236\\u548c\\u5220\\u9664\\u6587\\u4ef6\\u548c\\u6587\\u4ef6\\u5939\\u3002\\u5b66\\u4f1a\\u8fd9\\u4e9b\\u57fa\\u672c\\u64cd\\u4f5c\\u5bf9\\u4e8e\\u65e5\\u5e38\\u7684\\u6587\\u4ef6\\u7ba1\\u7406\\u975e\\u5e38\\u91cd\\u8981\\u3002\"}, {\"cell_type\": \"code\", \"source\": \"# \\u6587\\u4ef6\\u5927\\u5c0f\\u7edf\\u8ba1\\u793a\\u4f8b\\nimport os\\ndef get_directory_size(directory):\\n    total_size = 0\\n    for path, dirs, files in os.walk(directory):\\n        for file in files:\\n            try:\\n                filepath = os.path.join(path, file)\\n                total_size += os.path.getsize(filepath)\\n            except OSError:\\n                continue\\n    return total_size\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# \\u7b80\\u5355\\u7684\\u6587\\u4ef6\\u91cd\\u547d\\u540d\\u5de5\\u5177\\nimport os\\ndef batch_rename(directory, prefix):\\n    count = 1\\n    for filename in os.listdir(directory):\\n        if os.path.isfile(os.path.join(directory, filename)):\\n            file_ext = os.path.splitext(filename)[1]\\n            new_name = f\\\"{prefix}_{count:03d}{file_ext}\\\"\\n            os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))\\n            count += 1\\n    return count - 1\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python\", \"language\": \"python\", \"name\": \"python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '0', '1', null);
INSERT INTO books_chapter VALUES ('3', '第3章 办公软件应用', 'reading', '60', '本章介绍办公软件的使用技巧，包括文字处理、电子表格和演示文稿的基本操作。', null, null, 'python', '3', '2026-01-05 09:01:21.750927', '2026-01-05 09:01:21.750927', '1', null, 'jupyter', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 3.1 Word文档处理\\n\\nMicrosoft Word是最常用的文字处理软件，广泛应用于文档创建、编辑和排版等工作。对于非计算机专业学生来说，掌握Word的基本操作是学习和工作的必备技能。\\n\\nWord的主要功能包括文本输入与编辑、格式设置、段落设置、页面设置、表格制作、图片插入等。在学术写作中，我们经常需要使用Word来撰写论文、报告等文档。熟练掌握Word的样式、目录生成、引用和参考文献等功能可以大大提高学术写作的效率和质量。\"}, {\"cell_type\": \"markdown\", \"source\": \"## 3.2 Excel电子表格应用\\n\\nMicrosoft Excel是一款功能强大的电子表格软件，主要用于数据处理、数据分析和图表绘制等。对于非计算机专业学生来说，掌握Excel的基本操作和常用函数可以帮助我们更高效地处理和分析数据。\\n\\nExcel的主要功能包括数据输入和编辑、格式设置、公式和函数使用、数据分析工具、图表创建等。常用的函数包括求和函数SUM、平均值函数AVERAGE、计数函数COUNT、条件函数IF、查找函数VLOOKUP等。学会使用这些函数可以大大简化数据计算和分析的工作。\"}, {\"cell_type\": \"code\", \"source\": \"# Excel数据处理示例\\nimport pandas as pd\\ndef create_sample_data():\\n    data = {\\n        \'姓名\': [\'张三\', \'李四\', \'王五\', \'赵六\'],\\n        \'语文\': [85, 92, 78, 90],\\n        \'数学\': [90, 85, 95, 88],\\n        \'英语\': [88, 90, 82, 95]\\n    }\\n    return pd.DataFrame(data)\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# 简单的文本处理函数\\ndef format_text(text, operation):\\n    if operation == \'uppercase\':\\n        return text.upper()\\n    elif operation == \'lowercase\':\\n        return text.lower()\\n    elif operation == \'titlecase\':\\n        return text.title()\\n    else:\\n        return text\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 3.1 Word\\u6587\\u6863\\u5904\\u7406\\n\\nMicrosoft Word\\u662f\\u6700\\u5e38\\u7528\\u7684\\u6587\\u5b57\\u5904\\u7406\\u8f6f\\u4ef6\\uff0c\\u5e7f\\u6cdb\\u5e94\\u7528\\u4e8e\\u6587\\u6863\\u521b\\u5efa\\u3001\\u7f16\\u8f91\\u548c\\u6392\\u7248\\u7b49\\u5de5\\u4f5c\\u3002\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u638c\\u63e1Word\\u7684\\u57fa\\u672c\\u64cd\\u4f5c\\u662f\\u5b66\\u4e60\\u548c\\u5de5\\u4f5c\\u7684\\u5fc5\\u5907\\u6280\\u80fd\\u3002\\n\\nWord\\u7684\\u4e3b\\u8981\\u529f\\u80fd\\u5305\\u62ec\\u6587\\u672c\\u8f93\\u5165\\u4e0e\\u7f16\\u8f91\\u3001\\u683c\\u5f0f\\u8bbe\\u7f6e\\u3001\\u6bb5\\u843d\\u8bbe\\u7f6e\\u3001\\u9875\\u9762\\u8bbe\\u7f6e\\u3001\\u8868\\u683c\\u5236\\u4f5c\\u3001\\u56fe\\u7247\\u63d2\\u5165\\u7b49\\u3002\\u5728\\u5b66\\u672f\\u5199\\u4f5c\\u4e2d\\uff0c\\u6211\\u4eec\\u7ecf\\u5e38\\u9700\\u8981\\u4f7f\\u7528Word\\u6765\\u64b0\\u5199\\u8bba\\u6587\\u3001\\u62a5\\u544a\\u7b49\\u6587\\u6863\\u3002\\u719f\\u7ec3\\u638c\\u63e1Word\\u7684\\u6837\\u5f0f\\u3001\\u76ee\\u5f55\\u751f\\u6210\\u3001\\u5f15\\u7528\\u548c\\u53c2\\u8003\\u6587\\u732e\\u7b49\\u529f\\u80fd\\u53ef\\u4ee5\\u5927\\u5927\\u63d0\\u9ad8\\u5b66\\u672f\\u5199\\u4f5c\\u7684\\u6548\\u7387\\u548c\\u8d28\\u91cf\\u3002\"}, {\"cell_type\": \"markdown\", \"source\": \"## 3.2 Excel\\u7535\\u5b50\\u8868\\u683c\\u5e94\\u7528\\n\\nMicrosoft Excel\\u662f\\u4e00\\u6b3e\\u529f\\u80fd\\u5f3a\\u5927\\u7684\\u7535\\u5b50\\u8868\\u683c\\u8f6f\\u4ef6\\uff0c\\u4e3b\\u8981\\u7528\\u4e8e\\u6570\\u636e\\u5904\\u7406\\u3001\\u6570\\u636e\\u5206\\u6790\\u548c\\u56fe\\u8868\\u7ed8\\u5236\\u7b49\\u3002\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u638c\\u63e1Excel\\u7684\\u57fa\\u672c\\u64cd\\u4f5c\\u548c\\u5e38\\u7528\\u51fd\\u6570\\u53ef\\u4ee5\\u5e2e\\u52a9\\u6211\\u4eec\\u66f4\\u9ad8\\u6548\\u5730\\u5904\\u7406\\u548c\\u5206\\u6790\\u6570\\u636e\\u3002\\n\\nExcel\\u7684\\u4e3b\\u8981\\u529f\\u80fd\\u5305\\u62ec\\u6570\\u636e\\u8f93\\u5165\\u548c\\u7f16\\u8f91\\u3001\\u683c\\u5f0f\\u8bbe\\u7f6e\\u3001\\u516c\\u5f0f\\u548c\\u51fd\\u6570\\u4f7f\\u7528\\u3001\\u6570\\u636e\\u5206\\u6790\\u5de5\\u5177\\u3001\\u56fe\\u8868\\u521b\\u5efa\\u7b49\\u3002\\u5e38\\u7528\\u7684\\u51fd\\u6570\\u5305\\u62ec\\u6c42\\u548c\\u51fd\\u6570SUM\\u3001\\u5e73\\u5747\\u503c\\u51fd\\u6570AVERAGE\\u3001\\u8ba1\\u6570\\u51fd\\u6570COUNT\\u3001\\u6761\\u4ef6\\u51fd\\u6570IF\\u3001\\u67e5\\u627e\\u51fd\\u6570VLOOKUP\\u7b49\\u3002\\u5b66\\u4f1a\\u4f7f\\u7528\\u8fd9\\u4e9b\\u51fd\\u6570\\u53ef\\u4ee5\\u5927\\u5927\\u7b80\\u5316\\u6570\\u636e\\u8ba1\\u7b97\\u548c\\u5206\\u6790\\u7684\\u5de5\\u4f5c\\u3002\"}, {\"cell_type\": \"code\", \"source\": \"# Excel\\u6570\\u636e\\u5904\\u7406\\u793a\\u4f8b\\nimport pandas as pd\\ndef create_sample_data():\\n    data = {\\n        \'\\u59d3\\u540d\': [\'\\u5f20\\u4e09\', \'\\u674e\\u56db\', \'\\u738b\\u4e94\', \'\\u8d75\\u516d\'],\\n        \'\\u8bed\\u6587\': [85, 92, 78, 90],\\n        \'\\u6570\\u5b66\': [90, 85, 95, 88],\\n        \'\\u82f1\\u8bed\': [88, 90, 82, 95]\\n    }\\n    return pd.DataFrame(data)\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# \\u7b80\\u5355\\u7684\\u6587\\u672c\\u5904\\u7406\\u51fd\\u6570\\ndef format_text(text, operation):\\n    if operation == \'uppercase\':\\n        return text.upper()\\n    elif operation == \'lowercase\':\\n        return text.lower()\\n    elif operation == \'titlecase\':\\n        return text.title()\\n    else:\\n        return text\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python\", \"language\": \"python\", \"name\": \"python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '0', '1', null);
INSERT INTO books_chapter VALUES ('4', '第1章 数据分析基础', 'reading', '60', '本章介绍数据分析的基本概念、流程和常用方法，为后续学习奠定基础。', null, null, 'python', '1', '2026-01-05 09:01:21.741650', '2026-01-05 09:01:21.741650', '2', null, 'jupyter', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 1.1 数据分析概述\\n\\n数据分析是指用适当的统计分析方法对收集来的数据进行分析，提取有用信息并形成结论的过程。随着大数据时代的到来，数据分析在各个领域的重要性日益凸显。对于非计算机专业学生来说，掌握基本的数据分析技能可以帮助我们更好地理解和利用数据。\\n\\n数据分析的基本流程包括数据收集、数据清洗、数据转换、数据分析和数据可视化等步骤。在数据分析过程中，我们需要选择合适的分析方法和工具，根据数据的类型和分析的目的来确定具体的分析策略。\"}, {\"cell_type\": \"markdown\", \"source\": \"## 1.2 数据类型与数据结构\\n\\n在数据分析中，了解数据的类型和结构是非常重要的。常见的数据类型包括数值型数据（如整数、浮点数）、分类型数据（如性别、职业）、有序型数据（如评分等级）等。不同类型的数据需要采用不同的分析方法和处理方式。\\n\\n数据结构是指数据的组织方式，常见的数据结构包括表格数据、时间序列数据、文本数据等。表格数据是最常见的数据结构，它由行和列组成，每一行代表一个观察对象，每一列代表一个属性。\"}, {\"cell_type\": \"code\", \"source\": \"# 使用Pandas进行基本数据操作\\nimport pandas as pd\\ndef basic_data_operations(df):\\n    print(\'数据基本信息:\')\\n    print(df.info())\\n    print(\'\\n数据前5行:\')\\n    print(df.head())\\n    print(\'\\n数据统计摘要:\')\\n    print(df.describe())\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# 数据清洗示例\\nimport pandas as pd\\ndef handle_missing_values(df):\\n    print(\'缺失值统计:\')\\n    print(df.isnull().sum())\\n    # 填充数值型缺失值\\n    numeric_cols = df.select_dtypes(include=[\'float64\', \'int64\']).columns\\n    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())\\n    return df\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 1.1 \\u6570\\u636e\\u5206\\u6790\\u6982\\u8ff0\\n\\n\\u6570\\u636e\\u5206\\u6790\\u662f\\u6307\\u7528\\u9002\\u5f53\\u7684\\u7edf\\u8ba1\\u5206\\u6790\\u65b9\\u6cd5\\u5bf9\\u6536\\u96c6\\u6765\\u7684\\u6570\\u636e\\u8fdb\\u884c\\u5206\\u6790\\uff0c\\u63d0\\u53d6\\u6709\\u7528\\u4fe1\\u606f\\u5e76\\u5f62\\u6210\\u7ed3\\u8bba\\u7684\\u8fc7\\u7a0b\\u3002\\u968f\\u7740\\u5927\\u6570\\u636e\\u65f6\\u4ee3\\u7684\\u5230\\u6765\\uff0c\\u6570\\u636e\\u5206\\u6790\\u5728\\u5404\\u4e2a\\u9886\\u57df\\u7684\\u91cd\\u8981\\u6027\\u65e5\\u76ca\\u51f8\\u663e\\u3002\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u638c\\u63e1\\u57fa\\u672c\\u7684\\u6570\\u636e\\u5206\\u6790\\u6280\\u80fd\\u53ef\\u4ee5\\u5e2e\\u52a9\\u6211\\u4eec\\u66f4\\u597d\\u5730\\u7406\\u89e3\\u548c\\u5229\\u7528\\u6570\\u636e\\u3002\\n\\n\\u6570\\u636e\\u5206\\u6790\\u7684\\u57fa\\u672c\\u6d41\\u7a0b\\u5305\\u62ec\\u6570\\u636e\\u6536\\u96c6\\u3001\\u6570\\u636e\\u6e05\\u6d17\\u3001\\u6570\\u636e\\u8f6c\\u6362\\u3001\\u6570\\u636e\\u5206\\u6790\\u548c\\u6570\\u636e\\u53ef\\u89c6\\u5316\\u7b49\\u6b65\\u9aa4\\u3002\\u5728\\u6570\\u636e\\u5206\\u6790\\u8fc7\\u7a0b\\u4e2d\\uff0c\\u6211\\u4eec\\u9700\\u8981\\u9009\\u62e9\\u5408\\u9002\\u7684\\u5206\\u6790\\u65b9\\u6cd5\\u548c\\u5de5\\u5177\\uff0c\\u6839\\u636e\\u6570\\u636e\\u7684\\u7c7b\\u578b\\u548c\\u5206\\u6790\\u7684\\u76ee\\u7684\\u6765\\u786e\\u5b9a\\u5177\\u4f53\\u7684\\u5206\\u6790\\u7b56\\u7565\\u3002\"}, {\"cell_type\": \"markdown\", \"source\": \"## 1.2 \\u6570\\u636e\\u7c7b\\u578b\\u4e0e\\u6570\\u636e\\u7ed3\\u6784\\n\\n\\u5728\\u6570\\u636e\\u5206\\u6790\\u4e2d\\uff0c\\u4e86\\u89e3\\u6570\\u636e\\u7684\\u7c7b\\u578b\\u548c\\u7ed3\\u6784\\u662f\\u975e\\u5e38\\u91cd\\u8981\\u7684\\u3002\\u5e38\\u89c1\\u7684\\u6570\\u636e\\u7c7b\\u578b\\u5305\\u62ec\\u6570\\u503c\\u578b\\u6570\\u636e\\uff08\\u5982\\u6574\\u6570\\u3001\\u6d6e\\u70b9\\u6570\\uff09\\u3001\\u5206\\u7c7b\\u578b\\u6570\\u636e\\uff08\\u5982\\u6027\\u522b\\u3001\\u804c\\u4e1a\\uff09\\u3001\\u6709\\u5e8f\\u578b\\u6570\\u636e\\uff08\\u5982\\u8bc4\\u5206\\u7b49\\u7ea7\\uff09\\u7b49\\u3002\\u4e0d\\u540c\\u7c7b\\u578b\\u7684\\u6570\\u636e\\u9700\\u8981\\u91c7\\u7528\\u4e0d\\u540c\\u7684\\u5206\\u6790\\u65b9\\u6cd5\\u548c\\u5904\\u7406\\u65b9\\u5f0f\\u3002\\n\\n\\u6570\\u636e\\u7ed3\\u6784\\u662f\\u6307\\u6570\\u636e\\u7684\\u7ec4\\u7ec7\\u65b9\\u5f0f\\uff0c\\u5e38\\u89c1\\u7684\\u6570\\u636e\\u7ed3\\u6784\\u5305\\u62ec\\u8868\\u683c\\u6570\\u636e\\u3001\\u65f6\\u95f4\\u5e8f\\u5217\\u6570\\u636e\\u3001\\u6587\\u672c\\u6570\\u636e\\u7b49\\u3002\\u8868\\u683c\\u6570\\u636e\\u662f\\u6700\\u5e38\\u89c1\\u7684\\u6570\\u636e\\u7ed3\\u6784\\uff0c\\u5b83\\u7531\\u884c\\u548c\\u5217\\u7ec4\\u6210\\uff0c\\u6bcf\\u4e00\\u884c\\u4ee3\\u8868\\u4e00\\u4e2a\\u89c2\\u5bdf\\u5bf9\\u8c61\\uff0c\\u6bcf\\u4e00\\u5217\\u4ee3\\u8868\\u4e00\\u4e2a\\u5c5e\\u6027\\u3002\"}, {\"cell_type\": \"code\", \"source\": \"# \\u4f7f\\u7528Pandas\\u8fdb\\u884c\\u57fa\\u672c\\u6570\\u636e\\u64cd\\u4f5c\\nimport pandas as pd\\ndef basic_data_operations(df):\\n    print(\'\\u6570\\u636e\\u57fa\\u672c\\u4fe1\\u606f:\')\\n    print(df.info())\\n    print(\'\\n\\u6570\\u636e\\u524d5\\u884c:\')\\n    print(df.head())\\n    print(\'\\n\\u6570\\u636e\\u7edf\\u8ba1\\u6458\\u8981:\')\\n    print(df.describe())\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# \\u6570\\u636e\\u6e05\\u6d17\\u793a\\u4f8b\\nimport pandas as pd\\ndef handle_missing_values(df):\\n    print(\'\\u7f3a\\u5931\\u503c\\u7edf\\u8ba1:\')\\n    print(df.isnull().sum())\\n    # \\u586b\\u5145\\u6570\\u503c\\u578b\\u7f3a\\u5931\\u503c\\n    numeric_cols = df.select_dtypes(include=[\'float64\', \'int64\']).columns\\n    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())\\n    return df\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python\", \"language\": \"python\", \"name\": \"python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '0', '1', null);
INSERT INTO books_chapter VALUES ('5', '第2章 数据分析方法与应用', 'reading', '60', '本章详细讲解数据预处理技术，包括数据清洗、转换和特征工程的核心方法。', null, null, 'python', '2', '2026-01-05 09:01:21.744756', '2026-01-05 09:01:21.744756', '2', null, 'jupyter', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 2.1 描述性统计分析\\n\\n描述性统计分析是数据分析的基础，它通过计算各种统计量来描述数据的基本特征。常见的描述性统计量包括均值、中位数、众数、标准差、方差、四分位数等。这些统计量可以帮助我们了解数据的集中趋势、离散程度和分布特征。\\n\\n对于非计算机专业学生来说，掌握基本的描述性统计分析方法可以帮助我们初步了解数据的特征和规律。在Python中，我们可以使用NumPy和Pandas等库来计算各种描述性统计量。\"}, {\"cell_type\": \"markdown\", \"source\": \"## 2.2 相关性分析与回归分析\\n\\n相关性分析是研究两个或多个变量之间关系的统计方法。常见的相关性分析方法包括皮尔逊相关系数、斯皮尔曼等级相关系数等。这些方法可以帮助我们了解变量之间的相关程度和方向。\\n\\n回归分析是一种用于研究变量之间因果关系的统计方法，它通过建立回归模型来预测或解释变量之间的关系。常见的回归分析方法包括线性回归、多元线性回归、逻辑回归等。\"}, {\"cell_type\": \"code\", \"source\": \"# 描述性统计分析示例\\nimport pandas as pd\\nimport numpy as np\\ndef calculate_stats(data):\\n    df = pd.DataFrame(data)\\n    print(\'基本统计摘要:\')\\n    print(df.describe())\\n    print(\'\\n偏度:\', df.skew())\\n    print(\'峰度:\', df.kurtosis())\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# 相关性分析示例\\nimport pandas as pd\\ndef correlation_analysis(df):\\n    corr_matrix = df.corr()\\n    print(\'相关性矩阵:\')\\n    print(corr_matrix)\\n    return corr_matrix\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 2.1 \\u63cf\\u8ff0\\u6027\\u7edf\\u8ba1\\u5206\\u6790\\n\\n\\u63cf\\u8ff0\\u6027\\u7edf\\u8ba1\\u5206\\u6790\\u662f\\u6570\\u636e\\u5206\\u6790\\u7684\\u57fa\\u7840\\uff0c\\u5b83\\u901a\\u8fc7\\u8ba1\\u7b97\\u5404\\u79cd\\u7edf\\u8ba1\\u91cf\\u6765\\u63cf\\u8ff0\\u6570\\u636e\\u7684\\u57fa\\u672c\\u7279\\u5f81\\u3002\\u5e38\\u89c1\\u7684\\u63cf\\u8ff0\\u6027\\u7edf\\u8ba1\\u91cf\\u5305\\u62ec\\u5747\\u503c\\u3001\\u4e2d\\u4f4d\\u6570\\u3001\\u4f17\\u6570\\u3001\\u6807\\u51c6\\u5dee\\u3001\\u65b9\\u5dee\\u3001\\u56db\\u5206\\u4f4d\\u6570\\u7b49\\u3002\\u8fd9\\u4e9b\\u7edf\\u8ba1\\u91cf\\u53ef\\u4ee5\\u5e2e\\u52a9\\u6211\\u4eec\\u4e86\\u89e3\\u6570\\u636e\\u7684\\u96c6\\u4e2d\\u8d8b\\u52bf\\u3001\\u79bb\\u6563\\u7a0b\\u5ea6\\u548c\\u5206\\u5e03\\u7279\\u5f81\\u3002\\n\\n\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u638c\\u63e1\\u57fa\\u672c\\u7684\\u63cf\\u8ff0\\u6027\\u7edf\\u8ba1\\u5206\\u6790\\u65b9\\u6cd5\\u53ef\\u4ee5\\u5e2e\\u52a9\\u6211\\u4eec\\u521d\\u6b65\\u4e86\\u89e3\\u6570\\u636e\\u7684\\u7279\\u5f81\\u548c\\u89c4\\u5f8b\\u3002\\u5728Python\\u4e2d\\uff0c\\u6211\\u4eec\\u53ef\\u4ee5\\u4f7f\\u7528NumPy\\u548cPandas\\u7b49\\u5e93\\u6765\\u8ba1\\u7b97\\u5404\\u79cd\\u63cf\\u8ff0\\u6027\\u7edf\\u8ba1\\u91cf\\u3002\"}, {\"cell_type\": \"markdown\", \"source\": \"## 2.2 \\u76f8\\u5173\\u6027\\u5206\\u6790\\u4e0e\\u56de\\u5f52\\u5206\\u6790\\n\\n\\u76f8\\u5173\\u6027\\u5206\\u6790\\u662f\\u7814\\u7a76\\u4e24\\u4e2a\\u6216\\u591a\\u4e2a\\u53d8\\u91cf\\u4e4b\\u95f4\\u5173\\u7cfb\\u7684\\u7edf\\u8ba1\\u65b9\\u6cd5\\u3002\\u5e38\\u89c1\\u7684\\u76f8\\u5173\\u6027\\u5206\\u6790\\u65b9\\u6cd5\\u5305\\u62ec\\u76ae\\u5c14\\u900a\\u76f8\\u5173\\u7cfb\\u6570\\u3001\\u65af\\u76ae\\u5c14\\u66fc\\u7b49\\u7ea7\\u76f8\\u5173\\u7cfb\\u6570\\u7b49\\u3002\\u8fd9\\u4e9b\\u65b9\\u6cd5\\u53ef\\u4ee5\\u5e2e\\u52a9\\u6211\\u4eec\\u4e86\\u89e3\\u53d8\\u91cf\\u4e4b\\u95f4\\u7684\\u76f8\\u5173\\u7a0b\\u5ea6\\u548c\\u65b9\\u5411\\u3002\\n\\n\\u56de\\u5f52\\u5206\\u6790\\u662f\\u4e00\\u79cd\\u7528\\u4e8e\\u7814\\u7a76\\u53d8\\u91cf\\u4e4b\\u95f4\\u56e0\\u679c\\u5173\\u7cfb\\u7684\\u7edf\\u8ba1\\u65b9\\u6cd5\\uff0c\\u5b83\\u901a\\u8fc7\\u5efa\\u7acb\\u56de\\u5f52\\u6a21\\u578b\\u6765\\u9884\\u6d4b\\u6216\\u89e3\\u91ca\\u53d8\\u91cf\\u4e4b\\u95f4\\u7684\\u5173\\u7cfb\\u3002\\u5e38\\u89c1\\u7684\\u56de\\u5f52\\u5206\\u6790\\u65b9\\u6cd5\\u5305\\u62ec\\u7ebf\\u6027\\u56de\\u5f52\\u3001\\u591a\\u5143\\u7ebf\\u6027\\u56de\\u5f52\\u3001\\u903b\\u8f91\\u56de\\u5f52\\u7b49\\u3002\"}, {\"cell_type\": \"code\", \"source\": \"# \\u63cf\\u8ff0\\u6027\\u7edf\\u8ba1\\u5206\\u6790\\u793a\\u4f8b\\nimport pandas as pd\\nimport numpy as np\\ndef calculate_stats(data):\\n    df = pd.DataFrame(data)\\n    print(\'\\u57fa\\u672c\\u7edf\\u8ba1\\u6458\\u8981:\')\\n    print(df.describe())\\n    print(\'\\n\\u504f\\u5ea6:\', df.skew())\\n    print(\'\\u5cf0\\u5ea6:\', df.kurtosis())\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# \\u76f8\\u5173\\u6027\\u5206\\u6790\\u793a\\u4f8b\\nimport pandas as pd\\ndef correlation_analysis(df):\\n    corr_matrix = df.corr()\\n    print(\'\\u76f8\\u5173\\u6027\\u77e9\\u9635:\')\\n    print(corr_matrix)\\n    return corr_matrix\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python\", \"language\": \"python\", \"name\": \"python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '0', '1', null);
INSERT INTO books_chapter VALUES ('6', '第3章 数据可视化技术', 'reading', '60', '本章介绍数据可视化的基本原理和常用工具，学习如何有效展示数据 insights。', null, null, 'python', '3', '2026-01-05 09:01:21.754267', '2026-01-05 09:01:21.754267', '2', null, 'jupyter', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 3.1 数据可视化概述\\n\\n数据可视化是指将数据以图形或图像的形式呈现出来的技术。它可以帮助我们直观地理解数据的特征、趋势和关系，发现数据中隐藏的模式和规律。对于非计算机专业学生来说，掌握基本的数据可视化技能可以帮助我们更有效地展示和传达数据分析的结果。\\n\\n数据可视化的主要类型包括条形图、饼图、折线图、散点图、直方图、箱线图等。不同类型的图表适用于不同的数据类型和分析目的。\"}, {\"cell_type\": \"markdown\", \"source\": \"## 3.2 常用图表类型及应用\\n\\n条形图是最常见的数据可视化图表之一，它用矩形条的长度来表示数据的大小。条形图可以水平或垂直绘制，适用于比较不同类别的数据。在实际应用中，条形图常用于展示不同产品的销售额、不同地区的人口数量等比较数据。\\n\\n饼图用圆形和扇形来展示数据，其中圆形代表整体，扇形代表部分。饼图适用于展示部分与整体的关系，例如不同产品销售额占总销售额的比例、不同专业学生人数占总人数的比例等。\"}, {\"cell_type\": \"code\", \"source\": \"# 基本图表绘制示例\\nimport matplotlib.pyplot as plt\\ndef plot_bar_chart(labels, values):\\n    plt.figure(figsize=(10, 6))\\n    plt.bar(labels, values, color=\'skyblue\')\\n    plt.title(\'条形图示例\')\\n    plt.xlabel(\'类别\')\\n    plt.ylabel(\'数值\')\\n    plt.grid(axis=\'y\')\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# 折线图绘制示例\\nimport matplotlib.pyplot as plt\\ndef plot_line_chart(x_values, y_values):\\n    plt.figure(figsize=(10, 6))\\n    plt.plot(x_values, y_values, marker=\'o\', color=\'green\')\\n    plt.title(\'折线图示例\')\\n    plt.xlabel(\'X轴\')\\n    plt.ylabel(\'Y轴\')\\n    plt.grid(True)\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 3.1 \\u6570\\u636e\\u53ef\\u89c6\\u5316\\u6982\\u8ff0\\n\\n\\u6570\\u636e\\u53ef\\u89c6\\u5316\\u662f\\u6307\\u5c06\\u6570\\u636e\\u4ee5\\u56fe\\u5f62\\u6216\\u56fe\\u50cf\\u7684\\u5f62\\u5f0f\\u5448\\u73b0\\u51fa\\u6765\\u7684\\u6280\\u672f\\u3002\\u5b83\\u53ef\\u4ee5\\u5e2e\\u52a9\\u6211\\u4eec\\u76f4\\u89c2\\u5730\\u7406\\u89e3\\u6570\\u636e\\u7684\\u7279\\u5f81\\u3001\\u8d8b\\u52bf\\u548c\\u5173\\u7cfb\\uff0c\\u53d1\\u73b0\\u6570\\u636e\\u4e2d\\u9690\\u85cf\\u7684\\u6a21\\u5f0f\\u548c\\u89c4\\u5f8b\\u3002\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u638c\\u63e1\\u57fa\\u672c\\u7684\\u6570\\u636e\\u53ef\\u89c6\\u5316\\u6280\\u80fd\\u53ef\\u4ee5\\u5e2e\\u52a9\\u6211\\u4eec\\u66f4\\u6709\\u6548\\u5730\\u5c55\\u793a\\u548c\\u4f20\\u8fbe\\u6570\\u636e\\u5206\\u6790\\u7684\\u7ed3\\u679c\\u3002\\n\\n\\u6570\\u636e\\u53ef\\u89c6\\u5316\\u7684\\u4e3b\\u8981\\u7c7b\\u578b\\u5305\\u62ec\\u6761\\u5f62\\u56fe\\u3001\\u997c\\u56fe\\u3001\\u6298\\u7ebf\\u56fe\\u3001\\u6563\\u70b9\\u56fe\\u3001\\u76f4\\u65b9\\u56fe\\u3001\\u7bb1\\u7ebf\\u56fe\\u7b49\\u3002\\u4e0d\\u540c\\u7c7b\\u578b\\u7684\\u56fe\\u8868\\u9002\\u7528\\u4e8e\\u4e0d\\u540c\\u7684\\u6570\\u636e\\u7c7b\\u578b\\u548c\\u5206\\u6790\\u76ee\\u7684\\u3002\"}, {\"cell_type\": \"markdown\", \"source\": \"## 3.2 \\u5e38\\u7528\\u56fe\\u8868\\u7c7b\\u578b\\u53ca\\u5e94\\u7528\\n\\n\\u6761\\u5f62\\u56fe\\u662f\\u6700\\u5e38\\u89c1\\u7684\\u6570\\u636e\\u53ef\\u89c6\\u5316\\u56fe\\u8868\\u4e4b\\u4e00\\uff0c\\u5b83\\u7528\\u77e9\\u5f62\\u6761\\u7684\\u957f\\u5ea6\\u6765\\u8868\\u793a\\u6570\\u636e\\u7684\\u5927\\u5c0f\\u3002\\u6761\\u5f62\\u56fe\\u53ef\\u4ee5\\u6c34\\u5e73\\u6216\\u5782\\u76f4\\u7ed8\\u5236\\uff0c\\u9002\\u7528\\u4e8e\\u6bd4\\u8f83\\u4e0d\\u540c\\u7c7b\\u522b\\u7684\\u6570\\u636e\\u3002\\u5728\\u5b9e\\u9645\\u5e94\\u7528\\u4e2d\\uff0c\\u6761\\u5f62\\u56fe\\u5e38\\u7528\\u4e8e\\u5c55\\u793a\\u4e0d\\u540c\\u4ea7\\u54c1\\u7684\\u9500\\u552e\\u989d\\u3001\\u4e0d\\u540c\\u5730\\u533a\\u7684\\u4eba\\u53e3\\u6570\\u91cf\\u7b49\\u6bd4\\u8f83\\u6570\\u636e\\u3002\\n\\n\\u997c\\u56fe\\u7528\\u5706\\u5f62\\u548c\\u6247\\u5f62\\u6765\\u5c55\\u793a\\u6570\\u636e\\uff0c\\u5176\\u4e2d\\u5706\\u5f62\\u4ee3\\u8868\\u6574\\u4f53\\uff0c\\u6247\\u5f62\\u4ee3\\u8868\\u90e8\\u5206\\u3002\\u997c\\u56fe\\u9002\\u7528\\u4e8e\\u5c55\\u793a\\u90e8\\u5206\\u4e0e\\u6574\\u4f53\\u7684\\u5173\\u7cfb\\uff0c\\u4f8b\\u5982\\u4e0d\\u540c\\u4ea7\\u54c1\\u9500\\u552e\\u989d\\u5360\\u603b\\u9500\\u552e\\u989d\\u7684\\u6bd4\\u4f8b\\u3001\\u4e0d\\u540c\\u4e13\\u4e1a\\u5b66\\u751f\\u4eba\\u6570\\u5360\\u603b\\u4eba\\u6570\\u7684\\u6bd4\\u4f8b\\u7b49\\u3002\"}, {\"cell_type\": \"code\", \"source\": \"# \\u57fa\\u672c\\u56fe\\u8868\\u7ed8\\u5236\\u793a\\u4f8b\\nimport matplotlib.pyplot as plt\\ndef plot_bar_chart(labels, values):\\n    plt.figure(figsize=(10, 6))\\n    plt.bar(labels, values, color=\'skyblue\')\\n    plt.title(\'\\u6761\\u5f62\\u56fe\\u793a\\u4f8b\')\\n    plt.xlabel(\'\\u7c7b\\u522b\')\\n    plt.ylabel(\'\\u6570\\u503c\')\\n    plt.grid(axis=\'y\')\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# \\u6298\\u7ebf\\u56fe\\u7ed8\\u5236\\u793a\\u4f8b\\nimport matplotlib.pyplot as plt\\ndef plot_line_chart(x_values, y_values):\\n    plt.figure(figsize=(10, 6))\\n    plt.plot(x_values, y_values, marker=\'o\', color=\'green\')\\n    plt.title(\'\\u6298\\u7ebf\\u56fe\\u793a\\u4f8b\')\\n    plt.xlabel(\'X\\u8f74\')\\n    plt.ylabel(\'Y\\u8f74\')\\n    plt.grid(True)\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python\", \"language\": \"python\", \"name\": \"python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '0', '1', null);
INSERT INTO books_chapter VALUES ('7', '第1章 人工智能概述', 'reading', '60', '本章介绍人工智能的基本概念、发展历程和应用领域，帮助读者了解AI的全貌。', null, null, 'python', '1', '2026-01-05 09:01:21.743232', '2026-01-05 09:01:21.743232', '3', null, 'jupyter', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 1.1 人工智能的定义与发展历程\\n\\n人工智能（Artificial Intelligence，简称AI）是指由人制造出来的系统所表现出来的智能。人工智能的目标是让机器能够模拟人类的智能行为，如感知、推理、学习、决策等。对于非计算机专业学生来说，了解人工智能的基本概念和发展历程有助于我们更好地理解这一快速发展的技术领域。\\n\\n人工智能的发展大致可以分为三个阶段：第一阶段是人工智能的孕育期（1940s-1950s），这一时期主要是理论和技术的准备；第二阶段是人工智能的形成期（1950s-1960s），人工智能作为一个学科正式诞生；第三阶段是人工智能的发展期（1970s至今），人工智能经历了多次高潮和低谷，不断取得新的突破。\"}, {\"cell_type\": \"markdown\", \"source\": \"## 1.2 人工智能的主要领域与应用\\n\\n人工智能的应用领域非常广泛，涵盖了计算机视觉、自然语言处理、语音识别、专家系统、智能机器人等多个方面。计算机视觉是让计算机能够理解和解释图像或视频的技术，应用于人脸识别、物体检测、图像分割等任务；自然语言处理是让计算机能够理解和生成人类语言的技术，应用于机器翻译、情感分析、文本摘要等任务。\"}, {\"cell_type\": \"code\", \"source\": \"# 简单的智能对话机器人示例\\ndef simple_chatbot():\\n    responses = {\\n        \'你好\': \'你好！很高兴见到你！\',\\n        \'你是谁\': \'我是一个简单的对话机器人。\',\\n        \'什么是人工智能\': \'人工智能是指由人制造出来的系统所表现出来的智能。\'\\n    }\\n    return responses\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# 文本分类简单示例\\ndef simple_text_classifier(text):\\n    positive_words = [\'好\', \'棒\', \'优秀\', \'喜欢\']\\n    negative_words = [\'差\', \'糟糕\', \'失望\', \'不满意\']\\n    positive_count = sum(1 for word in positive_words if word in text)\\n    negative_count = sum(1 for word in negative_words if word in text)\\n    if positive_count > negative_count:\\n        return \'正面评价\'\\n    elif negative_count > positive_count:\\n        return \'负面评价\'\\n    else:\\n        return \'中性评价\'\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 1.1 \\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u5b9a\\u4e49\\u4e0e\\u53d1\\u5c55\\u5386\\u7a0b\\n\\n\\u4eba\\u5de5\\u667a\\u80fd\\uff08Artificial Intelligence\\uff0c\\u7b80\\u79f0AI\\uff09\\u662f\\u6307\\u7531\\u4eba\\u5236\\u9020\\u51fa\\u6765\\u7684\\u7cfb\\u7edf\\u6240\\u8868\\u73b0\\u51fa\\u6765\\u7684\\u667a\\u80fd\\u3002\\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u76ee\\u6807\\u662f\\u8ba9\\u673a\\u5668\\u80fd\\u591f\\u6a21\\u62df\\u4eba\\u7c7b\\u7684\\u667a\\u80fd\\u884c\\u4e3a\\uff0c\\u5982\\u611f\\u77e5\\u3001\\u63a8\\u7406\\u3001\\u5b66\\u4e60\\u3001\\u51b3\\u7b56\\u7b49\\u3002\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u4e86\\u89e3\\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u57fa\\u672c\\u6982\\u5ff5\\u548c\\u53d1\\u5c55\\u5386\\u7a0b\\u6709\\u52a9\\u4e8e\\u6211\\u4eec\\u66f4\\u597d\\u5730\\u7406\\u89e3\\u8fd9\\u4e00\\u5feb\\u901f\\u53d1\\u5c55\\u7684\\u6280\\u672f\\u9886\\u57df\\u3002\\n\\n\\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u53d1\\u5c55\\u5927\\u81f4\\u53ef\\u4ee5\\u5206\\u4e3a\\u4e09\\u4e2a\\u9636\\u6bb5\\uff1a\\u7b2c\\u4e00\\u9636\\u6bb5\\u662f\\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u5b55\\u80b2\\u671f\\uff081940s-1950s\\uff09\\uff0c\\u8fd9\\u4e00\\u65f6\\u671f\\u4e3b\\u8981\\u662f\\u7406\\u8bba\\u548c\\u6280\\u672f\\u7684\\u51c6\\u5907\\uff1b\\u7b2c\\u4e8c\\u9636\\u6bb5\\u662f\\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u5f62\\u6210\\u671f\\uff081950s-1960s\\uff09\\uff0c\\u4eba\\u5de5\\u667a\\u80fd\\u4f5c\\u4e3a\\u4e00\\u4e2a\\u5b66\\u79d1\\u6b63\\u5f0f\\u8bde\\u751f\\uff1b\\u7b2c\\u4e09\\u9636\\u6bb5\\u662f\\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u53d1\\u5c55\\u671f\\uff081970s\\u81f3\\u4eca\\uff09\\uff0c\\u4eba\\u5de5\\u667a\\u80fd\\u7ecf\\u5386\\u4e86\\u591a\\u6b21\\u9ad8\\u6f6e\\u548c\\u4f4e\\u8c37\\uff0c\\u4e0d\\u65ad\\u53d6\\u5f97\\u65b0\\u7684\\u7a81\\u7834\\u3002\"}, {\"cell_type\": \"markdown\", \"source\": \"## 1.2 \\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u4e3b\\u8981\\u9886\\u57df\\u4e0e\\u5e94\\u7528\\n\\n\\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u5e94\\u7528\\u9886\\u57df\\u975e\\u5e38\\u5e7f\\u6cdb\\uff0c\\u6db5\\u76d6\\u4e86\\u8ba1\\u7b97\\u673a\\u89c6\\u89c9\\u3001\\u81ea\\u7136\\u8bed\\u8a00\\u5904\\u7406\\u3001\\u8bed\\u97f3\\u8bc6\\u522b\\u3001\\u4e13\\u5bb6\\u7cfb\\u7edf\\u3001\\u667a\\u80fd\\u673a\\u5668\\u4eba\\u7b49\\u591a\\u4e2a\\u65b9\\u9762\\u3002\\u8ba1\\u7b97\\u673a\\u89c6\\u89c9\\u662f\\u8ba9\\u8ba1\\u7b97\\u673a\\u80fd\\u591f\\u7406\\u89e3\\u548c\\u89e3\\u91ca\\u56fe\\u50cf\\u6216\\u89c6\\u9891\\u7684\\u6280\\u672f\\uff0c\\u5e94\\u7528\\u4e8e\\u4eba\\u8138\\u8bc6\\u522b\\u3001\\u7269\\u4f53\\u68c0\\u6d4b\\u3001\\u56fe\\u50cf\\u5206\\u5272\\u7b49\\u4efb\\u52a1\\uff1b\\u81ea\\u7136\\u8bed\\u8a00\\u5904\\u7406\\u662f\\u8ba9\\u8ba1\\u7b97\\u673a\\u80fd\\u591f\\u7406\\u89e3\\u548c\\u751f\\u6210\\u4eba\\u7c7b\\u8bed\\u8a00\\u7684\\u6280\\u672f\\uff0c\\u5e94\\u7528\\u4e8e\\u673a\\u5668\\u7ffb\\u8bd1\\u3001\\u60c5\\u611f\\u5206\\u6790\\u3001\\u6587\\u672c\\u6458\\u8981\\u7b49\\u4efb\\u52a1\\u3002\"}, {\"cell_type\": \"code\", \"source\": \"# \\u7b80\\u5355\\u7684\\u667a\\u80fd\\u5bf9\\u8bdd\\u673a\\u5668\\u4eba\\u793a\\u4f8b\\ndef simple_chatbot():\\n    responses = {\\n        \'\\u4f60\\u597d\': \'\\u4f60\\u597d\\uff01\\u5f88\\u9ad8\\u5174\\u89c1\\u5230\\u4f60\\uff01\',\\n        \'\\u4f60\\u662f\\u8c01\': \'\\u6211\\u662f\\u4e00\\u4e2a\\u7b80\\u5355\\u7684\\u5bf9\\u8bdd\\u673a\\u5668\\u4eba\\u3002\',\\n        \'\\u4ec0\\u4e48\\u662f\\u4eba\\u5de5\\u667a\\u80fd\': \'\\u4eba\\u5de5\\u667a\\u80fd\\u662f\\u6307\\u7531\\u4eba\\u5236\\u9020\\u51fa\\u6765\\u7684\\u7cfb\\u7edf\\u6240\\u8868\\u73b0\\u51fa\\u6765\\u7684\\u667a\\u80fd\\u3002\'\\n    }\\n    return responses\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# \\u6587\\u672c\\u5206\\u7c7b\\u7b80\\u5355\\u793a\\u4f8b\\ndef simple_text_classifier(text):\\n    positive_words = [\'\\u597d\', \'\\u68d2\', \'\\u4f18\\u79c0\', \'\\u559c\\u6b22\']\\n    negative_words = [\'\\u5dee\', \'\\u7cdf\\u7cd5\', \'\\u5931\\u671b\', \'\\u4e0d\\u6ee1\\u610f\']\\n    positive_count = sum(1 for word in positive_words if word in text)\\n    negative_count = sum(1 for word in negative_words if word in text)\\n    if positive_count > negative_count:\\n        return \'\\u6b63\\u9762\\u8bc4\\u4ef7\'\\n    elif negative_count > positive_count:\\n        return \'\\u8d1f\\u9762\\u8bc4\\u4ef7\'\\n    else:\\n        return \'\\u4e2d\\u6027\\u8bc4\\u4ef7\'\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python\", \"language\": \"python\", \"name\": \"python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '0', '1', null);
INSERT INTO books_chapter VALUES ('8', '第2章 机器学习基础', 'reading', '60', '本章详细讲解机器学习的基本原理和常用算法，包括监督学习和无监督学习。', null, null, 'python', '2', '2026-01-05 09:01:21.749382', '2026-01-05 09:01:21.749382', '3', null, 'jupyter', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 2.1 机器学习的基本概念\\n\\n机器学习是人工智能的一个重要分支，它是一门研究如何使计算机系统通过经验自动改进的学科。机器学习的核心思想是让计算机从数据中学习规律，而不需要显式地编程指定规则。对于非计算机专业学生来说，了解机器学习的基本概念有助于我们理解人工智能技术的工作原理。\\n\\n机器学习的主要类型包括监督学习、无监督学习和强化学习等。监督学习是从标记数据中学习的方法，常见的任务包括分类和回归；无监督学习是从未标记数据中学习的方法，常见的任务包括聚类和降维；强化学习是通过与环境交互并接收奖惩信号来学习的方法，适用于决策和控制类任务。\"}, {\"cell_type\": \"markdown\", \"source\": \"## 2.2 机器学习算法简介\\n\\n线性回归是最基本的机器学习算法之一，它用于建模自变量和因变量之间的线性关系。线性回归假设自变量和因变量之间存在线性关系，通过最小化预测值和实际值之间的误差来学习模型参数。线性回归在房价预测、销售预测等问题中有着广泛的应用。\\n\\n决策树是一种基于树结构的分类和回归算法，它通过对特征进行递归分割来构建决策树。决策树具有直观、易于理解的特点，在医疗诊断、风险评估等领域有着广泛的应用。\"}, {\"cell_type\": \"code\", \"source\": \"# 简单线性回归示例\\nimport numpy as np\\ndef simple_linear_regression(x, y):\\n    x_mean = np.mean(x)\\n    y_mean = np.mean(y)\\n    numerator = np.sum((x - x_mean) * (y - y_mean))\\n    denominator = np.sum((x - x_mean) ** 2)\\n    slope = numerator / denominator\\n    intercept = y_mean - slope * x_mean\\n    return slope, intercept\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# K-means聚类简单示例\\nimport numpy as np\\ndef kmeans_sample():\\n    print(\'K-means聚类是一种无监督学习算法，用于将数据分成多个簇。\')\\n    print(\'算法步骤：\')\\n    print(\'1. 随机选择K个聚类中心\')\\n    print(\'2. 将每个数据点分配到最近的聚类中心\')\\n    print(\'3. 更新聚类中心为每个簇的均值\')\\n    print(\'4. 重复步骤2和3直到收敛\')\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 2.1 \\u673a\\u5668\\u5b66\\u4e60\\u7684\\u57fa\\u672c\\u6982\\u5ff5\\n\\n\\u673a\\u5668\\u5b66\\u4e60\\u662f\\u4eba\\u5de5\\u667a\\u80fd\\u7684\\u4e00\\u4e2a\\u91cd\\u8981\\u5206\\u652f\\uff0c\\u5b83\\u662f\\u4e00\\u95e8\\u7814\\u7a76\\u5982\\u4f55\\u4f7f\\u8ba1\\u7b97\\u673a\\u7cfb\\u7edf\\u901a\\u8fc7\\u7ecf\\u9a8c\\u81ea\\u52a8\\u6539\\u8fdb\\u7684\\u5b66\\u79d1\\u3002\\u673a\\u5668\\u5b66\\u4e60\\u7684\\u6838\\u5fc3\\u601d\\u60f3\\u662f\\u8ba9\\u8ba1\\u7b97\\u673a\\u4ece\\u6570\\u636e\\u4e2d\\u5b66\\u4e60\\u89c4\\u5f8b\\uff0c\\u800c\\u4e0d\\u9700\\u8981\\u663e\\u5f0f\\u5730\\u7f16\\u7a0b\\u6307\\u5b9a\\u89c4\\u5219\\u3002\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u4e86\\u89e3\\u673a\\u5668\\u5b66\\u4e60\\u7684\\u57fa\\u672c\\u6982\\u5ff5\\u6709\\u52a9\\u4e8e\\u6211\\u4eec\\u7406\\u89e3\\u4eba\\u5de5\\u667a\\u80fd\\u6280\\u672f\\u7684\\u5de5\\u4f5c\\u539f\\u7406\\u3002\\n\\n\\u673a\\u5668\\u5b66\\u4e60\\u7684\\u4e3b\\u8981\\u7c7b\\u578b\\u5305\\u62ec\\u76d1\\u7763\\u5b66\\u4e60\\u3001\\u65e0\\u76d1\\u7763\\u5b66\\u4e60\\u548c\\u5f3a\\u5316\\u5b66\\u4e60\\u7b49\\u3002\\u76d1\\u7763\\u5b66\\u4e60\\u662f\\u4ece\\u6807\\u8bb0\\u6570\\u636e\\u4e2d\\u5b66\\u4e60\\u7684\\u65b9\\u6cd5\\uff0c\\u5e38\\u89c1\\u7684\\u4efb\\u52a1\\u5305\\u62ec\\u5206\\u7c7b\\u548c\\u56de\\u5f52\\uff1b\\u65e0\\u76d1\\u7763\\u5b66\\u4e60\\u662f\\u4ece\\u672a\\u6807\\u8bb0\\u6570\\u636e\\u4e2d\\u5b66\\u4e60\\u7684\\u65b9\\u6cd5\\uff0c\\u5e38\\u89c1\\u7684\\u4efb\\u52a1\\u5305\\u62ec\\u805a\\u7c7b\\u548c\\u964d\\u7ef4\\uff1b\\u5f3a\\u5316\\u5b66\\u4e60\\u662f\\u901a\\u8fc7\\u4e0e\\u73af\\u5883\\u4ea4\\u4e92\\u5e76\\u63a5\\u6536\\u5956\\u60e9\\u4fe1\\u53f7\\u6765\\u5b66\\u4e60\\u7684\\u65b9\\u6cd5\\uff0c\\u9002\\u7528\\u4e8e\\u51b3\\u7b56\\u548c\\u63a7\\u5236\\u7c7b\\u4efb\\u52a1\\u3002\"}, {\"cell_type\": \"markdown\", \"source\": \"## 2.2 \\u673a\\u5668\\u5b66\\u4e60\\u7b97\\u6cd5\\u7b80\\u4ecb\\n\\n\\u7ebf\\u6027\\u56de\\u5f52\\u662f\\u6700\\u57fa\\u672c\\u7684\\u673a\\u5668\\u5b66\\u4e60\\u7b97\\u6cd5\\u4e4b\\u4e00\\uff0c\\u5b83\\u7528\\u4e8e\\u5efa\\u6a21\\u81ea\\u53d8\\u91cf\\u548c\\u56e0\\u53d8\\u91cf\\u4e4b\\u95f4\\u7684\\u7ebf\\u6027\\u5173\\u7cfb\\u3002\\u7ebf\\u6027\\u56de\\u5f52\\u5047\\u8bbe\\u81ea\\u53d8\\u91cf\\u548c\\u56e0\\u53d8\\u91cf\\u4e4b\\u95f4\\u5b58\\u5728\\u7ebf\\u6027\\u5173\\u7cfb\\uff0c\\u901a\\u8fc7\\u6700\\u5c0f\\u5316\\u9884\\u6d4b\\u503c\\u548c\\u5b9e\\u9645\\u503c\\u4e4b\\u95f4\\u7684\\u8bef\\u5dee\\u6765\\u5b66\\u4e60\\u6a21\\u578b\\u53c2\\u6570\\u3002\\u7ebf\\u6027\\u56de\\u5f52\\u5728\\u623f\\u4ef7\\u9884\\u6d4b\\u3001\\u9500\\u552e\\u9884\\u6d4b\\u7b49\\u95ee\\u9898\\u4e2d\\u6709\\u7740\\u5e7f\\u6cdb\\u7684\\u5e94\\u7528\\u3002\\n\\n\\u51b3\\u7b56\\u6811\\u662f\\u4e00\\u79cd\\u57fa\\u4e8e\\u6811\\u7ed3\\u6784\\u7684\\u5206\\u7c7b\\u548c\\u56de\\u5f52\\u7b97\\u6cd5\\uff0c\\u5b83\\u901a\\u8fc7\\u5bf9\\u7279\\u5f81\\u8fdb\\u884c\\u9012\\u5f52\\u5206\\u5272\\u6765\\u6784\\u5efa\\u51b3\\u7b56\\u6811\\u3002\\u51b3\\u7b56\\u6811\\u5177\\u6709\\u76f4\\u89c2\\u3001\\u6613\\u4e8e\\u7406\\u89e3\\u7684\\u7279\\u70b9\\uff0c\\u5728\\u533b\\u7597\\u8bca\\u65ad\\u3001\\u98ce\\u9669\\u8bc4\\u4f30\\u7b49\\u9886\\u57df\\u6709\\u7740\\u5e7f\\u6cdb\\u7684\\u5e94\\u7528\\u3002\"}, {\"cell_type\": \"code\", \"source\": \"# \\u7b80\\u5355\\u7ebf\\u6027\\u56de\\u5f52\\u793a\\u4f8b\\nimport numpy as np\\ndef simple_linear_regression(x, y):\\n    x_mean = np.mean(x)\\n    y_mean = np.mean(y)\\n    numerator = np.sum((x - x_mean) * (y - y_mean))\\n    denominator = np.sum((x - x_mean) ** 2)\\n    slope = numerator / denominator\\n    intercept = y_mean - slope * x_mean\\n    return slope, intercept\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# K-means\\u805a\\u7c7b\\u7b80\\u5355\\u793a\\u4f8b\\nimport numpy as np\\ndef kmeans_sample():\\n    print(\'K-means\\u805a\\u7c7b\\u662f\\u4e00\\u79cd\\u65e0\\u76d1\\u7763\\u5b66\\u4e60\\u7b97\\u6cd5\\uff0c\\u7528\\u4e8e\\u5c06\\u6570\\u636e\\u5206\\u6210\\u591a\\u4e2a\\u7c07\\u3002\')\\n    print(\'\\u7b97\\u6cd5\\u6b65\\u9aa4\\uff1a\')\\n    print(\'1. \\u968f\\u673a\\u9009\\u62e9K\\u4e2a\\u805a\\u7c7b\\u4e2d\\u5fc3\')\\n    print(\'2. \\u5c06\\u6bcf\\u4e2a\\u6570\\u636e\\u70b9\\u5206\\u914d\\u5230\\u6700\\u8fd1\\u7684\\u805a\\u7c7b\\u4e2d\\u5fc3\')\\n    print(\'3. \\u66f4\\u65b0\\u805a\\u7c7b\\u4e2d\\u5fc3\\u4e3a\\u6bcf\\u4e2a\\u7c07\\u7684\\u5747\\u503c\')\\n    print(\'4. \\u91cd\\u590d\\u6b65\\u9aa42\\u548c3\\u76f4\\u5230\\u6536\\u655b\')\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python\", \"language\": \"python\", \"name\": \"python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '0', '1', null);
INSERT INTO books_chapter VALUES ('9', '第3章 深度学习入门', 'reading', '60', '本章介绍深度学习的核心概念和应用，包括神经网络基础和常用架构。', null, null, 'python', '3', '2026-01-05 09:01:21.757418', '2026-01-05 09:01:21.757418', '3', null, 'jupyter', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 3.1 神经网络基础\\n\\n神经网络是深度学习的基础，它是由大量人工神经元相互连接而成的计算模型，灵感来源于人脑的神经元结构。对于非计算机专业学生来说，了解神经网络的基本结构和工作原理有助于我们理解深度学习的核心概念。\\n\\n神经网络的基本组成单元是人工神经元，它接收多个输入信号，通过权重加权后求和，再经过激活函数处理后输出结果。多个神经元按层次结构组织，形成输入层、隐藏层和输出层。输入层接收原始数据；隐藏层负责特征提取和处理；输出层产生最终的预测结果。\"}, {\"cell_type\": \"markdown\", \"source\": \"## 3.2 深度学习应用与实践\\n\\n深度学习技术已经广泛应用于各个领域，取得了令人瞩目的成果。在计算机视觉领域，深度学习在图像分类、目标检测、图像分割、人脸识别等任务中取得了突破性进展；在自然语言处理领域，深度学习在机器翻译、文本分类、情感分析、问答系统、文本生成等任务中表现出色；在语音识别领域，深度学习大幅提高了语音识别的准确率。\"}, {\"cell_type\": \"code\", \"source\": \"# 神经网络基本结构示例\\ndef neural_network_structure():\\n    print(\'神经网络基本结构示例：\')\\n    print(\'输入层 -> 隐藏层 -> 输出层\')\\n    print(\'激活函数：ReLU, Sigmoid, Tanh等\')\\n    print(\'损失函数：MSE, Cross-Entropy等\')\\n    print(\'优化算法：SGD, Adam, RMSprop等\')\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# 深度学习应用领域\\ndef deep_learning_applications():\\n    applications = {\\n        \'计算机视觉\': [\'图像分类\', \'目标检测\', \'人脸识别\', \'图像生成\'],\\n        \'自然语言处理\': [\'机器翻译\', \'文本分类\', \'问答系统\', \'文本生成\'],\\n        \'语音识别\': [\'语音转文字\', \'语音合成\', \'声纹识别\'],\\n        \'推荐系统\': [\'商品推荐\', \'内容推荐\', \'个性化服务\']\\n    }\\n    return applications\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '{\"cells\": [{\"cell_type\": \"markdown\", \"source\": \"## 3.1 \\u795e\\u7ecf\\u7f51\\u7edc\\u57fa\\u7840\\n\\n\\u795e\\u7ecf\\u7f51\\u7edc\\u662f\\u6df1\\u5ea6\\u5b66\\u4e60\\u7684\\u57fa\\u7840\\uff0c\\u5b83\\u662f\\u7531\\u5927\\u91cf\\u4eba\\u5de5\\u795e\\u7ecf\\u5143\\u76f8\\u4e92\\u8fde\\u63a5\\u800c\\u6210\\u7684\\u8ba1\\u7b97\\u6a21\\u578b\\uff0c\\u7075\\u611f\\u6765\\u6e90\\u4e8e\\u4eba\\u8111\\u7684\\u795e\\u7ecf\\u5143\\u7ed3\\u6784\\u3002\\u5bf9\\u4e8e\\u975e\\u8ba1\\u7b97\\u673a\\u4e13\\u4e1a\\u5b66\\u751f\\u6765\\u8bf4\\uff0c\\u4e86\\u89e3\\u795e\\u7ecf\\u7f51\\u7edc\\u7684\\u57fa\\u672c\\u7ed3\\u6784\\u548c\\u5de5\\u4f5c\\u539f\\u7406\\u6709\\u52a9\\u4e8e\\u6211\\u4eec\\u7406\\u89e3\\u6df1\\u5ea6\\u5b66\\u4e60\\u7684\\u6838\\u5fc3\\u6982\\u5ff5\\u3002\\n\\n\\u795e\\u7ecf\\u7f51\\u7edc\\u7684\\u57fa\\u672c\\u7ec4\\u6210\\u5355\\u5143\\u662f\\u4eba\\u5de5\\u795e\\u7ecf\\u5143\\uff0c\\u5b83\\u63a5\\u6536\\u591a\\u4e2a\\u8f93\\u5165\\u4fe1\\u53f7\\uff0c\\u901a\\u8fc7\\u6743\\u91cd\\u52a0\\u6743\\u540e\\u6c42\\u548c\\uff0c\\u518d\\u7ecf\\u8fc7\\u6fc0\\u6d3b\\u51fd\\u6570\\u5904\\u7406\\u540e\\u8f93\\u51fa\\u7ed3\\u679c\\u3002\\u591a\\u4e2a\\u795e\\u7ecf\\u5143\\u6309\\u5c42\\u6b21\\u7ed3\\u6784\\u7ec4\\u7ec7\\uff0c\\u5f62\\u6210\\u8f93\\u5165\\u5c42\\u3001\\u9690\\u85cf\\u5c42\\u548c\\u8f93\\u51fa\\u5c42\\u3002\\u8f93\\u5165\\u5c42\\u63a5\\u6536\\u539f\\u59cb\\u6570\\u636e\\uff1b\\u9690\\u85cf\\u5c42\\u8d1f\\u8d23\\u7279\\u5f81\\u63d0\\u53d6\\u548c\\u5904\\u7406\\uff1b\\u8f93\\u51fa\\u5c42\\u4ea7\\u751f\\u6700\\u7ec8\\u7684\\u9884\\u6d4b\\u7ed3\\u679c\\u3002\"}, {\"cell_type\": \"markdown\", \"source\": \"## 3.2 \\u6df1\\u5ea6\\u5b66\\u4e60\\u5e94\\u7528\\u4e0e\\u5b9e\\u8df5\\n\\n\\u6df1\\u5ea6\\u5b66\\u4e60\\u6280\\u672f\\u5df2\\u7ecf\\u5e7f\\u6cdb\\u5e94\\u7528\\u4e8e\\u5404\\u4e2a\\u9886\\u57df\\uff0c\\u53d6\\u5f97\\u4e86\\u4ee4\\u4eba\\u77a9\\u76ee\\u7684\\u6210\\u679c\\u3002\\u5728\\u8ba1\\u7b97\\u673a\\u89c6\\u89c9\\u9886\\u57df\\uff0c\\u6df1\\u5ea6\\u5b66\\u4e60\\u5728\\u56fe\\u50cf\\u5206\\u7c7b\\u3001\\u76ee\\u6807\\u68c0\\u6d4b\\u3001\\u56fe\\u50cf\\u5206\\u5272\\u3001\\u4eba\\u8138\\u8bc6\\u522b\\u7b49\\u4efb\\u52a1\\u4e2d\\u53d6\\u5f97\\u4e86\\u7a81\\u7834\\u6027\\u8fdb\\u5c55\\uff1b\\u5728\\u81ea\\u7136\\u8bed\\u8a00\\u5904\\u7406\\u9886\\u57df\\uff0c\\u6df1\\u5ea6\\u5b66\\u4e60\\u5728\\u673a\\u5668\\u7ffb\\u8bd1\\u3001\\u6587\\u672c\\u5206\\u7c7b\\u3001\\u60c5\\u611f\\u5206\\u6790\\u3001\\u95ee\\u7b54\\u7cfb\\u7edf\\u3001\\u6587\\u672c\\u751f\\u6210\\u7b49\\u4efb\\u52a1\\u4e2d\\u8868\\u73b0\\u51fa\\u8272\\uff1b\\u5728\\u8bed\\u97f3\\u8bc6\\u522b\\u9886\\u57df\\uff0c\\u6df1\\u5ea6\\u5b66\\u4e60\\u5927\\u5e45\\u63d0\\u9ad8\\u4e86\\u8bed\\u97f3\\u8bc6\\u522b\\u7684\\u51c6\\u786e\\u7387\\u3002\"}, {\"cell_type\": \"code\", \"source\": \"# \\u795e\\u7ecf\\u7f51\\u7edc\\u57fa\\u672c\\u7ed3\\u6784\\u793a\\u4f8b\\ndef neural_network_structure():\\n    print(\'\\u795e\\u7ecf\\u7f51\\u7edc\\u57fa\\u672c\\u7ed3\\u6784\\u793a\\u4f8b\\uff1a\')\\n    print(\'\\u8f93\\u5165\\u5c42 -> \\u9690\\u85cf\\u5c42 -> \\u8f93\\u51fa\\u5c42\')\\n    print(\'\\u6fc0\\u6d3b\\u51fd\\u6570\\uff1aReLU, Sigmoid, Tanh\\u7b49\')\\n    print(\'\\u635f\\u5931\\u51fd\\u6570\\uff1aMSE, Cross-Entropy\\u7b49\')\\n    print(\'\\u4f18\\u5316\\u7b97\\u6cd5\\uff1aSGD, Adam, RMSprop\\u7b49\')\", \"outputs\": []}, {\"cell_type\": \"code\", \"source\": \"# \\u6df1\\u5ea6\\u5b66\\u4e60\\u5e94\\u7528\\u9886\\u57df\\ndef deep_learning_applications():\\n    applications = {\\n        \'\\u8ba1\\u7b97\\u673a\\u89c6\\u89c9\': [\'\\u56fe\\u50cf\\u5206\\u7c7b\', \'\\u76ee\\u6807\\u68c0\\u6d4b\', \'\\u4eba\\u8138\\u8bc6\\u522b\', \'\\u56fe\\u50cf\\u751f\\u6210\'],\\n        \'\\u81ea\\u7136\\u8bed\\u8a00\\u5904\\u7406\': [\'\\u673a\\u5668\\u7ffb\\u8bd1\', \'\\u6587\\u672c\\u5206\\u7c7b\', \'\\u95ee\\u7b54\\u7cfb\\u7edf\', \'\\u6587\\u672c\\u751f\\u6210\'],\\n        \'\\u8bed\\u97f3\\u8bc6\\u522b\': [\'\\u8bed\\u97f3\\u8f6c\\u6587\\u5b57\', \'\\u8bed\\u97f3\\u5408\\u6210\', \'\\u58f0\\u7eb9\\u8bc6\\u522b\'],\\n        \'\\u63a8\\u8350\\u7cfb\\u7edf\': [\'\\u5546\\u54c1\\u63a8\\u8350\', \'\\u5185\\u5bb9\\u63a8\\u8350\', \'\\u4e2a\\u6027\\u5316\\u670d\\u52a1\']\\n    }\\n    return applications\", \"outputs\": []}], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python\", \"language\": \"python\", \"name\": \"python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}, \"nbformat\": 4, \"nbformat_minor\": 4}', '0', '1', null);

-- ----------------------------
-- Table structure for `books_jupytercell`
-- ----------------------------
DROP TABLE IF EXISTS `books_jupytercell`;
CREATE TABLE `books_jupytercell` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cell_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `execution_count` int(11) DEFAULT NULL,
  `metadata` json NOT NULL,
  `order` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `notebook_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `books_jupytercell_notebook_id_ea9c8727_fk_books_jup` (`notebook_id`),
  CONSTRAINT `books_jupytercell_notebook_id_ea9c8727_fk_books_jup` FOREIGN KEY (`notebook_id`) REFERENCES `books_jupyternotebook` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of books_jupytercell
-- ----------------------------
INSERT INTO books_jupytercell VALUES ('1', 'markdown', '## 1.1 计算机系统概述\n\n计算机系统由硬件系统和软件系统两大部分组成。硬件系统是计算机的物理组成部分，包括中央处理器(CPU)、内存、存储设备、输入设备和输出设备等。软件系统则是运行在硬件之上的程序和数据，包括系统软件和应用软件。\n\n对于非计算机专业学生来说，了解计算机的基本组成和工作原理有助于我们更好地使用计算机。计算机的基本工作原理是存储程序和程序控制，即程序和数据存储在计算机的存储器中，由CPU依次取出并执行指令，完成预定的任务。\n\n随着计算机技术的发展，计算机的性能不断提升，应用领域也不断扩大。从最初的科学计算，到现在的人工智能、大数据分析等，计算机已经渗透到我们生活和工作的方方面面。', null, '{}', '0', '2026-01-05 09:01:21.770114', '2026-01-05 09:01:21.770114');
INSERT INTO books_jupytercell VALUES ('2', 'markdown', '## 1.2 计算机中的数制与编码\n\n计算机内部采用二进制进行数据存储和处理。二进制只有0和1两个数字，运算规则简单，便于用电子元件实现。除了二进制，计算机中还常用到十进制、八进制和十六进制等数制，它们之间可以相互转换。\n\n在计算机中，各种信息（如文字、图像、声音等）都需要转换为二进制形式进行存储和处理。文字的编码是指用二进制数表示文字的规则，常见的编码标准有ASCII码、GB2312、UTF-8等。了解这些编码标准有助于我们正确地处理和显示各种文字信息。\n\n对于非计算机专业学生来说，掌握基本的数制转换方法和了解常见的编码标准是很有必要的，这有助于我们更好地理解计算机是如何处理信息的。', null, '{}', '1', '2026-01-05 09:01:21.777961', '2026-01-05 09:01:21.777961');
INSERT INTO books_jupytercell VALUES ('3', 'code', '# 计算机存储单位换算示例\ndef storage_conversion(bytes_value):\n    units = [\'B\', \'KB\', \'MB\', \'GB\', \'TB\']\n    index = 0\n    value = float(bytes_value)\n    while value >= 1024 and index < len(units) - 1:\n        value /= 1024\n        index += 1\n    return f\"{value:.2f} {units[index]}\"\n\n# 测试函数\nprint(storage_conversion(1024))  # 1 KB\nprint(storage_conversion(1048576))  # 1 MB', null, '{}', '2', '2026-01-05 09:01:21.785979', '2026-01-05 09:01:21.785979');
INSERT INTO books_jupytercell VALUES ('4', 'markdown', '## 1.1 数据分析概述\n\n数据分析是指用适当的统计分析方法对收集来的数据进行分析，提取有用信息并形成结论的过程。随着大数据时代的到来，数据分析在各个领域的重要性日益凸显。对于非计算机专业学生来说，掌握基本的数据分析技能可以帮助我们更好地理解和利用数据。\n\n数据分析的基本流程包括数据收集、数据清洗、数据转换、数据分析和数据可视化等步骤。在数据分析过程中，我们需要选择合适的分析方法和工具，根据数据的类型和分析的目的来确定具体的分析策略。', null, '{}', '0', '2026-01-05 09:01:21.771706', '2026-01-05 09:01:21.771706');
INSERT INTO books_jupytercell VALUES ('5', 'markdown', '## 1.2 数据类型与数据结构\n\n在数据分析中，了解数据的类型和结构是非常重要的。常见的数据类型包括数值型数据（如整数、浮点数）、分类型数据（如性别、职业）、有序型数据（如评分等级）等。不同类型的数据需要采用不同的分析方法和处理方式。\n\n数据结构是指数据的组织方式，常见的数据结构包括表格数据、时间序列数据、文本数据等。表格数据是最常见的数据结构，它由行和列组成，每一行代表一个观察对象，每一列代表一个属性。', null, '{}', '1', '2026-01-05 09:01:21.777961', '2026-01-05 09:01:21.777961');
INSERT INTO books_jupytercell VALUES ('6', 'code', '# 使用Pandas进行基本数据操作\nimport pandas as pd\ndef basic_data_operations(df):\n    print(\'数据基本信息:\')\n    print(df.info())\n    print(\'\n数据前5行:\')\n    print(df.head())\n    print(\'\n数据统计摘要:\')\n    print(df.describe())', null, '{}', '2', '2026-01-05 09:01:21.785979', '2026-01-05 09:01:21.785979');
INSERT INTO books_jupytercell VALUES ('7', 'code', '# 数据清洗示例\nimport pandas as pd\ndef handle_missing_values(df):\n    print(\'缺失值统计:\')\n    print(df.isnull().sum())\n    # 填充数值型缺失值\n    numeric_cols = df.select_dtypes(include=[\'float64\', \'int64\']).columns\n    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())\n    return df', null, '{}', '3', '2026-01-05 09:01:21.790666', '2026-01-05 09:01:21.790666');
INSERT INTO books_jupytercell VALUES ('8', 'markdown', '## 1.1 人工智能的定义与发展历程\n\n人工智能（Artificial Intelligence，简称AI）是指由人制造出来的系统所表现出来的智能。人工智能的目标是让机器能够模拟人类的智能行为，如感知、推理、学习、决策等。对于非计算机专业学生来说，了解人工智能的基本概念和发展历程有助于我们更好地理解这一快速发展的技术领域。\n\n人工智能的发展大致可以分为三个阶段：第一阶段是人工智能的孕育期（1940s-1950s），这一时期主要是理论和技术的准备；第二阶段是人工智能的形成期（1950s-1960s），人工智能作为一个学科正式诞生；第三阶段是人工智能的发展期（1970s至今），人工智能经历了多次高潮和低谷，不断取得新的突破。', null, '{}', '0', '2026-01-05 09:01:21.773265', '2026-01-05 09:01:21.773265');
INSERT INTO books_jupytercell VALUES ('9', 'markdown', '## 1.2 人工智能的主要领域与应用\n\n人工智能的应用领域非常广泛，涵盖了计算机视觉、自然语言处理、语音识别、专家系统、智能机器人等多个方面。计算机视觉是让计算机能够理解和解释图像或视频的技术，应用于人脸识别、物体检测、图像分割等任务；自然语言处理是让计算机能够理解和生成人类语言的技术，应用于机器翻译、情感分析、文本摘要等任务。', null, '{}', '1', '2026-01-05 09:01:21.779509', '2026-01-05 09:01:21.779509');
INSERT INTO books_jupytercell VALUES ('10', 'code', '# 简单的智能对话机器人示例\ndef simple_chatbot():\n    responses = {\n        \'你好\': \'你好！很高兴见到你！\',\n        \'你是谁\': \'我是一个简单的对话机器人。\',\n        \'什么是人工智能\': \'人工智能是指由人制造出来的系统所表现出来的智能。\'\n    }\n    return responses', null, '{}', '2', '2026-01-05 09:01:21.787563', '2026-01-05 09:01:21.787563');
INSERT INTO books_jupytercell VALUES ('11', 'code', '# 文本分类简单示例\ndef simple_text_classifier(text):\n    positive_words = [\'好\', \'棒\', \'优秀\', \'喜欢\']\n    negative_words = [\'差\', \'糟糕\', \'失望\', \'不满意\']\n    positive_count = sum(1 for word in positive_words if word in text)\n    negative_count = sum(1 for word in negative_words if word in text)\n    if positive_count > negative_count:\n        return \'正面评价\'\n    elif negative_count > positive_count:\n        return \'负面评价\'\n    else:\n        return \'中性评价\'', null, '{}', '3', '2026-01-05 09:01:21.792214', '2026-01-05 09:01:21.792214');
INSERT INTO books_jupytercell VALUES ('12', 'markdown', '## 2.1 操作系统概述\n\n操作系统是管理计算机硬件与软件资源的系统软件，为用户提供了一个操作计算机的界面。常见的操作系统有Windows、macOS和Linux等。对于非计算机专业学生来说，熟悉操作系统的基本操作是使用计算机的前提。\n\n操作系统的主要功能包括进程管理、内存管理、文件管理和设备管理等。进程管理负责调度和控制程序的执行；内存管理负责分配和回收内存资源；文件管理负责组织和存取文件；设备管理负责管理和控制各种硬件设备。了解这些功能有助于我们更好地理解和使用操作系统。', null, '{}', '0', '2026-01-05 09:01:21.773265', '2026-01-05 09:01:21.773265');
INSERT INTO books_jupytercell VALUES ('13', 'markdown', '## 2.2 文件与文件夹管理\n\n文件是存储在计算机中的一组相关信息的集合，通常具有特定的扩展名来标识文件类型。文件夹则是用于组织和管理文件的容器，可以嵌套创建子文件夹。合理地组织文件和文件夹结构有助于提高工作效率。\n\n在Windows操作系统中，文件系统采用树形结构，以驱动器盘符为根目录，向下延伸出多个层次的文件夹和文件。我们可以通过资源管理器来浏览、创建、移动、复制和删除文件和文件夹。学会这些基本操作对于日常的文件管理非常重要。', null, '{}', '1', '2026-01-05 09:01:21.779509', '2026-01-05 09:01:21.779509');
INSERT INTO books_jupytercell VALUES ('14', 'code', '# 文件大小统计示例\nimport os\ndef get_directory_size(directory):\n    total_size = 0\n    for path, dirs, files in os.walk(directory):\n        for file in files:\n            try:\n                filepath = os.path.join(path, file)\n                total_size += os.path.getsize(filepath)\n            except OSError:\n                continue\n    return total_size', null, '{}', '2', '2026-01-05 09:01:21.787563', '2026-01-05 09:01:21.787563');
INSERT INTO books_jupytercell VALUES ('15', 'code', '# 简单的文件重命名工具\nimport os\ndef batch_rename(directory, prefix):\n    count = 1\n    for filename in os.listdir(directory):\n        if os.path.isfile(os.path.join(directory, filename)):\n            file_ext = os.path.splitext(filename)[1]\n            new_name = f\"{prefix}_{count:03d}{file_ext}\"\n            os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))\n            count += 1\n    return count - 1', null, '{}', '3', '2026-01-05 09:01:21.792214', '2026-01-05 09:01:21.792214');
INSERT INTO books_jupytercell VALUES ('16', 'markdown', '## 2.1 描述性统计分析\n\n描述性统计分析是数据分析的基础，它通过计算各种统计量来描述数据的基本特征。常见的描述性统计量包括均值、中位数、众数、标准差、方差、四分位数等。这些统计量可以帮助我们了解数据的集中趋势、离散程度和分布特征。\n\n对于非计算机专业学生来说，掌握基本的描述性统计分析方法可以帮助我们初步了解数据的特征和规律。在Python中，我们可以使用NumPy和Pandas等库来计算各种描述性统计量。', null, '{}', '0', '2026-01-05 09:01:21.774841', '2026-01-05 09:01:21.774841');
INSERT INTO books_jupytercell VALUES ('17', 'markdown', '## 2.2 相关性分析与回归分析\n\n相关性分析是研究两个或多个变量之间关系的统计方法。常见的相关性分析方法包括皮尔逊相关系数、斯皮尔曼等级相关系数等。这些方法可以帮助我们了解变量之间的相关程度和方向。\n\n回归分析是一种用于研究变量之间因果关系的统计方法，它通过建立回归模型来预测或解释变量之间的关系。常见的回归分析方法包括线性回归、多元线性回归、逻辑回归等。', null, '{}', '1', '2026-01-05 09:01:21.781592', '2026-01-05 09:01:21.781592');
INSERT INTO books_jupytercell VALUES ('18', 'code', '# 描述性统计分析示例\nimport pandas as pd\nimport numpy as np\ndef calculate_stats(data):\n    df = pd.DataFrame(data)\n    print(\'基本统计摘要:\')\n    print(df.describe())\n    print(\'\n偏度:\', df.skew())\n    print(\'峰度:\', df.kurtosis())', null, '{}', '2', '2026-01-05 09:01:21.787563', '2026-01-05 09:01:21.787563');
INSERT INTO books_jupytercell VALUES ('19', 'code', '# 相关性分析示例\nimport pandas as pd\ndef correlation_analysis(df):\n    corr_matrix = df.corr()\n    print(\'相关性矩阵:\')\n    print(corr_matrix)\n    return corr_matrix', null, '{}', '3', '2026-01-05 09:01:21.793781', '2026-01-05 09:01:21.793781');
INSERT INTO books_jupytercell VALUES ('20', 'markdown', '## 2.1 机器学习的基本概念\n\n机器学习是人工智能的一个重要分支，它是一门研究如何使计算机系统通过经验自动改进的学科。机器学习的核心思想是让计算机从数据中学习规律，而不需要显式地编程指定规则。对于非计算机专业学生来说，了解机器学习的基本概念有助于我们理解人工智能技术的工作原理。\n\n机器学习的主要类型包括监督学习、无监督学习和强化学习等。监督学习是从标记数据中学习的方法，常见的任务包括分类和回归；无监督学习是从未标记数据中学习的方法，常见的任务包括聚类和降维；强化学习是通过与环境交互并接收奖惩信号来学习的方法，适用于决策和控制类任务。', null, '{}', '0', '2026-01-05 09:01:21.774841', '2026-01-05 09:01:21.774841');
INSERT INTO books_jupytercell VALUES ('21', 'markdown', '## 2.2 机器学习算法简介\n\n线性回归是最基本的机器学习算法之一，它用于建模自变量和因变量之间的线性关系。线性回归假设自变量和因变量之间存在线性关系，通过最小化预测值和实际值之间的误差来学习模型参数。线性回归在房价预测、销售预测等问题中有着广泛的应用。\n\n决策树是一种基于树结构的分类和回归算法，它通过对特征进行递归分割来构建决策树。决策树具有直观、易于理解的特点，在医疗诊断、风险评估等领域有着广泛的应用。', null, '{}', '1', '2026-01-05 09:01:21.782600', '2026-01-05 09:01:21.782600');
INSERT INTO books_jupytercell VALUES ('22', 'code', '# 简单线性回归示例\nimport numpy as np\ndef simple_linear_regression(x, y):\n    x_mean = np.mean(x)\n    y_mean = np.mean(y)\n    numerator = np.sum((x - x_mean) * (y - y_mean))\n    denominator = np.sum((x - x_mean) ** 2)\n    slope = numerator / denominator\n    intercept = y_mean - slope * x_mean\n    return slope, intercept', null, '{}', '2', '2026-01-05 09:01:21.789127', '2026-01-05 09:01:21.789127');
INSERT INTO books_jupytercell VALUES ('23', 'code', '# K-means聚类简单示例\nimport numpy as np\ndef kmeans_sample():\n    print(\'K-means聚类是一种无监督学习算法，用于将数据分成多个簇。\')\n    print(\'算法步骤：\')\n    print(\'1. 随机选择K个聚类中心\')\n    print(\'2. 将每个数据点分配到最近的聚类中心\')\n    print(\'3. 更新聚类中心为每个簇的均值\')\n    print(\'4. 重复步骤2和3直到收敛\')', null, '{}', '3', '2026-01-05 09:01:21.793781', '2026-01-05 09:01:21.793781');
INSERT INTO books_jupytercell VALUES ('24', 'markdown', '## 3.1 Word文档处理\n\nMicrosoft Word是最常用的文字处理软件，广泛应用于文档创建、编辑和排版等工作。对于非计算机专业学生来说，掌握Word的基本操作是学习和工作的必备技能。\n\nWord的主要功能包括文本输入与编辑、格式设置、段落设置、页面设置、表格制作、图片插入等。在学术写作中，我们经常需要使用Word来撰写论文、报告等文档。熟练掌握Word的样式、目录生成、引用和参考文献等功能可以大大提高学术写作的效率和质量。', null, '{}', '0', '2026-01-05 09:01:21.776405', '2026-01-05 09:01:21.776405');
INSERT INTO books_jupytercell VALUES ('25', 'markdown', '## 3.2 Excel电子表格应用\n\nMicrosoft Excel是一款功能强大的电子表格软件，主要用于数据处理、数据分析和图表绘制等。对于非计算机专业学生来说，掌握Excel的基本操作和常用函数可以帮助我们更高效地处理和分析数据。\n\nExcel的主要功能包括数据输入和编辑、格式设置、公式和函数使用、数据分析工具、图表创建等。常用的函数包括求和函数SUM、平均值函数AVERAGE、计数函数COUNT、条件函数IF、查找函数VLOOKUP等。学会使用这些函数可以大大简化数据计算和分析的工作。', null, '{}', '1', '2026-01-05 09:01:21.782600', '2026-01-05 09:01:21.782600');
INSERT INTO books_jupytercell VALUES ('26', 'code', '# Excel数据处理示例\nimport pandas as pd\ndef create_sample_data():\n    data = {\n        \'姓名\': [\'张三\', \'李四\', \'王五\', \'赵六\'],\n        \'语文\': [85, 92, 78, 90],\n        \'数学\': [90, 85, 95, 88],\n        \'英语\': [88, 90, 82, 95]\n    }\n    return pd.DataFrame(data)', null, '{}', '2', '2026-01-05 09:01:21.789127', '2026-01-05 09:01:21.789127');
INSERT INTO books_jupytercell VALUES ('27', 'code', '# 简单的文本处理函数\ndef format_text(text, operation):\n    if operation == \'uppercase\':\n        return text.upper()\n    elif operation == \'lowercase\':\n        return text.lower()\n    elif operation == \'titlecase\':\n        return text.title()\n    else:\n        return text', null, '{}', '3', '2026-01-05 09:01:21.793781', '2026-01-05 09:01:21.793781');
INSERT INTO books_jupytercell VALUES ('28', 'markdown', '## 3.1 数据可视化概述\n\n数据可视化是指将数据以图形或图像的形式呈现出来的技术。它可以帮助我们直观地理解数据的特征、趋势和关系，发现数据中隐藏的模式和规律。对于非计算机专业学生来说，掌握基本的数据可视化技能可以帮助我们更有效地展示和传达数据分析的结果。\n\n数据可视化的主要类型包括条形图、饼图、折线图、散点图、直方图、箱线图等。不同类型的图表适用于不同的数据类型和分析目的。', null, '{}', '0', '2026-01-05 09:01:21.776405', '2026-01-05 09:01:21.776405');
INSERT INTO books_jupytercell VALUES ('29', 'markdown', '## 3.2 常用图表类型及应用\n\n条形图是最常见的数据可视化图表之一，它用矩形条的长度来表示数据的大小。条形图可以水平或垂直绘制，适用于比较不同类别的数据。在实际应用中，条形图常用于展示不同产品的销售额、不同地区的人口数量等比较数据。\n\n饼图用圆形和扇形来展示数据，其中圆形代表整体，扇形代表部分。饼图适用于展示部分与整体的关系，例如不同产品销售额占总销售额的比例、不同专业学生人数占总人数的比例等。', null, '{}', '1', '2026-01-05 09:01:21.782600', '2026-01-05 09:01:21.782600');
INSERT INTO books_jupytercell VALUES ('30', 'code', '# 基本图表绘制示例\nimport matplotlib.pyplot as plt\ndef plot_bar_chart(labels, values):\n    plt.figure(figsize=(10, 6))\n    plt.bar(labels, values, color=\'skyblue\')\n    plt.title(\'条形图示例\')\n    plt.xlabel(\'类别\')\n    plt.ylabel(\'数值\')\n    plt.grid(axis=\'y\')', null, '{}', '2', '2026-01-05 09:01:21.790666', '2026-01-05 09:01:21.790666');
INSERT INTO books_jupytercell VALUES ('31', 'code', '# 折线图绘制示例\nimport matplotlib.pyplot as plt\ndef plot_line_chart(x_values, y_values):\n    plt.figure(figsize=(10, 6))\n    plt.plot(x_values, y_values, marker=\'o\', color=\'green\')\n    plt.title(\'折线图示例\')\n    plt.xlabel(\'X轴\')\n    plt.ylabel(\'Y轴\')\n    plt.grid(True)', null, '{}', '3', '2026-01-05 09:01:21.795309', '2026-01-05 09:01:21.795309');
INSERT INTO books_jupytercell VALUES ('32', 'markdown', '## 3.1 神经网络基础\n\n神经网络是深度学习的基础，它是由大量人工神经元相互连接而成的计算模型，灵感来源于人脑的神经元结构。对于非计算机专业学生来说，了解神经网络的基本结构和工作原理有助于我们理解深度学习的核心概念。\n\n神经网络的基本组成单元是人工神经元，它接收多个输入信号，通过权重加权后求和，再经过激活函数处理后输出结果。多个神经元按层次结构组织，形成输入层、隐藏层和输出层。输入层接收原始数据；隐藏层负责特征提取和处理；输出层产生最终的预测结果。', null, '{}', '0', '2026-01-05 09:01:21.777961', '2026-01-05 09:01:21.777961');
INSERT INTO books_jupytercell VALUES ('33', 'markdown', '## 3.2 深度学习应用与实践\n\n深度学习技术已经广泛应用于各个领域，取得了令人瞩目的成果。在计算机视觉领域，深度学习在图像分类、目标检测、图像分割、人脸识别等任务中取得了突破性进展；在自然语言处理领域，深度学习在机器翻译、文本分类、情感分析、问答系统、文本生成等任务中表现出色；在语音识别领域，深度学习大幅提高了语音识别的准确率。', null, '{}', '1', '2026-01-05 09:01:21.784303', '2026-01-05 09:01:21.784303');
INSERT INTO books_jupytercell VALUES ('34', 'code', '# 神经网络基本结构示例\ndef neural_network_structure():\n    print(\'神经网络基本结构示例：\')\n    print(\'输入层 -> 隐藏层 -> 输出层\')\n    print(\'激活函数：ReLU, Sigmoid, Tanh等\')\n    print(\'损失函数：MSE, Cross-Entropy等\')\n    print(\'优化算法：SGD, Adam, RMSprop等\')', null, '{}', '2', '2026-01-05 09:01:21.790666', '2026-01-05 09:01:21.790666');
INSERT INTO books_jupytercell VALUES ('35', 'code', '# 深度学习应用领域\ndef deep_learning_applications():\n    applications = {\n        \'计算机视觉\': [\'图像分类\', \'目标检测\', \'人脸识别\', \'图像生成\'],\n        \'自然语言处理\': [\'机器翻译\', \'文本分类\', \'问答系统\', \'文本生成\'],\n        \'语音识别\': [\'语音转文字\', \'语音合成\', \'声纹识别\'],\n        \'推荐系统\': [\'商品推荐\', \'内容推荐\', \'个性化服务\']\n    }\n    return applications', null, '{}', '3', '2026-01-05 09:01:21.795309', '2026-01-05 09:01:21.795309');

-- ----------------------------
-- Table structure for `books_jupyternotebook`
-- ----------------------------
DROP TABLE IF EXISTS `books_jupyternotebook`;
CREATE TABLE `books_jupyternotebook` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nbformat` int(11) NOT NULL,
  `nbformat_minor` int(11) NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `chapter_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `books_jupyternotebook_chapter_id_7ce25ec4_fk_books_chapter_id` FOREIGN KEY (`chapter_id`) REFERENCES `books_chapter` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of books_jupyternotebook
-- ----------------------------
INSERT INTO books_jupyternotebook VALUES ('1', '4', '4', '{\"kernelspec\": {\"name\": \"python\", \"language\": \"python\", \"display_name\": \"Python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}', '2026-01-05 09:01:21.760566', '2026-01-05 09:01:21.760566');
INSERT INTO books_jupyternotebook VALUES ('2', '4', '4', '{\"kernelspec\": {\"name\": \"python\", \"language\": \"python\", \"display_name\": \"Python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}', '2026-01-05 09:01:21.762109', '2026-01-05 09:01:21.762109');
INSERT INTO books_jupyternotebook VALUES ('3', '4', '4', '{\"kernelspec\": {\"name\": \"python\", \"language\": \"python\", \"display_name\": \"Python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}', '2026-01-05 09:01:21.763715', '2026-01-05 09:01:21.763715');
INSERT INTO books_jupyternotebook VALUES ('4', '4', '4', '{\"kernelspec\": {\"name\": \"python\", \"language\": \"python\", \"display_name\": \"Python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}', '2026-01-05 09:01:21.765253', '2026-01-05 09:01:21.765253');
INSERT INTO books_jupyternotebook VALUES ('5', '4', '4', '{\"kernelspec\": {\"name\": \"python\", \"language\": \"python\", \"display_name\": \"Python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}', '2026-01-05 09:01:21.765253', '2026-01-05 09:01:21.765253');
INSERT INTO books_jupyternotebook VALUES ('6', '4', '4', '{\"kernelspec\": {\"name\": \"python\", \"language\": \"python\", \"display_name\": \"Python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}', '2026-01-05 09:01:21.766800', '2026-01-05 09:01:21.766800');
INSERT INTO books_jupyternotebook VALUES ('7', '4', '4', '{\"kernelspec\": {\"name\": \"python\", \"language\": \"python\", \"display_name\": \"Python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}', '2026-01-05 09:01:21.766800', '2026-01-05 09:01:21.766800');
INSERT INTO books_jupyternotebook VALUES ('8', '4', '4', '{\"kernelspec\": {\"name\": \"python\", \"language\": \"python\", \"display_name\": \"Python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}', '2026-01-05 09:01:21.768384', '2026-01-05 09:01:21.768384');
INSERT INTO books_jupyternotebook VALUES ('9', '4', '4', '{\"kernelspec\": {\"name\": \"python\", \"language\": \"python\", \"display_name\": \"Python\"}, \"language_info\": {\"name\": \"python\", \"version\": \"3.9.0\"}}', '2026-01-05 09:01:21.770114', '2026-01-05 09:01:21.770114');

-- ----------------------------
-- Table structure for `books_jupyteroutput`
-- ----------------------------
DROP TABLE IF EXISTS `books_jupyteroutput`;
CREATE TABLE `books_jupyteroutput` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `output_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data` json NOT NULL,
  `ename` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `evalue` longtext COLLATE utf8mb4_unicode_ci,
  `traceback` json DEFAULT NULL,
  `execution_count` int(11) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `cell_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `books_jupyteroutput_cell_id_9ff59088_fk_books_jupytercell_id` (`cell_id`),
  CONSTRAINT `books_jupyteroutput_cell_id_9ff59088_fk_books_jupytercell_id` FOREIGN KEY (`cell_id`) REFERENCES `books_jupytercell` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of books_jupyteroutput
-- ----------------------------

-- ----------------------------
-- Table structure for `books_practice`
-- ----------------------------
DROP TABLE IF EXISTS `books_practice`;
CREATE TABLE `books_practice` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `chapter_id` int(11) NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  `language` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `difficulty` int(11) NOT NULL,
  `order` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `questions` json NOT NULL DEFAULT (_utf8mb4'[]'),
  PRIMARY KEY (`id`),
  KEY `books_practice_chapter_id_ceafeeaf` (`chapter_id`),
  CONSTRAINT `books_practice_chapter_id_ceafeeaf_fk_books_chapter_id` FOREIGN KEY (`chapter_id`) REFERENCES `books_chapter` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of books_practice
-- ----------------------------
INSERT INTO books_practice VALUES ('73', '1', '第1章 计算机基础知识 - 练习题集', '《大学计算机基础与应用》第1章 计算机基础知识的练习题，包含6道不同类型的题目', 'python', '2', '1', '2026-01-05 09:01:21.798409', '2026-01-05 09:01:21.798409');
INSERT INTO books_practice VALUES ('74', '4', '第1章 数据分析基础 - 练习题集', '《数据分析与可视化入门》第1章 数据分析基础的练习题，包含6道不同类型的题目', 'python', '2', '1', '2026-01-05 09:01:21.799980', '2026-01-05 09:01:21.799980');
INSERT INTO books_practice VALUES ('75', '7', '第1章 人工智能概述 - 练习题集', '《人工智能与机器学习基础》第1章 人工智能概述的练习题，包含6道不同类型的题目', 'python', '2', '1', '2026-01-05 09:01:21.801504', '2026-01-05 09:01:21.801504');
INSERT INTO books_practice VALUES ('76', '2', '第2章 操作系统基础 - 练习题集', '《大学计算机基础与应用》第2章 操作系统基础的练习题，包含6道不同类型的题目', 'python', '2', '1', '2026-01-05 09:01:21.803045', '2026-01-05 09:01:21.803045');
INSERT INTO books_practice VALUES ('77', '5', '第2章 数据分析方法与应用 - 练习题集', '《数据分析与可视化入门》第2章 数据分析方法与应用的练习题，包含6道不同类型的题目', 'python', '2', '1', '2026-01-05 09:01:21.804645', '2026-01-05 09:01:21.804645');
INSERT INTO books_practice VALUES ('78', '8', '第2章 机器学习基础 - 练习题集', '《人工智能与机器学习基础》第2章 机器学习基础的练习题，包含6道不同类型的题目', 'python', '2', '1', '2026-01-05 09:01:21.806176', '2026-01-05 09:01:21.806176');
INSERT INTO books_practice VALUES ('79', '3', '第3章 办公软件应用 - 练习题集', '《大学计算机基础与应用》第3章 办公软件应用的练习题，包含6道不同类型的题目', 'python', '2', '1', '2026-01-05 09:01:21.807773', '2026-01-05 09:01:21.807773');
INSERT INTO books_practice VALUES ('80', '6', '第3章 数据可视化技术 - 练习题集', '《数据分析与可视化入门》第3章 数据可视化技术的练习题，包含6道不同类型的题目', 'python', '2', '1', '2026-01-05 09:01:21.810958', '2026-01-05 09:01:21.810958');
INSERT INTO books_practice VALUES ('81', '9', '第3章 深度学习入门 - 练习题集', '《人工智能与机器学习基础》第3章 深度学习入门的练习题，包含6道不同类型的题目', 'python', '2', '1', '2026-01-05 09:01:21.812554', '2026-01-05 09:01:21.812554');

-- ----------------------------
-- Table structure for `books_practicechoiceoption`
-- ----------------------------
DROP TABLE IF EXISTS `books_practicechoiceoption`;
CREATE TABLE `books_practicechoiceoption` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_correct` tinyint(1) NOT NULL,
  `order` int(11) NOT NULL,
  `practice_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `books_practicechoice_practice_id_19fe06f4_fk_books_pra` (`practice_id`),
  CONSTRAINT `books_practicechoice_practice_id_19fe06f4_fk_books_pra` FOREIGN KEY (`practice_id`) REFERENCES `books_practice` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of books_practicechoiceoption
-- ----------------------------

-- ----------------------------
-- Table structure for `books_practicefillblank`
-- ----------------------------
DROP TABLE IF EXISTS `books_practicefillblank`;
CREATE TABLE `books_practicefillblank` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `prompt` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `placeholder` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `correct_answer` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order` int(11) NOT NULL,
  `practice_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `books_practicefillbl_practice_id_7f0c7cf4_fk_books_pra` (`practice_id`),
  CONSTRAINT `books_practicefillbl_practice_id_7f0c7cf4_fk_books_pra` FOREIGN KEY (`practice_id`) REFERENCES `books_practice` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of books_practicefillblank
-- ----------------------------

-- ----------------------------
-- Table structure for `books_testcase`
-- ----------------------------
DROP TABLE IF EXISTS `books_testcase`;
CREATE TABLE `books_testcase` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `input_data` json NOT NULL,
  `expected_output` json NOT NULL,
  `practice_id` bigint(20) NOT NULL,
  `order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `books_testcase_practice_id_bb93ba0b_fk_books_practice_id` (`practice_id`),
  CONSTRAINT `books_testcase_practice_id_bb93ba0b_fk_books_practice_id` FOREIGN KEY (`practice_id`) REFERENCES `books_practice` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of books_testcase
-- ----------------------------

-- ----------------------------
-- Table structure for `django_admin_log`
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_users_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of django_admin_log
-- ----------------------------

-- ----------------------------
-- Table structure for `django_content_type`
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of django_content_type
-- ----------------------------
INSERT INTO django_content_type VALUES ('1', 'admin', 'logentry');
INSERT INTO django_content_type VALUES ('3', 'auth', 'group');
INSERT INTO django_content_type VALUES ('2', 'auth', 'permission');
INSERT INTO django_content_type VALUES ('6', 'authtoken', 'token');
INSERT INTO django_content_type VALUES ('7', 'authtoken', 'tokenproxy');
INSERT INTO django_content_type VALUES ('10', 'books', 'book');
INSERT INTO django_content_type VALUES ('11', 'books', 'chapter');
INSERT INTO django_content_type VALUES ('14', 'books', 'jupytercell');
INSERT INTO django_content_type VALUES ('16', 'books', 'jupyternotebook');
INSERT INTO django_content_type VALUES ('15', 'books', 'jupyteroutput');
INSERT INTO django_content_type VALUES ('12', 'books', 'practice');
INSERT INTO django_content_type VALUES ('17', 'books', 'practicechoiceoption');
INSERT INTO django_content_type VALUES ('18', 'books', 'practicefillblank');
INSERT INTO django_content_type VALUES ('13', 'books', 'testcase');
INSERT INTO django_content_type VALUES ('4', 'contenttypes', 'contenttype');
INSERT INTO django_content_type VALUES ('29', 'learning', 'exercise');
INSERT INTO django_content_type VALUES ('30', 'learning', 'exerciserecord');
INSERT INTO django_content_type VALUES ('31', 'learning', 'exercisetestcase');
INSERT INTO django_content_type VALUES ('19', 'learning', 'heatmapdata');
INSERT INTO django_content_type VALUES ('32', 'learning', 'jupyterdocument');
INSERT INTO django_content_type VALUES ('36', 'learning', 'knowledgemastery');
INSERT INTO django_content_type VALUES ('35', 'learning', 'learningpreference');
INSERT INTO django_content_type VALUES ('34', 'learning', 'learningrecommendation');
INSERT INTO django_content_type VALUES ('20', 'learning', 'learningrecord');
INSERT INTO django_content_type VALUES ('33', 'learning', 'learningstyle');
INSERT INTO django_content_type VALUES ('28', 'learning', 'note');
INSERT INTO django_content_type VALUES ('37', 'learning', 'noteattachment');
INSERT INTO django_content_type VALUES ('38', 'learning', 'noteshare');
INSERT INTO django_content_type VALUES ('39', 'learning', 'notetag');
INSERT INTO django_content_type VALUES ('40', 'learning', 'notetagrelation');
INSERT INTO django_content_type VALUES ('41', 'learning', 'noteversion');
INSERT INTO django_content_type VALUES ('21', 'learning', 'practicerecord');
INSERT INTO django_content_type VALUES ('26', 'learning', 'roadmapbook');
INSERT INTO django_content_type VALUES ('23', 'learning', 'roadmapstage');
INSERT INTO django_content_type VALUES ('24', 'learning', 'roadmaptemplate');
INSERT INTO django_content_type VALUES ('25', 'learning', 'userlearningpath');
INSERT INTO django_content_type VALUES ('27', 'learning', 'userpathstage');
INSERT INTO django_content_type VALUES ('22', 'learning', 'wrongquestion');
INSERT INTO django_content_type VALUES ('5', 'sessions', 'session');
INSERT INTO django_content_type VALUES ('45', 'toolkit', 'executionhistory');
INSERT INTO django_content_type VALUES ('42', 'toolkit', 'tool');
INSERT INTO django_content_type VALUES ('43', 'toolkit', 'toolcategory');
INSERT INTO django_content_type VALUES ('44', 'toolkit', 'toolparameter');
INSERT INTO django_content_type VALUES ('8', 'users', 'user');
INSERT INTO django_content_type VALUES ('9', 'users', 'userpreferences');

-- ----------------------------
-- Table structure for `django_migrations`
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of django_migrations
-- ----------------------------
INSERT INTO django_migrations VALUES ('1', 'contenttypes', '0001_initial', '2026-01-05 08:39:09.185332');
INSERT INTO django_migrations VALUES ('2', 'contenttypes', '0002_remove_content_type_name', '2026-01-05 08:39:09.321518');
INSERT INTO django_migrations VALUES ('3', 'auth', '0001_initial', '2026-01-05 08:39:09.735292');
INSERT INTO django_migrations VALUES ('4', 'auth', '0002_alter_permission_name_max_length', '2026-01-05 08:39:09.819869');
INSERT INTO django_migrations VALUES ('5', 'auth', '0003_alter_user_email_max_length', '2026-01-05 08:39:09.825965');
INSERT INTO django_migrations VALUES ('6', 'auth', '0004_alter_user_username_opts', '2026-01-05 08:39:09.835164');
INSERT INTO django_migrations VALUES ('7', 'auth', '0005_alter_user_last_login_null', '2026-01-05 08:39:09.842821');
INSERT INTO django_migrations VALUES ('8', 'auth', '0006_require_contenttypes_0002', '2026-01-05 08:39:09.848998');
INSERT INTO django_migrations VALUES ('9', 'auth', '0007_alter_validators_add_error_messages', '2026-01-05 08:39:09.857282');
INSERT INTO django_migrations VALUES ('10', 'auth', '0008_alter_user_username_max_length', '2026-01-05 08:39:09.863433');
INSERT INTO django_migrations VALUES ('11', 'auth', '0009_alter_user_last_name_max_length', '2026-01-05 08:39:09.872668');
INSERT INTO django_migrations VALUES ('12', 'auth', '0010_alter_group_name_max_length', '2026-01-05 08:39:09.893032');
INSERT INTO django_migrations VALUES ('13', 'auth', '0011_update_proxy_permissions', '2026-01-05 08:39:09.902134');
INSERT INTO django_migrations VALUES ('14', 'auth', '0012_alter_user_first_name_max_length', '2026-01-05 08:39:09.909738');
INSERT INTO django_migrations VALUES ('15', 'users', '0001_initial', '2026-01-05 08:39:10.462404');
INSERT INTO django_migrations VALUES ('16', 'admin', '0001_initial', '2026-01-05 08:39:10.662577');
INSERT INTO django_migrations VALUES ('17', 'admin', '0002_logentry_remove_auto_add', '2026-01-05 08:39:10.670228');
INSERT INTO django_migrations VALUES ('18', 'admin', '0003_logentry_add_action_flag_choices', '2026-01-05 08:39:10.678982');
INSERT INTO django_migrations VALUES ('19', 'auth', '0013_auto_20260104_2314', '2026-01-05 08:39:10.683569');
INSERT INTO django_migrations VALUES ('20', 'authtoken', '0001_initial', '2026-01-05 08:39:10.795592');
INSERT INTO django_migrations VALUES ('21', 'authtoken', '0002_auto_20160226_1747', '2026-01-05 08:39:10.819453');
INSERT INTO django_migrations VALUES ('22', 'authtoken', '0003_tokenproxy', '2026-01-05 08:39:10.825615');
INSERT INTO django_migrations VALUES ('23', 'books', '0001_initial', '2026-01-05 08:39:11.151863');
INSERT INTO django_migrations VALUES ('24', 'books', '0002_chapter_video_url', '2026-01-05 08:39:11.178842');
INSERT INTO django_migrations VALUES ('25', 'books', '0003_book_pdf_file', '2026-01-05 08:39:11.205433');
INSERT INTO django_migrations VALUES ('26', 'books', '0004_book_owner', '2026-01-05 08:39:11.294888');
INSERT INTO django_migrations VALUES ('27', 'books', '0005_chapter_content_type_chapter_jupyter_content', '2026-01-05 08:39:11.359053');
INSERT INTO django_migrations VALUES ('28', 'books', '0006_add_jupyter_notebook_models', '2026-01-05 08:39:11.686714');
INSERT INTO django_migrations VALUES ('29', 'books', '0007_chapter_merged_content', '2026-01-05 08:39:11.717813');
INSERT INTO django_migrations VALUES ('30', 'books', '0008_chapter_level_chapter_parent_order', '2026-01-05 08:39:11.803301');
INSERT INTO django_migrations VALUES ('31', 'books', '0009_remove_chapter_parent_order_chapter_is_main_chapter_and_more', '2026-01-05 08:39:12.006933');
INSERT INTO django_migrations VALUES ('32', 'books', '0010_auto_20260104_2041', '2026-01-05 08:39:12.506875');
INSERT INTO django_migrations VALUES ('33', 'books', '0011_add_sample_practice_data', '2026-01-05 08:39:12.521651');
INSERT INTO django_migrations VALUES ('34', 'books', '0012_alter_practice_options_alter_testcase_options_and_more', '2026-01-05 08:39:12.697160');
INSERT INTO django_migrations VALUES ('35', 'books', '0013_modify_practice_model', '2026-01-05 08:39:12.963762');
INSERT INTO django_migrations VALUES ('36', 'learning', '0001_initial', '2026-01-05 08:39:13.200530');
INSERT INTO django_migrations VALUES ('37', 'learning', '0002_initial', '2026-01-05 08:39:13.678872');
INSERT INTO django_migrations VALUES ('38', 'learning', '0003_wrongquestion', '2026-01-05 08:39:13.944940');
INSERT INTO django_migrations VALUES ('39', 'learning', '0004_roadmapstage_roadmaptemplate_userlearningpath_and_more', '2026-01-05 08:39:14.730734');
INSERT INTO django_migrations VALUES ('40', 'learning', '0005_note', '2026-01-05 08:39:14.840194');
INSERT INTO django_migrations VALUES ('41', 'learning', '0006_note_is_starred_notetag_notecategory_note_category_and_more', '2026-01-05 08:39:15.317563');
INSERT INTO django_migrations VALUES ('42', 'learning', '0007_exercise_exerciserecord_exercisetestcase_and_more', '2026-01-05 08:39:15.892596');
INSERT INTO django_migrations VALUES ('43', 'learning', '0008_wrongquestion_attempt_time_wrongquestion_practice_and_more', '2026-01-05 08:39:16.414992');
INSERT INTO django_migrations VALUES ('44', 'learning', '0009_wrongquestion_question_type', '2026-01-05 08:39:16.459226');
INSERT INTO django_migrations VALUES ('45', 'learning', '0010_jupyterdocument', '2026-01-05 08:39:16.729825');
INSERT INTO django_migrations VALUES ('46', 'learning', '0011_learningstyle_learningrecommendation_and_more', '2026-01-05 08:39:17.912735');
INSERT INTO django_migrations VALUES ('47', 'learning', '0012_noteattachment_noteshare_notetag_notetagrelation_and_more', '2026-01-05 08:39:19.532564');
INSERT INTO django_migrations VALUES ('48', 'learning', '0013_alter_notetag_name', '2026-01-05 08:39:19.594543');
INSERT INTO django_migrations VALUES ('49', 'sessions', '0001_initial', '2026-01-05 08:39:19.644230');
INSERT INTO django_migrations VALUES ('50', 'toolkit', '0001_initial', '2026-01-05 08:39:20.069327');
INSERT INTO django_migrations VALUES ('51', 'toolkit', '0002_remove_tool_title_tool_name_tool_slug_and_more', '2026-01-05 08:39:20.295650');

-- ----------------------------
-- Table structure for `django_session`
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of django_session
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_exercise`
-- ----------------------------
DROP TABLE IF EXISTS `learning_exercise`;
CREATE TABLE `learning_exercise` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `question` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `code_template` longtext COLLATE utf8mb4_unicode_ci,
  `language` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `difficulty` int(11) NOT NULL,
  `category` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_exercise
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_exerciserecord`
-- ----------------------------
DROP TABLE IF EXISTS `learning_exerciserecord`;
CREATE TABLE `learning_exerciserecord` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_code` longtext COLLATE utf8mb4_unicode_ci,
  `passed` tinyint(1) NOT NULL,
  `score` int(11) NOT NULL,
  `submitted_at` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `exercise_id` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_exerciserec_exercise_id_b5043b55_fk_learning_` (`exercise_id`),
  KEY `learning_exerciserecord_user_id_7cb0621c_fk_users_user_id` (`user_id`),
  CONSTRAINT `learning_exerciserec_exercise_id_b5043b55_fk_learning_` FOREIGN KEY (`exercise_id`) REFERENCES `learning_exercise` (`id`),
  CONSTRAINT `learning_exerciserecord_user_id_7cb0621c_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_exerciserecord
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_exercisetestcase`
-- ----------------------------
DROP TABLE IF EXISTS `learning_exercisetestcase`;
CREATE TABLE `learning_exercisetestcase` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `input_data` json NOT NULL,
  `expected_output` json NOT NULL,
  `order` int(11) NOT NULL,
  `exercise_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_exercisetes_exercise_id_9bfec691_fk_learning_` (`exercise_id`),
  CONSTRAINT `learning_exercisetes_exercise_id_9bfec691_fk_learning_` FOREIGN KEY (`exercise_id`) REFERENCES `learning_exercise` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_exercisetestcase
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_heatmapdata`
-- ----------------------------
DROP TABLE IF EXISTS `learning_heatmapdata`;
CREATE TABLE `learning_heatmapdata` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `minutes` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `learning_heatmapdata_user_id_date_25f9952f_uniq` (`user_id`,`date`),
  CONSTRAINT `learning_heatmapdata_user_id_c48cf065_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_heatmapdata
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_jupyterdocument`
-- ----------------------------
DROP TABLE IF EXISTS `learning_jupyterdocument`;
CREATE TABLE `learning_jupyterdocument` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_public` tinyint(1) NOT NULL,
  `book_id` int(11) DEFAULT NULL,
  `chapter_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_jupyterdocument_book_id_8396f98e_fk_books_book_id` (`book_id`),
  KEY `learning_jupyterdocument_chapter_id_9874d510_fk_books_chapter_id` (`chapter_id`),
  KEY `learning_jupyterdocument_user_id_da7c196b_fk_users_user_id` (`user_id`),
  CONSTRAINT `learning_jupyterdocument_book_id_8396f98e_fk_books_book_id` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `learning_jupyterdocument_chapter_id_9874d510_fk_books_chapter_id` FOREIGN KEY (`chapter_id`) REFERENCES `books_chapter` (`id`),
  CONSTRAINT `learning_jupyterdocument_user_id_da7c196b_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_jupyterdocument
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_knowledgemastery`
-- ----------------------------
DROP TABLE IF EXISTS `learning_knowledgemastery`;
CREATE TABLE `learning_knowledgemastery` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `knowledge_point` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mastery_level` double NOT NULL,
  `assessed_at` datetime(6) NOT NULL,
  `assessment_count` int(11) NOT NULL,
  `tags` json NOT NULL,
  `book_id` int(11) DEFAULT NULL,
  `chapter_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `learning_knowledgemaster_user_id_knowledge_point__7b744414_uniq` (`user_id`,`knowledge_point`,`book_id`,`chapter_id`),
  KEY `learning_knowledgemastery_book_id_bb100a26_fk_books_book_id` (`book_id`),
  KEY `learning_knowledgema_chapter_id_f7682bdb_fk_books_cha` (`chapter_id`),
  CONSTRAINT `learning_knowledgema_chapter_id_f7682bdb_fk_books_cha` FOREIGN KEY (`chapter_id`) REFERENCES `books_chapter` (`id`),
  CONSTRAINT `learning_knowledgemastery_book_id_bb100a26_fk_books_book_id` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `learning_knowledgemastery_user_id_03567d67_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_knowledgemastery
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_learningpreference`
-- ----------------------------
DROP TABLE IF EXISTS `learning_learningpreference`;
CREATE TABLE `learning_learningpreference` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `learning_goals` json NOT NULL,
  `interest_areas` json NOT NULL,
  `daily_available_minutes` int(11) NOT NULL,
  `reminder_enabled` tinyint(1) NOT NULL,
  `reminder_time` time(6) DEFAULT NULL,
  `difficulty_preference` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `learning_learningpreference_user_id_42c60e88_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_learningpreference
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_learningrecommendation`
-- ----------------------------
DROP TABLE IF EXISTS `learning_learningrecommendation`;
CREATE TABLE `learning_learningrecommendation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recommendation_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reason` longtext COLLATE utf8mb4_unicode_ci,
  `score` double NOT NULL,
  `recommended_at` datetime(6) NOT NULL,
  `user_feedback` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `feedback_at` datetime(6) DEFAULT NULL,
  `book_id` int(11) DEFAULT NULL,
  `chapter_id` int(11) DEFAULT NULL,
  `exercise_id` int(11) DEFAULT NULL,
  `roadmap_id` int(11) DEFAULT NULL,
  `stage_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  `user_path_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_learningrec_book_id_fa4f41fb_fk_books_boo` (`book_id`),
  KEY `learning_learningrec_chapter_id_6e6931d9_fk_books_cha` (`chapter_id`),
  KEY `learning_learningrec_exercise_id_b1f3fa44_fk_learning_` (`exercise_id`),
  KEY `learning_learningrec_roadmap_id_14159915_fk_learning_` (`roadmap_id`),
  KEY `learning_learningrec_stage_id_b0adc32c_fk_learning_` (`stage_id`),
  KEY `learning_learningrec_user_id_60ea181f_fk_users_use` (`user_id`),
  KEY `learning_learningrec_user_path_id_d8ab5be3_fk_learning_` (`user_path_id`),
  CONSTRAINT `learning_learningrec_book_id_fa4f41fb_fk_books_boo` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `learning_learningrec_chapter_id_6e6931d9_fk_books_cha` FOREIGN KEY (`chapter_id`) REFERENCES `books_chapter` (`id`),
  CONSTRAINT `learning_learningrec_exercise_id_b1f3fa44_fk_learning_` FOREIGN KEY (`exercise_id`) REFERENCES `learning_exercise` (`id`),
  CONSTRAINT `learning_learningrec_roadmap_id_14159915_fk_learning_` FOREIGN KEY (`roadmap_id`) REFERENCES `learning_roadmaptemplate` (`id`),
  CONSTRAINT `learning_learningrec_stage_id_b0adc32c_fk_learning_` FOREIGN KEY (`stage_id`) REFERENCES `learning_roadmapstage` (`id`),
  CONSTRAINT `learning_learningrec_user_id_60ea181f_fk_users_use` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `learning_learningrec_user_path_id_d8ab5be3_fk_learning_` FOREIGN KEY (`user_path_id`) REFERENCES `learning_userlearningpath` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_learningrecommendation
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_learningrecord`
-- ----------------------------
DROP TABLE IF EXISTS `learning_learningrecord`;
CREATE TABLE `learning_learningrecord` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `progress` int(11) NOT NULL,
  `last_learn_time` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `book_id` int(11) NOT NULL,
  `chapter_id` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `learning_learningrecord_user_id_book_id_chapter_id_65fd4047_uniq` (`user_id`,`book_id`,`chapter_id`),
  KEY `learning_learningrecord_book_id_7c1e132b_fk_books_book_id` (`book_id`),
  KEY `learning_learningrecord_chapter_id_4189fa50_fk_books_chapter_id` (`chapter_id`),
  CONSTRAINT `learning_learningrecord_book_id_7c1e132b_fk_books_book_id` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `learning_learningrecord_chapter_id_4189fa50_fk_books_chapter_id` FOREIGN KEY (`chapter_id`) REFERENCES `books_chapter` (`id`),
  CONSTRAINT `learning_learningrecord_user_id_ed465a70_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_learningrecord
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_learningstyle`
-- ----------------------------
DROP TABLE IF EXISTS `learning_learningstyle`;
CREATE TABLE `learning_learningstyle` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `visual_score` double NOT NULL,
  `auditory_score` double NOT NULL,
  `reading_score` double NOT NULL,
  `kinesthetic_score` double NOT NULL,
  `pace_preference` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `environment_preference` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `preferred_resource_types` json NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `learning_learningstyle_user_id_32b4b42b_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_learningstyle
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_note`
-- ----------------------------
DROP TABLE IF EXISTS `learning_note`;
CREATE TABLE `learning_note` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `book_id` int(11) DEFAULT NULL,
  `chapter_id` int(11) DEFAULT NULL,
  `is_favorite` tinyint(1) NOT NULL,
  `is_public` tinyint(1) NOT NULL,
  `last_reviewed_at` datetime(6) DEFAULT NULL,
  `position` longtext COLLATE utf8mb4_unicode_ci,
  `view_count` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_note_chapter_id_52bcce73_fk_books_chapter_id` (`chapter_id`),
  KEY `learning_no_user_id_2d0f6a_idx` (`user_id`,`updated_at` DESC),
  KEY `learning_no_book_id_5a411d_idx` (`book_id`,`chapter_id`),
  KEY `learning_no_is_favo_a18781_idx` (`is_favorite`),
  CONSTRAINT `learning_note_book_id_c45e713e_fk_books_book_id` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `learning_note_chapter_id_52bcce73_fk_books_chapter_id` FOREIGN KEY (`chapter_id`) REFERENCES `books_chapter` (`id`),
  CONSTRAINT `learning_note_user_id_98c88ac5_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_note
-- ----------------------------
INSERT INTO learning_note VALUES ('1', '来自《大学计算机基础与应用》的笔记', '<blockquote>计算机系统由硬件系统和软件系统两大部</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.841066', '2026-01-05 09:01:21.841066', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('2', '来自《大学计算机基础与应用》的笔记', '<blockquote>备和输出设备等。</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.839421', '2026-01-05 09:01:21.839421', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('3', '来自《大学计算机基础与应用》的笔记', '<blockquote>和软件系统两大部</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.837895', '2026-01-05 09:01:21.837895', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('4', '来自《大学计算机基础与应用》的笔记', '<blockquote>分组成。硬件系统是计算机的物理</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.836370', '2026-01-05 09:01:21.836370', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('5', '来自《大学计算机基础与应用》的笔记', '<blockquote>硬件系统是计</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.834789', '2026-01-05 09:01:21.834789', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('6', '来自《大学计算机基础与应用》的笔记', '<blockquote>两大部分组成。硬件系统是</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.832995', '2026-01-05 09:01:21.832995', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('7', '来自《大学计算机基础与应用》的笔记', '<blockquote>和软件系统两大部分组成。硬件系统是计算机的物理组成部分，包括中央处理器(CPU)、内存、存储设备、输入设备和输出</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.831985', '2026-01-05 09:01:21.831985', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('8', '来自《大学计算机基础与应用》的笔记', '<blockquote>件。</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.829817', '2026-01-05 09:01:21.829817', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('9', '来自《大学计算机基础与应用》的笔记', '<blockquote>成。硬件系统是</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.826735', '2026-01-05 09:01:21.826735', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('10', '来自《大学计算机基础与应用》的笔记', '<blockquote>成。硬件系统是</blockquote>\n\n在章节：第1章 计算机基础知识', '2026-01-05 09:01:21.826735', '2026-01-05 09:01:21.826735', '2', '1', '1', '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('11', '无标题笔记', '', '2026-01-05 09:01:21.825208', '2026-01-05 09:01:21.825208', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('12', '无标题笔记', '', '2026-01-05 09:01:21.823672', '2026-01-05 09:01:21.823672', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('13', '无标题笔记', '', '2026-01-05 09:01:21.823672', '2026-01-05 09:01:21.823672', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('14', '无标题笔记', '<p><br></p>', '2026-01-05 09:01:21.822106', '2026-01-05 09:01:21.822106', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('15', '无标题笔记', '<p><br></p>', '2026-01-05 09:01:21.822106', '2026-01-05 09:01:21.822106', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('16', '无标题笔记', '', '2026-01-05 09:01:21.822106', '2026-01-05 09:01:21.822106', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('17', '无标题笔记', '<p><br></p>', '2026-01-05 09:01:21.820557', '2026-01-05 09:01:21.820557', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('18', '无标题笔记', '<p><br></p>', '2026-01-05 09:01:21.820557', '2026-01-05 09:01:21.820557', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('19', '无标题笔记', '<p><br></p>', '2026-01-05 09:01:21.818996', '2026-01-05 09:01:21.818996', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('20', '无标题笔记', '<p><br></p>', '2026-01-05 09:01:21.818996', '2026-01-05 09:01:21.818996', '2', null, null, '0', '0', null, null, '0');
INSERT INTO learning_note VALUES ('21', '无标题笔记', '<p><br></p>', '2026-01-05 09:01:21.816368', '2026-01-05 09:01:21.816368', '2', null, null, '0', '0', null, null, '0');

-- ----------------------------
-- Table structure for `learning_noteattachment`
-- ----------------------------
DROP TABLE IF EXISTS `learning_noteattachment`;
CREATE TABLE `learning_noteattachment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` int(11) NOT NULL,
  `file_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `note_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_noteattachment_note_id_81a9eb7f_fk_learning_note_id` (`note_id`),
  CONSTRAINT `learning_noteattachment_note_id_81a9eb7f_fk_learning_note_id` FOREIGN KEY (`note_id`) REFERENCES `learning_note` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_noteattachment
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_noteshare`
-- ----------------------------
DROP TABLE IF EXISTS `learning_noteshare`;
CREATE TABLE `learning_noteshare` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `share_code` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `view_count` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `note_id` int(11) NOT NULL,
  `shared_by_id` bigint(20) NOT NULL,
  `shared_to_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `share_code` (`share_code`),
  KEY `learning_noteshare_note_id_f75af4d0_fk_learning_note_id` (`note_id`),
  KEY `learning_noteshare_shared_by_id_b12b9914_fk_users_user_id` (`shared_by_id`),
  KEY `learning_noteshare_shared_to_id_27ecf05a_fk_users_user_id` (`shared_to_id`),
  CONSTRAINT `learning_noteshare_note_id_f75af4d0_fk_learning_note_id` FOREIGN KEY (`note_id`) REFERENCES `learning_note` (`id`),
  CONSTRAINT `learning_noteshare_shared_by_id_b12b9914_fk_users_user_id` FOREIGN KEY (`shared_by_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `learning_noteshare_shared_to_id_27ecf05a_fk_users_user_id` FOREIGN KEY (`shared_to_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_noteshare
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_notetag`
-- ----------------------------
DROP TABLE IF EXISTS `learning_notetag`;
CREATE TABLE `learning_notetag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `learning_notetag_user_id_name_9901d7c0_uniq` (`user_id`,`name`),
  CONSTRAINT `learning_notetag_user_id_ee30ff18_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_notetag
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_notetagrelation`
-- ----------------------------
DROP TABLE IF EXISTS `learning_notetagrelation`;
CREATE TABLE `learning_notetagrelation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `note_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `learning_notetagrelation_note_id_tag_id_95cd0cb6_uniq` (`note_id`,`tag_id`),
  KEY `learning_notetagrelation_tag_id_775886a4_fk_learning_notetag_id` (`tag_id`),
  CONSTRAINT `learning_notetagrelation_note_id_85215209_fk_learning_note_id` FOREIGN KEY (`note_id`) REFERENCES `learning_note` (`id`),
  CONSTRAINT `learning_notetagrelation_tag_id_775886a4_fk_learning_notetag_id` FOREIGN KEY (`tag_id`) REFERENCES `learning_notetag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_notetagrelation
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_noteversion`
-- ----------------------------
DROP TABLE IF EXISTS `learning_noteversion`;
CREATE TABLE `learning_noteversion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `version_number` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `note_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_noteversion_note_id_660edfd6_fk_learning_note_id` (`note_id`),
  CONSTRAINT `learning_noteversion_note_id_660edfd6_fk_learning_note_id` FOREIGN KEY (`note_id`) REFERENCES `learning_note` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_noteversion
-- ----------------------------
INSERT INTO learning_noteversion VALUES ('1', '来自《大学计算机基础与应用》的笔记', '<blockquote>计算机系统由硬件系统和软件系统两大部</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.847109', '1');
INSERT INTO learning_noteversion VALUES ('2', '来自《大学计算机基础与应用》的笔记', '<blockquote>备和输出设备等。</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.848694', '2');
INSERT INTO learning_noteversion VALUES ('3', '来自《大学计算机基础与应用》的笔记', '<blockquote>和软件系统两大部</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.848694', '3');
INSERT INTO learning_noteversion VALUES ('4', '来自《大学计算机基础与应用》的笔记', '<blockquote>分组成。硬件系统是计算机的物理</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.850237', '4');
INSERT INTO learning_noteversion VALUES ('5', '来自《大学计算机基础与应用》的笔记', '<blockquote>硬件系统是计</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.850237', '5');
INSERT INTO learning_noteversion VALUES ('6', '来自《大学计算机基础与应用》的笔记', '<blockquote>两大部分组成。硬件系统是</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.851781', '6');
INSERT INTO learning_noteversion VALUES ('7', '来自《大学计算机基础与应用》的笔记', '<blockquote>和软件系统两大部分组成。硬件系统是计算机的物理组成部分，包括中央处理器(CPU)、内存、存储设备、输入设备和输出</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.851781', '7');
INSERT INTO learning_noteversion VALUES ('8', '来自《大学计算机基础与应用》的笔记', '<blockquote>件。</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.853320', '8');
INSERT INTO learning_noteversion VALUES ('9', '来自《大学计算机基础与应用》的笔记', '<blockquote>成。硬件系统是</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.853320', '9');
INSERT INTO learning_noteversion VALUES ('10', '来自《大学计算机基础与应用》的笔记', '<blockquote>成。硬件系统是</blockquote>\n\n在章节：第1章 计算机基础知识', '1', '2026-01-05 09:01:21.853320', '10');
INSERT INTO learning_noteversion VALUES ('11', '无标题笔记', '', '1', '2026-01-05 09:01:21.854887', '11');
INSERT INTO learning_noteversion VALUES ('12', '无标题笔记', '', '1', '2026-01-05 09:01:21.854887', '12');
INSERT INTO learning_noteversion VALUES ('13', '无标题笔记', '', '1', '2026-01-05 09:01:21.854887', '13');
INSERT INTO learning_noteversion VALUES ('14', '无标题笔记', '', '1', '2026-01-05 09:01:21.856418', '14');
INSERT INTO learning_noteversion VALUES ('15', '无标题笔记', '', '2', '2026-01-05 09:01:21.842608', '14');
INSERT INTO learning_noteversion VALUES ('16', '无标题笔记', '', '1', '2026-01-05 09:01:21.856418', '15');
INSERT INTO learning_noteversion VALUES ('17', '无标题笔记', '', '2', '2026-01-05 09:01:21.842608', '15');
INSERT INTO learning_noteversion VALUES ('18', '无标题笔记', '', '1', '2026-01-05 09:01:21.856418', '16');
INSERT INTO learning_noteversion VALUES ('19', '无标题笔记', '', '1', '2026-01-05 09:01:21.857942', '17');
INSERT INTO learning_noteversion VALUES ('20', '无标题笔记', '', '2', '2026-01-05 09:01:21.844140', '17');
INSERT INTO learning_noteversion VALUES ('21', '无标题笔记', '', '1', '2026-01-05 09:01:21.857942', '18');
INSERT INTO learning_noteversion VALUES ('22', '无标题笔记', '', '2', '2026-01-05 09:01:21.844140', '18');
INSERT INTO learning_noteversion VALUES ('23', '无标题笔记', '', '1', '2026-01-05 09:01:21.859478', '19');
INSERT INTO learning_noteversion VALUES ('24', '无标题笔记', '', '2', '2026-01-05 09:01:21.844140', '19');
INSERT INTO learning_noteversion VALUES ('25', '无标题笔记', '', '1', '2026-01-05 09:01:21.859478', '20');
INSERT INTO learning_noteversion VALUES ('26', '无标题笔记', '', '2', '2026-01-05 09:01:21.845765', '20');
INSERT INTO learning_noteversion VALUES ('27', '无标题笔记', '', '1', '2026-01-05 09:01:21.859478', '21');
INSERT INTO learning_noteversion VALUES ('28', '无标题笔记', '', '2', '2026-01-05 09:01:21.845765', '21');

-- ----------------------------
-- Table structure for `learning_practicerecord`
-- ----------------------------
DROP TABLE IF EXISTS `learning_practicerecord`;
CREATE TABLE `learning_practicerecord` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `score` int(11) NOT NULL,
  `completed` tinyint(1) NOT NULL,
  `user_code` longtext COLLATE utf8mb4_unicode_ci,
  `completed_time` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `book_id` int(11) NOT NULL,
  `chapter_id` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_practicerecord_book_id_cbe92c81_fk_books_book_id` (`book_id`),
  KEY `learning_practicerecord_chapter_id_30b38c81_fk_books_chapter_id` (`chapter_id`),
  KEY `learning_practicerecord_user_id_3b36a740_fk_users_user_id` (`user_id`),
  CONSTRAINT `learning_practicerecord_book_id_cbe92c81_fk_books_book_id` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `learning_practicerecord_chapter_id_30b38c81_fk_books_chapter_id` FOREIGN KEY (`chapter_id`) REFERENCES `books_chapter` (`id`),
  CONSTRAINT `learning_practicerecord_user_id_3b36a740_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_practicerecord
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_roadmapbook`
-- ----------------------------
DROP TABLE IF EXISTS `learning_roadmapbook`;
CREATE TABLE `learning_roadmapbook` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `recommended_order` int(11) NOT NULL,
  `importance` int(11) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci,
  `book_id` int(11) NOT NULL,
  `stage_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_roadmapbook_book_id_79422470_fk_books_book_id` (`book_id`),
  KEY `learning_roadmapbook_stage_id_dc6510c4_fk_learning_` (`stage_id`),
  CONSTRAINT `learning_roadmapbook_book_id_79422470_fk_books_book_id` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `learning_roadmapbook_stage_id_dc6510c4_fk_learning_` FOREIGN KEY (`stage_id`) REFERENCES `learning_roadmapstage` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_roadmapbook
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_roadmapstage`
-- ----------------------------
DROP TABLE IF EXISTS `learning_roadmapstage`;
CREATE TABLE `learning_roadmapstage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `stage_order` int(11) NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `learning_goals` json NOT NULL,
  `required_skills` json NOT NULL,
  `estimated_duration` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `roadmap_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_roadmapstag_roadmap_id_7761cc5c_fk_learning_` (`roadmap_id`),
  CONSTRAINT `learning_roadmapstag_roadmap_id_7761cc5c_fk_learning_` FOREIGN KEY (`roadmap_id`) REFERENCES `learning_roadmaptemplate` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_roadmapstage
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_roadmaptemplate`
-- ----------------------------
DROP TABLE IF EXISTS `learning_roadmaptemplate`;
CREATE TABLE `learning_roadmaptemplate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `major` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `difficulty_level` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estimated_hours` int(11) NOT NULL,
  `tags` json NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_roadmaptemplate
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_userlearningpath`
-- ----------------------------
DROP TABLE IF EXISTS `learning_userlearningpath`;
CREATE TABLE `learning_userlearningpath` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `progress` int(11) NOT NULL,
  `started_at` datetime(6) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `custom_goals` json NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `current_stage_id` bigint(20) DEFAULT NULL,
  `roadmap_id` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `learning_userlearningpath_user_id_roadmap_id_aef05b72_uniq` (`user_id`,`roadmap_id`),
  KEY `learning_userlearnin_current_stage_id_0ec7d5f3_fk_learning_` (`current_stage_id`),
  KEY `learning_userlearnin_roadmap_id_1dee3a22_fk_learning_` (`roadmap_id`),
  CONSTRAINT `learning_userlearnin_current_stage_id_0ec7d5f3_fk_learning_` FOREIGN KEY (`current_stage_id`) REFERENCES `learning_roadmapstage` (`id`),
  CONSTRAINT `learning_userlearnin_roadmap_id_1dee3a22_fk_learning_` FOREIGN KEY (`roadmap_id`) REFERENCES `learning_roadmaptemplate` (`id`),
  CONSTRAINT `learning_userlearningpath_user_id_9de86145_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_userlearningpath
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_userpathstage`
-- ----------------------------
DROP TABLE IF EXISTS `learning_userpathstage`;
CREATE TABLE `learning_userpathstage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `progress` int(11) NOT NULL,
  `is_completed` tinyint(1) NOT NULL,
  `started_at` datetime(6) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci,
  `stage_id` bigint(20) NOT NULL,
  `user_path_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `learning_userpathstage_user_path_id_stage_id_d82b2a79_uniq` (`user_path_id`,`stage_id`),
  KEY `learning_userpathsta_stage_id_8ff84cc4_fk_learning_` (`stage_id`),
  CONSTRAINT `learning_userpathsta_stage_id_8ff84cc4_fk_learning_` FOREIGN KEY (`stage_id`) REFERENCES `learning_roadmapstage` (`id`),
  CONSTRAINT `learning_userpathsta_user_path_id_1a76f5f9_fk_learning_` FOREIGN KEY (`user_path_id`) REFERENCES `learning_userlearningpath` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_userpathstage
-- ----------------------------

-- ----------------------------
-- Table structure for `learning_wrongquestion`
-- ----------------------------
DROP TABLE IF EXISTS `learning_wrongquestion`;
CREATE TABLE `learning_wrongquestion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `difficulty` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `book_id` int(11) DEFAULT NULL,
  `chapter_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  `attempt_time` datetime(6) NOT NULL,
  `practice_id` int(11) DEFAULT NULL,
  `question_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `learning_wrongquestion_user_id_4836267f_fk_users_user_id` (`user_id`),
  KEY `learning_wrongquesti_practice_id_bc88438e_fk_learning_` (`practice_id`),
  KEY `learning_wrongquestion_book_id_90495cce_fk_books_book_id` (`book_id`),
  KEY `learning_wrongquestion_chapter_id_08d3a9d1_fk_books_chapter_id` (`chapter_id`),
  CONSTRAINT `learning_wrongquesti_practice_id_bc88438e_fk_learning_` FOREIGN KEY (`practice_id`) REFERENCES `learning_exercise` (`id`),
  CONSTRAINT `learning_wrongquestion_book_id_90495cce_fk_books_book_id` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `learning_wrongquestion_chapter_id_08d3a9d1_fk_books_chapter_id` FOREIGN KEY (`chapter_id`) REFERENCES `books_chapter` (`id`),
  CONSTRAINT `learning_wrongquestion_user_id_4836267f_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of learning_wrongquestion
-- ----------------------------

-- ----------------------------
-- Table structure for `toolkit_executionhistory`
-- ----------------------------
DROP TABLE IF EXISTS `toolkit_executionhistory`;
CREATE TABLE `toolkit_executionhistory` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `parameters` json NOT NULL,
  `result` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `error_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `tool_id` int(11) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `toolkit_executionhistory_tool_id_a7be6175_fk_toolkit_tool_id` (`tool_id`),
  KEY `toolkit_executionhistory_user_id_d6df0256_fk_users_user_id` (`user_id`),
  CONSTRAINT `toolkit_executionhistory_tool_id_a7be6175_fk_toolkit_tool_id` FOREIGN KEY (`tool_id`) REFERENCES `toolkit_tool` (`id`),
  CONSTRAINT `toolkit_executionhistory_user_id_d6df0256_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of toolkit_executionhistory
-- ----------------------------
INSERT INTO toolkit_executionhistory VALUES ('1', '{\"text\": \"??????\"}', '', 'failed', '请输入文件夹路径；请输入命名模式', '2026-01-05 09:04:13.588604', '1');
INSERT INTO toolkit_executionhistory VALUES ('2', '{\"text\": \"??????????,????TextExtractTool????\"}', '', 'failed', '请输入文件路径', '2026-01-05 09:04:13.590157', '5');
INSERT INTO toolkit_executionhistory VALUES ('3', '{\"jsonText\": \"{\\\"name\\\":\\\"??\\\",\\\"value\\\":123}\"}', '', 'failed', '请输入JSON内容', '2026-01-05 09:04:13.590157', '6');
INSERT INTO toolkit_executionhistory VALUES ('4', '{\"columns\": \"\", \"filePath\": \"\", \"sheetName\": \"\"}', '', 'failed', '请输入JSON内容', '2026-01-05 09:04:13.591700', '6');
INSERT INTO toolkit_executionhistory VALUES ('5', '{\"columns\": \"\", \"filePath\": \"\", \"sheetName\": \"\"}', '', 'failed', '请输入JSON内容', '2026-01-05 09:04:13.591700', '6');
INSERT INTO toolkit_executionhistory VALUES ('6', '{\"columns\": \"\", \"filePath\": \"\", \"sheetName\": \"\"}', '', 'failed', '请输入JSON内容', '2026-01-05 09:04:13.593240', '6');
INSERT INTO toolkit_executionhistory VALUES ('7', '{\"columns\": \"\", \"filePath\": \"\", \"sheetName\": \"\"}', '', 'failed', '请输入JSON内容', '2026-01-05 09:04:13.593240', '6');
INSERT INTO toolkit_executionhistory VALUES ('8', '{\"indentSize\": 2, \"jsonContent\": \"{\\\"name\\\":\\\"??\\\",\\\"value\\\":123}\"}', '{\"success\": true, \"result\": {\"message\": \"JSON\\u683c\\u5f0f\\u5316\\u6210\\u529f\", \"formatted_json\": \"{\\n  \\\"name\\\": \\\"??\\\",\\n  \\\"value\\\": 123\\n}\", \"statistics\": {\"original_size\": 25, \"formatted_size\": 34, \"size_difference\": 9, \"indent_size\": 2}}, \"error\": null}', 'success', '', '2026-01-05 09:04:13.594803', '6');
INSERT INTO toolkit_executionhistory VALUES ('9', '{\"columns\": \"\", \"filePath\": \"\", \"sheetName\": \"\"}', '', 'failed', '请输入JSON内容', '2026-01-05 09:04:13.594803', '6');
INSERT INTO toolkit_executionhistory VALUES ('10', '{\"columns\": \"A,B,C\", \"filePath\": \"D:\\\\文档\\\\数字教材\", \"sheetName\": \"Sheet1\"}', '', 'failed', '请输入JSON内容', '2026-01-05 09:04:13.596348', '6');
INSERT INTO toolkit_executionhistory VALUES ('11', '{\"columns\": \"A,B,C\", \"filePath\": \"D:\\\\文档\\\\数字教材\\\\1.\", \"sheetName\": \"Sheet1\"}', '', 'failed', '请输入JSON内容', '2026-01-05 09:04:13.597884', '6');

-- ----------------------------
-- Table structure for `toolkit_tool`
-- ----------------------------
DROP TABLE IF EXISTS `toolkit_tool`;
CREATE TABLE `toolkit_tool` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `icon` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `book_id` int(11) DEFAULT NULL,
  `book_title` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `chapter_number` int(11) DEFAULT NULL,
  `first_section_id` int(11) DEFAULT NULL,
  `implementation_class` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `category_id` bigint(20) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `toolkit_tool_category_id_16177411_fk_toolkit_toolcategory_id` (`category_id`),
  CONSTRAINT `toolkit_tool_category_id_16177411_fk_toolkit_toolcategory_id` FOREIGN KEY (`category_id`) REFERENCES `toolkit_toolcategory` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of toolkit_tool
-- ----------------------------
INSERT INTO toolkit_tool VALUES ('1', '批量重命名文件夹中的文件', 'file-text', null, '', null, null, 'file_tools.FileRenameTool', '1', '2026-01-05 09:04:13.567886', '2026-01-05 09:04:13.567886', '1', '批量重命名文件', 'file-rename');
INSERT INTO toolkit_tool VALUES ('2', '合并多个Excel文件到一个工作簿', 'table', null, '', null, null, 'file_tools.ExcelMergeTool', '1', '2026-01-05 09:04:13.569526', '2026-01-05 09:04:13.569526', '1', 'Excel表格合并', 'excel-merge');
INSERT INTO toolkit_tool VALUES ('3', '分析Excel或CSV文件中的数据', 'bar-chart', null, '', null, null, 'data_tools.DataAnalysisTool', '1', '2026-01-05 09:04:13.571083', '2026-01-05 09:04:13.571083', '2', '数据统计分析', 'data-analysis');
INSERT INTO toolkit_tool VALUES ('4', '批量压缩文件夹中的图片文件', 'image', null, '', null, null, 'image_tools.ImageCompressTool', '1', '2026-01-05 09:04:13.571083', '2026-01-05 09:04:13.571083', '3', '图片批量压缩', 'image-compress');
INSERT INTO toolkit_tool VALUES ('5', '从各种文件中提取文本内容', 'align-left', null, '', null, null, 'text_tools.TextExtractTool', '1', '2026-01-05 09:04:13.572615', '2026-01-05 09:04:13.572615', '4', '文本内容提取', 'text-extract');
INSERT INTO toolkit_tool VALUES ('6', '格式化和美化JSON字符串', 'code', null, '', null, null, 'text_tools.JsonFormatTool', '1', '2026-01-05 09:04:13.572615', '2026-01-05 09:04:13.572615', '4', 'JSON格式化', 'json-format');

-- ----------------------------
-- Table structure for `toolkit_toolcategory`
-- ----------------------------
DROP TABLE IF EXISTS `toolkit_toolcategory`;
CREATE TABLE `toolkit_toolcategory` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of toolkit_toolcategory
-- ----------------------------
INSERT INTO toolkit_toolcategory VALUES ('1', '文件处理', 'file', '处理各种文件的工具集合', '2026-01-05 09:04:13.565371', '2026-01-05 09:04:13.565371');
INSERT INTO toolkit_toolcategory VALUES ('2', '数据处理', 'data', '数据分析和处理工具', '2026-01-05 09:04:13.566881', '2026-01-05 09:04:13.566881');
INSERT INTO toolkit_toolcategory VALUES ('3', '图片处理', 'image', '图片编辑和优化工具', '2026-01-05 09:04:13.566881', '2026-01-05 09:04:13.566881');
INSERT INTO toolkit_toolcategory VALUES ('4', '文本处理', 'text', '文本分析和转换工具', '2026-01-05 09:04:13.566881', '2026-01-05 09:04:13.566881');

-- ----------------------------
-- Table structure for `toolkit_toolparameter`
-- ----------------------------
DROP TABLE IF EXISTS `toolkit_toolparameter`;
CREATE TABLE `toolkit_toolparameter` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `placeholder` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `default_value` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_required` tinyint(1) NOT NULL,
  `options` json NOT NULL,
  `order` int(11) NOT NULL,
  `tool_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `toolkit_toolparameter_tool_id_1644c523_fk_toolkit_tool_id` (`tool_id`),
  CONSTRAINT `toolkit_toolparameter_tool_id_1644c523_fk_toolkit_tool_id` FOREIGN KEY (`tool_id`) REFERENCES `toolkit_tool` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of toolkit_toolparameter
-- ----------------------------
INSERT INTO toolkit_toolparameter VALUES ('1', 'folderPath', '文件夹路径', 'text', '例如: C:\\Users\\Documents\\Files', '', '1', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('2', 'namingPattern', '命名模式', 'text', '例如: File_{index}.txt', 'File_{index}', '1', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('3', 'fileType', '文件类型筛选', 'text', '例如: .txt,.pdf', '', '0', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('4', 'folderPath', '文件夹路径', 'text', '例如: C:\\Users\\Documents\\ExcelFiles', '', '1', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('5', 'outputFileName', '输出文件名', 'text', '例如: merged_data.xlsx', 'merged_data.xlsx', '1', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('6', 'includeHeaders', '包含表头', 'boolean', '', 'True', '0', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('7', 'filePath', '文件路径', 'text', '例如: C:\\Users\\Documents\\data.xlsx', '', '1', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('8', 'sheetName', '工作表名称', 'text', '例如: Sheet1', '', '0', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('9', 'analysisColumn', '分析列', 'text', '例如: sales', '', '1', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('10', 'folderPath', '文件夹路径', 'text', '例如: C:\\Users\\Documents\\Images', '', '1', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('11', 'quality', '压缩质量', 'number', '', '80', '0', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('12', 'maxWidth', '最大宽度', 'number', '', '1920', '0', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('13', 'filePath', '文件路径', 'text', '例如: C:\\Users\\Documents\\sample.pdf', '', '1', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('14', 'outputFormat', '输出格式', 'select', '', 'txt', '0', '[\"txt\", \"json\", \"markdown\"]', '0');
INSERT INTO toolkit_toolparameter VALUES ('15', 'jsonContent', 'JSON内容', 'textarea', '例如: {\"name\":\"value\"}', '', '1', '[]', '0');
INSERT INTO toolkit_toolparameter VALUES ('16', 'indentSize', '缩进大小', 'number', '', '2', '0', '[]', '0');

-- ----------------------------
-- Table structure for `users_user`
-- ----------------------------
DROP TABLE IF EXISTS `users_user`;
CREATE TABLE `users_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `avatar` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of users_user
-- ----------------------------
INSERT INTO users_user VALUES ('1', 'pbkdf2_sha256$600000$0O2hL1EyBbitiWbtHdvFDs$oDan8Jh3Lw1NI7RCbV1D6d0UZ9HOhwN3jXB+uOLIxBY=', null, '1', 'admin', '', '', '1', '1', '2025-10-29 07:12:37.306572', '', 'admin@example.com');
INSERT INTO users_user VALUES ('2', 'pbkdf2_sha256$600000$v82Z4YKjvzrgESnx3WC7SH$emZv0w2uQOBI8NEdQ9CaiPhe5AvmI/D+gGHkKMOHZQ8=', null, '0', 'student', '', '', '0', '1', '2025-10-29 07:12:37.620634', '', 'student@example.com');

-- ----------------------------
-- Table structure for `users_userpreferences`
-- ----------------------------
DROP TABLE IF EXISTS `users_userpreferences`;
CREATE TABLE `users_userpreferences` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `default_language` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code_theme` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `auto_play_video` tinyint(1) NOT NULL,
  `keyboard_shortcuts` tinyint(1) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `users_userpreferences_user_id_c5a5f271_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of users_userpreferences
-- ----------------------------
INSERT INTO users_userpreferences VALUES ('1', 'python', 'vs-dark', '0', '1', '1');
INSERT INTO users_userpreferences VALUES ('2', 'python', 'vs-dark', '1', '1', '2');

-- ----------------------------
-- Table structure for `users_user_groups`
-- ----------------------------
DROP TABLE IF EXISTS `users_user_groups`;
CREATE TABLE `users_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_groups_user_id_group_id_b88eab82_uniq` (`user_id`,`group_id`),
  KEY `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` (`group_id`),
  CONSTRAINT `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `users_user_groups_user_id_5f6f5a90_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of users_user_groups
-- ----------------------------

-- ----------------------------
-- Table structure for `users_user_user_permissions`
-- ----------------------------
DROP TABLE IF EXISTS `users_user_user_permissions`;
CREATE TABLE `users_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_user_permissions_user_id_permission_id_43338c45_uniq` (`user_id`,`permission_id`),
  KEY `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_user_permissions_user_id_20aca447_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of users_user_user_permissions
-- ----------------------------
