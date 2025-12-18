-- 创建数据库用户并授予权限
CREATE USER IF NOT EXISTS 'test_user'@'%' IDENTIFIED BY '12345678';
GRANT ALL PRIVILEGES ON ai_agent_db.* TO 'test_user'@'%';
FLUSH PRIVILEGES;
