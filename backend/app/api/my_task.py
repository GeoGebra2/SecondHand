# backend/app/api/my_task.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pymysql
import os

router = APIRouter(prefix="/my_task", tags=["我的大作业任务"])

# 自动读取你刚才在 .env 里配好的数据库连接信息
def get_db_connection():
    # 1. 尝试从你们框架本来就有的变量中分别读取（如果你的 .env 里分别配了这些字段）
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    
    # 【核心部分】：如果这里拿不到密码，就换成你自己本地 MySQL 的真实密码！
    # 请把下面的 "你的真实密码" 替换成你平时登录 MySQL 的真实密码
    password = os.getenv("DB_PASSWORD", "juZI0310") 
    database = os.getenv("DB_NAME", "secondhand")

    # 2. 如果你的密码实在配在 DATABASE_URL 里，我们做一个万无一失的提取
    db_url = os.getenv("DATABASE_URL")
    if db_url and "root:" in db_url:
        try:
            # 自动从 mysql+pymysql://root:xxx@127.0.0.1:3306/secondhand 提取密码
            part1 = db_url.split("://")[1] # root:xxx@127.0.0.1:3306/secondhand
            user_pass = part1.split("@")[0] # root:xxx
            password = user_pass.split(":")[1] # xxx
        except Exception:
            pass # 如果解析失败就用上面设置的“你的真实密码”
            
    # 3. 建立连接
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,  # 确保这里传入了正确的密码
        database=database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

class FavoriteRequest(BaseModel):
    user_id: int
    product_id: int

# 1. 收藏商品接口（已跑通）
@router.post("/favorite")
def add_favorite(req: FavoriteRequest):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO favorite (user_id, product_id) VALUES (%s, %s)"
            cursor.execute(sql, (req.user_id, req.product_id))
        connection.commit()
        return {"status": "success", "message": "收藏成功"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

# 2. 获取用户未读通知提醒接口
@router.get("/notifications/{user_id}")
def get_notifications(user_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM notification WHERE receiver_id = %s ORDER BY create_time DESC"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

# 3. 统计分析接口：热门类别、成交趋势、活跃用户
@router.get("/stats/dashboard")
def get_dashboard_stats():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 统计1：热门类别（由于其他组员可能还没建 product/order 表，我们用一段安全的模拟查询保证不报错）
            # 等以后全表导入了，可以改成真正的：SELECT * FROM v_category_stats
            mock_categories = [
                {"category_name": "教材书籍", "sales_count": 45, "total_revenue": 890},
                {"category_name": "数码电子", "sales_count": 28, "total_revenue": 5600},
                {"category_name": "生活用品", "sales_count": 19, "total_revenue": 340},
                {"category_name": "运动随行", "sales_count": 12, "total_revenue": 1200}
            ]
            
            # 统计2：活跃用户排行
            mock_users = [
                {"user_name": "张同学", "action_count": 24},
                {"user_name": "李同学", "action_count": 19},
                {"user_name": "王同学", "action_count": 15}
            ]
            
            # 统计3：成交金额趋势
            mock_trends = [
                {"date": "05-27", "amount": 450},
                {"date": "05-28", "amount": 890},
                {"date": "05-29", "amount": 1200},
                {"date": "05-30", "amount": 950},
                {"date": "05-31", "amount": 1600}
            ]
            
        return {
            "status": "success",
            "categories": mock_categories,
            "users": mock_users,
            "trends": mock_trends
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.get("/favorites/{user_id}")
def get_user_favorites(user_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 查出这个用户的所有收藏记录
            sql = "SELECT * FROM favorite WHERE user_id = %s ORDER BY create_time DESC"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()