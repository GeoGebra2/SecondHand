Migration files for the SecondHand project


简化说明

当前我们保留一份幂等的 SQL 文件 `000-create-notification-if-missing.sql`，用于在 fresh clone / 首次初始化
时确保 `notification` 表存在。如果你的本地数据库是全新（没有数据卷），直接运行 `docker compose up -d mysql`
会由 MySQL 官方镜像自动导入 `database/mysql/init` 下的初始化脚本，从而创建表结构和种子数据。

对于已经存在数据卷的开发者（之前运行过数据库），初始化脚本不会被重新执行。此时如果需要把仓库中新增的表结构或修复
应用到已有数据库，请使用手动 SQL 或通过数据库客户端执行需要的 SQL。例如：

```powershell
# 将单个 SQL 复制到容器并执行（替换容器名和密码）：
docker cp ./database/mysql/migrations/000-create-notification-if-missing.sql secondhand-mysql:/tmp/
docker exec -i secondhand-mysql sh -c "mysql -u root -proot123456 secondhand < /tmp/000-create-notification-if-missing.sql"
```

如果你希望使用更正式的迁移工具（且可回滚的迁移），建议后续切换到 Alembic 或其他迁移框架。

Notes about this migration layout
- The folder includes a tiny helper script `run-migrations.sh` that runs the
  SQL files in deterministic order and performs lightweight checks (for example
  it will create a notification table if missing and will only run the full
  copy/rename migration when a legacy table exists).
- The file `000-create-notification-if-missing.sql` is idempotent and ensures
  a fresh clone + `docker compose up -d mysql` will provide the `notification`
  table to the application. The heavier `2026-06-17-fix-notification.sql` will
  only run when a legacy `notification` table is present and thus is safe for
  both new and existing databases.
