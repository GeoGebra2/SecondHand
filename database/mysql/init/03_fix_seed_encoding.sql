SET NAMES utf8mb4;

-- Repair garbled seed text when the import client charset was wrong.
UPDATE `user`
SET
  `user_name` = '演示学生',
  `gender` = '男',
  `bio` = '用于课程演示的学生账号，明文密码：student123'
WHERE `student_no` = '2023001001'
  AND HEX(`user_name`) IN (
    'C3A6C2BCE2809DC3A7C2A4C2BAC3A5C2ADC2A6C3A7E2809DC5B8',
    '3F3F3F3F'
  );

UPDATE `user`
SET
  `user_name` = '平台管理员',
  `gender` = '女',
  `bio` = '用于课程演示的管理员账号，明文密码：admin12345'
WHERE `student_no` = '2023000001'
  AND HEX(`user_name`) IN (
    'C3A5C2B9C2B3C3A5C28FC2B0C3A7C2AEC2A1C3A7C290E280A0C3A5E28098CB9C',
    '3F3F3F3F3F'
  );

UPDATE `product`
SET
  `title` = '高等数学教材',
  `description` = '教材较新，适合大一新生复习和期末备考。',
  `trade_location` = '图书馆南门'
WHERE `product_id` = 1
  AND HEX(`title`) IN (
    'C3A9C2ABCB9CC3A7C2ADE280B0C3A6E280A2C2B0C3A5C2ADC2A6C3A6E280A2E284A2C3A6C29DC290',
    '3F3F3F3F3F3F'
  );

UPDATE `product`
SET
  `title` = '二手机械键盘',
  `description` = '青轴机械键盘，自带数据线，正常使用无故障。',
  `trade_location` = '一食堂门口'
WHERE `product_id` = 2
  AND HEX(`title`) IN (
    'C3A4C2BAC592C3A6E280B0E280B9C3A6C593C2BAC3A6C2A2C2B0C3A9E2809DC2AEC3A7E280BACB9C',
    '3F3F3F3F3F3F'
  );

UPDATE `product`
SET
  `title` = '宿舍小风扇',
  `description` = '支持 USB 供电，适合宿舍桌面使用。',
  `trade_location` = '宿舍楼下快递点'
WHERE `product_id` = 3
  AND HEX(`title`) IN (
    'C3A5C2AEC2BFC3A8CB86C28DC3A5C2B0C28FC3A9C2A3C5BDC3A6E280B0E280A1',
    '3F3F3F3F3F'
  );
