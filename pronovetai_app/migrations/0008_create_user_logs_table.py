from django.db import migrations

# ────────────────────────────
#  DDL for pt_user_logs
#    • user_id  : BIGINT   (matches pt_users.user_id)
#    • message  : TEXT
#    • timestamp: DATETIME (auto-filled on insert)
# ────────────────────────────
SQL_CREATE = """
CREATE TABLE IF NOT EXISTS pt_user_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,          -- signed is fine
    user_id BIGINT NOT NULL,                       -- ← no UNSIGNED
    message TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX user_idx (user_id),
    CONSTRAINT pt_user_logs_user_fk
        FOREIGN KEY (user_id) REFERENCES pt_users (user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;
"""

SQL_DROP = "DROP TABLE IF EXISTS pt_user_logs;"


class Migration(migrations.Migration):

    dependencies = [
        ("pronovetai_app", "0007_create_user_m2m_tables"),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_CREATE, reverse_sql=SQL_DROP),
    ]
