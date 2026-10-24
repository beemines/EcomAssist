-- 仅在原DDL之后补充已批准的版本追溯字段，旧行保持NULL。
SET NAMES utf8mb4;

ALTER TABLE topic_classifications
  ADD COLUMN model_version VARCHAR(128) NULL COMMENT '产生本结果的不可变模型版本',
  ADD COLUMN taxonomy_version VARCHAR(96) NULL COMMENT '本结果使用的17类术语表版本',
  ADD COLUMN input_hash CHAR(64) NULL COMMENT '数据库原始问题UTF-8的SHA-256',
  ADD COLUMN batch_id CHAR(36) NULL COMMENT '本次旁路归类批次UUID',
  ADD KEY idx_topic_model_version (model_version);
