# backend/app/api/my_task.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pymysql
import os

router = APIRouter(prefix="/my_task", tags=["favorite"])

def get_db_connection():
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "juZI0310") 
    database = os.getenv("DB_NAME", "secondhand")

    db_url = os.getenv("DATABASE_URL")
    if db_url and "root:" in db_url:
        try:
            part1 = db_url.split("://")[1] 
            user_pass = part1.split("@")[0] 
            password = user_pass.split(":")[1] 
        except Exception:
            pass 
            
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,  
        database=database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

class FavoriteRequest(BaseModel):
    user_id: int
    product_id: int

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

@router.get("/stats/dashboard")
# 3. 统计分析接口：使用最稳健的兼容逻辑
# 3. 统计分析接口：稳健优化版（完全兼容 MySQL ONLY_FULL_GROUP_BY）
@router.get("/stats/dashboard")
def get_dashboard_stats():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 统计 1：先查每个分类的商品上架数和金额
            cursor.execute("""
                SELECT category_name, COUNT(*) AS pub_count, SUM(price) AS total_revenue 
                FROM product GROUP BY category_name
            """)
            raw_pubs = cursor.fetchall()
            
            # 统计 2：单独查每个分类的被收藏总数（通过 Join 避开 Group By 复杂嵌套）
            cursor.execute("""
                SELECT p.category_name, COUNT(f.product_id) AS fav_count 
                FROM product p 
                JOIN favorite f ON p.product_id = f.product_id 
                GROUP BY p.category_name
            """)
            raw_favs = cursor.fetchall()
            
            # 将收藏数据存入字典，便于后续快速查找
            fav_map = {item['category_name']: item['fav_count'] for item in raw_favs}
            
            # 统计 3：在 Python 中完成合并逻辑 (发布数 + 收藏数)
            categories_list = []
            for item in raw_pubs:
                cat = item.get("category_name") or "未分类"
                pub = item.get("pub_count") or 0
                fav = fav_map.get(cat, 0)
                categories_list.append({
                    "category_name": cat,
                    "sales_count": pub + fav,  # 这里就是你想要的“热度”
                    "total_revenue": int(item.get("total_revenue") or 0)
                })
            
            # 按热度重新排序
            categories_list.sort(key=lambda x: x["sales_count"], reverse=True)

            # 统计 4：活跃用户排行 (保持你原本稳健的子查询逻辑)
            sql_active_users = """
                SELECT 
                    u.user_name, 
                    ((SELECT COUNT(*) FROM product WHERE seller_id = u.user_id) * 20 + 
                     (SELECT COUNT(*) FROM favorite WHERE user_id = u.user_id) * 10 +
                     (CASE WHEN DATEDIFF(NOW(), u.last_login_time) <= 7 THEN 50 ELSE 0 END)) AS action_count
                FROM user u
                ORDER BY action_count DESC
                LIMIT 5;
            """
            cursor.execute(sql_active_users)
            raw_users = cursor.fetchall()
            
            users_list = [{"user_name": u.get("user_name") or "神秘同学", "action_count": u.get("action_count") or 0} for u in raw_users]
            
            trends_list = [{"date": "06-04", "amount": 350}, {"date": "06-05", "amount": 890}, {"date": "06-06", "amount": 1500}]
            
        return {
            "status": "success",
            "categories": categories_list,  
            "users": users_list,            
            "trends": trends_list
        }
    except Exception as e:
        print("❌ [MySQL 统计错误]: ", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()
@router.get("/favorites/{user_id}")
def get_user_favorites(user_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM favorite WHERE user_id = %s ORDER BY create_time DESC"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

class NotificationRequest(BaseModel):
    receiver_id: int
    content: str

@router.post("/notifications/send")
def send_notification(req: NotificationRequest):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO notification (receiver_id, content) VALUES (%s, %s)"
            cursor.execute(sql, (req.receiver_id, req.content))
        connection.commit()
        return {"status": "success", "message": "通知发送成功"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()