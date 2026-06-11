SET NAMES utf8mb4;

INSERT INTO `user` (
  `student_no`,
  `user_name`,
  `gender`,
  `phone`,
  `email`,
  `password_hash`,
  `role`,
  `credit_score`,
  `status`,
  `verify_status`,
  `avatar_url`,
  `bio`
) VALUES
(
  '2023001001',
  '演示学生',
  '男',
  '13800000001',
  'student@campus.edu',
  '$2b$12$eM0UQzjmWFSxJ1KfQy989O2ztWTpT4IPpFDA9ym78JG/U7Q4M7spO',
  'student',
  100,
  'active',
  'verified',
  NULL,
  '用于课程演示的学生账号，明文密码：student123'
),
(
  '2023000001',
  '平台管理员',
  '女',
  '13800000002',
  'admin@campus.edu',
  '$2b$12$SiNeAziRZW2yyoQwoMrzPedLG0S189.mpwkbidbV..QC0pXUx/IxG',
  'admin',
  100,
  'active',
  'verified',
  NULL,
  '用于课程演示的管理员账号，明文密码：admin12345'
);

INSERT INTO `category` (
  `category_name`,
  `description`,
  `sort_order`,
  `status`
) VALUES
('教材资料', '课程教材、复习资料、考试笔记等', 1, 'ACTIVE'),
('数码产品', '耳机、键盘、平板等电子设备', 2, 'ACTIVE'),
('生活用品', '宿舍与校园生活常用物品', 3, 'ACTIVE');

INSERT INTO `product` (
  `seller_id`,
  `category_id`,
  `title`,
  `description`,
  `price`,
  `trade_location`,
  `status`
) VALUES
(
  1,
  1,
  '高等数学教材',
  '教材较新，适合大一新生复习和期末备考。',
  25.00,
  '图书馆南门',
  'ON_SALE'
),
(
  1,
  2,
  '二手机械键盘',
  '青轴机械键盘，自带数据线，正常使用无故障。',
  120.00,
  '一食堂门口',
  'ON_SALE'
),
(
  1,
  3,
  '宿舍小风扇',
  '支持 USB 供电，适合宿舍桌面使用。',
  35.00,
  '宿舍楼下快递点',
  'ON_SALE'
);

INSERT INTO `product_image` (
  `product_id`,
  `image_url`,
  `sort_order`
) VALUES
(1, 'https://dummyimage.com/360x240/dbeafe/1d4ed8&text=Book', 0),
(2, 'https://dummyimage.com/360x240/e0f2fe/0369a1&text=Keyboard', 0),
(3, 'https://dummyimage.com/360x240/dcfce7/047857&text=Fan', 0);
