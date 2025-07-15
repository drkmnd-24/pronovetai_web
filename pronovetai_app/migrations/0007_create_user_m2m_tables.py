from django.db import migrations

# ────────────────────────────────────────────────────────────────
#  DDL that creates the two missing join-tables
#  * Use BIGINT for user_id   (matches pt_users.user_id)
#  * Use INT    for group_id  (matches auth_group.id)
#  * Use INT    for perm_id   (matches auth_permission.id)
# ────────────────────────────────────────────────────────────────
CREATE_GROUPS = """
CREATE TABLE IF NOT EXISTS pt_users_groups (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    group_id INT NOT NULL,
    UNIQUE KEY user_group_idx (user_id, group_id),
    CONSTRAINT pt_users_groups_user_fk
        FOREIGN KEY (user_id)  REFERENCES pt_users (user_id)
        ON DELETE CASCADE,
    CONSTRAINT pt_users_groups_group_fk
        FOREIGN KEY (group_id) REFERENCES auth_group (id)
        ON DELETE CASCADE
) ENGINE=InnoDB;
"""

CREATE_PERMS = """
CREATE TABLE IF NOT EXISTS pt_users_user_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY user_perm_idx (user_id, permission_id),
    CONSTRAINT pt_users_perms_user_fk
        FOREIGN KEY (user_id)      REFERENCES pt_users (user_id)
        ON DELETE CASCADE,
    CONSTRAINT pt_users_perms_perm_fk
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
        ON DELETE CASCADE
) ENGINE=InnoDB;
"""

DROP_PERMS = "DROP TABLE IF EXISTS pt_users_user_permissions;"
DROP_GROUPS = "DROP TABLE IF EXISTS pt_users_groups;"


class Migration(migrations.Migration):
    dependencies = [
        ("pronovetai_app", "0006_alter_company_options"),  # last applied migration
    ]

    operations = [
        migrations.RunSQL(
            sql=[CREATE_GROUPS, CREATE_PERMS],
            reverse_sql=[DROP_PERMS, DROP_GROUPS],
        ),
    ]
