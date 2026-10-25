-- Explicit, additive Step8 migration. No foreign keys or unique call ID.
SET NAMES utf8mb4;
CREATE TABLE IF NOT EXISTS tool_audit_logs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  conversation_id BIGINT UNSIGNED NULL,
  tool_call_id VARCHAR(64) NOT NULL,
  tool_name VARCHAR(64) NOT NULL,
  source VARCHAR(128) NOT NULL,
  arguments JSON NOT NULL,
  result_summary TEXT NOT NULL,
  status ENUM('success','failed','timeout','validation_blocked','permission_denied') NOT NULL,
  error_code VARCHAR(64) NULL,
  error_message VARCHAR(512) NULL,
  retry_count INT UNSIGNED NOT NULL,
  elapsed_ms BIGINT UNSIGNED NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_tool_audit_conversation_time (conversation_id,created_at),
  KEY idx_tool_audit_call (tool_call_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工具调用审计，无外键';
