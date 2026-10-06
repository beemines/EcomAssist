-- 演示种子可重复执行；保留已有数据，不占用 demo-user 的新会话。
SET NAMES utf8mb4;
START TRANSACTION;

INSERT INTO conversations (user_id, status)
SELECT 'seed-user', '已转人工'
WHERE NOT EXISTS (SELECT 1 FROM conversations WHERE user_id = 'seed-user');
SET @seed_conversation_id = (SELECT MIN(id) FROM conversations WHERE user_id = 'seed-user');

INSERT INTO messages (conversation_id, role, content)
SELECT @seed_conversation_id, 'user', '收到的商品有破损，我想申请退货。'
WHERE NOT EXISTS (SELECT 1 FROM messages WHERE conversation_id = @seed_conversation_id AND role = 'user');
INSERT INTO messages (conversation_id, role, content)
SELECT @seed_conversation_id, 'assistant', '已为您记录售后问题并转交人工客服，请保留商品和包装照片。'
WHERE NOT EXISTS (SELECT 1 FROM messages WHERE conversation_id = @seed_conversation_id AND role = 'assistant');

INSERT INTO tickets (ticket_no, conversation_id, description, ticket_type)
SELECT 'Tseed000000000000000000000000001', @seed_conversation_id, '用户收到商品破损，申请人工处理退货。', '售后'
WHERE NOT EXISTS (SELECT 1 FROM tickets WHERE ticket_no = 'Tseed000000000000000000000000001');

INSERT INTO faq (question, answer, category)
SELECT '如何申请退货？', '请提供订单号及退货原因，商品符合退货条件时可申请售后，具体由人工客服核实。', '售后'
WHERE NOT EXISTS (SELECT 1 FROM faq WHERE question = '如何申请退货？');
INSERT INTO faq (question, answer, category)
SELECT '退货运费由谁承担？', '商品质量问题的退货运费由商家承担；其他原因以商品页面及售后审核结果为准。', '运费'
WHERE NOT EXISTS (SELECT 1 FROM faq WHERE question = '退货运费由谁承担？');

COMMIT;
