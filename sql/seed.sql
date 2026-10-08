-- 演示种子可重复执行；保留已有数据，不占用 demo-user 的新会话。
SET NAMES utf8mb4;
-- 四类示例数据作为一笔事务提交，避免只写入会话却没有对应消息或工单。
START TRANSACTION;

-- 只补不存在的 seed-user 会话，再取稳定的最早主键供后续关联。
INSERT INTO conversations (user_id, status)
SELECT 'seed-user', '已转人工'
WHERE NOT EXISTS (SELECT 1 FROM conversations WHERE user_id = 'seed-user');
SET @seed_conversation_id = (SELECT MIN(id) FROM conversations WHERE user_id = 'seed-user');

-- 各角色示例只补一次，重复执行不会不断追加相同演示消息。
INSERT INTO messages (conversation_id, role, content)
SELECT @seed_conversation_id, 'user', '收到的商品有破损，我想申请退货。'
WHERE NOT EXISTS (SELECT 1 FROM messages WHERE conversation_id = @seed_conversation_id AND role = 'user');
INSERT INTO messages (conversation_id, role, content)
SELECT @seed_conversation_id, 'assistant', '已为您记录售后问题并转交人工客服，请保留商品和包装照片。'
WHERE NOT EXISTS (SELECT 1 FROM messages WHERE conversation_id = @seed_conversation_id AND role = 'assistant');

-- 使用固定演示工单号关联种子会话，保持重复执行时可追踪同一份工单。
INSERT INTO tickets (ticket_no, conversation_id, description, ticket_type)
SELECT 'Tseed000000000000000000000000001', @seed_conversation_id, '用户收到商品破损，申请人工处理退货。', '售后'
WHERE NOT EXISTS (SELECT 1 FROM tickets WHERE ticket_no = 'Tseed000000000000000000000000001');

-- 保留原关键词检索阶段的 FAQ 示例，按问题原文判断是否已存在。
INSERT INTO faq (question, answer, category)
SELECT '如何申请退货？', '请提供订单号及退货原因，商品符合退货条件时可申请售后，具体由人工客服核实。', '售后'
WHERE NOT EXISTS (SELECT 1 FROM faq WHERE question = '如何申请退货？');
INSERT INTO faq (question, answer, category)
SELECT '退货运费由谁承担？', '商品质量问题的退货运费由商家承担；其他原因以商品页面及售后审核结果为准。', '运费'
WHERE NOT EXISTS (SELECT 1 FROM faq WHERE question = '退货运费由谁承担？');

-- 所有插入完成后一起提交，已有数据通过各条 NOT EXISTS 检查保留。
COMMIT;
