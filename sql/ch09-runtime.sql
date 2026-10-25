-- step09原DDL之后的必要补充；旧行NULL不自动进入后台处理。
SET NAMES utf8mb4;

ALTER TABLE low_confidence_questions
  ADD COLUMN user_message_id BIGINT UNSIGNED NULL COMMENT '原轮用户消息ID,旧行NULL;软引用' AFTER conversation_id,
  ADD COLUMN assistant_message_id BIGINT UNSIGNED NULL COMMENT '原轮助手消息ID,同入口幂等;软引用' AFTER user_message_id,
  ADD COLUMN snapshot_status ENUM('captured','not_retrieved','unavailable') NULL COMMENT '区分真实取证、未检索和旧证据缺失' AFTER matched_review_id,
  ADD COLUMN processing JSON NULL COMMENT '版本化后台处理状态,旧NULL行默认不处理' AFTER snapshot_status,
  ADD UNIQUE KEY uk_lcq_assistant_source (assistant_message_id,source);

ALTER TABLE review_queue
  ADD COLUMN knowledge_chunk_id BIGINT UNSIGNED NULL COMMENT '本缺口唯一知识块ID,审核重放不重复创建' AFTER approved_answer,
  ADD COLUMN publication JSON NULL COMMENT '版本化发布状态,索引核验后才ready' AFTER knowledge_chunk_id,
  ADD UNIQUE KEY uk_review_knowledge_chunk (knowledge_chunk_id);

ALTER TABLE eval_runs
  ADD COLUMN run_key VARCHAR(64) NULL COMMENT '新评估UUID;重复落表幂等,旧行兼容NULL' AFTER id,
  ADD UNIQUE KEY uk_eval_run_key (run_key);
