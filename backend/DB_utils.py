import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv
import os
from datetime import datetime
from flask import jsonify
import bcrypt


class DatabaseManager:
    def __init__(self):
        load_dotenv()
        # 使用 Neon 資料庫連接
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL 未設置，請在 .env 文件中設置 DATABASE_URL")
        
        parsed = urlparse(database_url)
        
        self.conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # 移除前導 /
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        self.conn.autocommit = False

    def _ensure_connection(self):
        """確保資料庫連接是活躍的"""
        try:
            if self.conn.closed:
                # 連接已關閉，重新連接
                parsed = urlparse(os.getenv("DATABASE_URL"))
                self.conn = psycopg2.connect(
                    host=parsed.hostname,
                    port=parsed.port or 5432,
                    database=parsed.path[1:],
                    user=parsed.username,
                    password=parsed.password,
                    sslmode='require'
                )
                self.conn.autocommit = False
        except Exception:
            # 如果檢查連接狀態失敗，嘗試重新連接
            parsed = urlparse(os.getenv("DATABASE_URL"))
            self.conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                sslmode='require'
            )
            self.conn.autocommit = False

    def execute_query(self, query, params=None):
        try:
            self._ensure_connection()
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)

            # 檢查是否為 SELECT 查詢（包括 WITH ... SELECT）
            query_upper = query.strip().upper()
            is_select = (
                query_upper.startswith("SELECT")
                or query_upper.startswith("WITH")
                or "RETURNING" in query_upper
            )

            if is_select:
                result = cur.fetchall()
            else:
                self.conn.commit()
                result = cur.fetchall() if "RETURNING" in query_upper else True

            cur.close()
            return result

        except Exception as e:
            print(f"Query execution error: {e}")
            # 如果連接錯誤，嘗試重新連接
            try:
                self._ensure_connection()
            except:
                pass
            raise e

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()

    def check_account_exists(self, account):
        query = 'SELECT COUNT(*) FROM "USER" WHERE "Account" = %s'
        result = self.execute_query(query, (account,))
        return result[0][0] > 0

    def create_user(
        self,
        account,
        password,
        user_name,
        user_nickname,
        nationality,
        city,
        phone,
        email,
        sex,
        birthday,
        register_time,
    ):
        try:
            # 先獲取最大的 User_id
            max_id_query = 'SELECT COALESCE(MAX("User_id"), 0) FROM "USER"'
            result = self.execute_query(max_id_query)
            new_user_id = result[0][0] + 1

            # 插入用戶資料
            insert_query = """
                INSERT INTO "USER" (
                    "User_id", "Account", "Password", "User_name", "User_nickname", 
                    "Nationality", "City", "Phone", "Email", "Sex", "Birthday", "Register_time"
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING "User_id"
            """
            result = self.execute_query(
                insert_query,
                (
                    new_user_id,
                    account,
                    password,
                    user_name,
                    user_nickname,
                    nationality,
                    city,
                    phone,
                    email,
                    sex,
                    birthday,
                    register_time,
                ),
            )

            if result and len(result) > 0:
                self.conn.commit()
                return result[0][0]  # 返回新創建的 user_id

            self.conn.rollback()
            return None

        except Exception as e:
            self.conn.rollback()
            print(f"Error creating user: {e}")
            return None

    def set_user_role(self, user_id, role):
        try:
            role_query = """
                INSERT INTO "USER_ROLE" ("User_id", "Role")
                VALUES (%s, %s)
            """
            self.execute_query(role_query, (user_id, role))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error setting user role: {e}")
            return False

    def verify_login(self, account, password):
        query = """
                SELECT u."User_id", u."User_name", u."User_nickname", u."Email", r."Role"
                FROM "USER" u
                JOIN "USER_ROLE" r ON u."User_id" = r."User_id"
                WHERE u."Account" = %s AND u."Password" = %s
                """
        result = self.execute_query(query, (account, password))

        # 登入成功
        if result and len(result) > 0:
            row = result[0]
            return {
                "status": "success",
                "message": f"Welcome back, {row[1]}!",
                "user": {
                    "user_id": row[0],
                    "role": row[4],
                    "email": row[3],
                    "nickname": row[2],
                    "user_name": row[1],
                },
            }

        # 登入失敗
        return {"status": "error", "message": "Invalid account or password!"}

    # ==================== Google OAuth 相關方法 ====================
    
    def get_user_by_google_id(self, google_id):
        """透過 Google ID 獲取用戶"""
        try:
            query = """
                SELECT u."User_id", u."User_name", u."User_nickname", u."Email", 
                       r."Role", u."Avatar_url", u."Google_id"
                FROM "USER" u
                LEFT JOIN "USER_ROLE" r ON u."User_id" = r."User_id"
                WHERE u."Google_id" = %s
            """
            result = self.execute_query(query, (google_id,))
            if result and len(result) > 0:
                row = result[0]
                return {
                    'user_id': row[0],
                    'user_name': row[1],
                    'user_nickname': row[2],
                    'email': row[3],
                    'role': row[4] or 'User',
                    'avatar_url': row[5],
                    'google_id': row[6]
                }
            return None
        except Exception as e:
            print(f"Error getting user by Google ID: {e}")
            return None
    
    def get_user_by_email(self, email):
        """透過 Email 獲取用戶"""
        try:
            query = """
                SELECT u."User_id", u."User_name", u."User_nickname", u."Email", 
                       r."Role", u."Avatar_url", u."Google_id"
                FROM "USER" u
                LEFT JOIN "USER_ROLE" r ON u."User_id" = r."User_id"
                WHERE u."Email" = %s
            """
            result = self.execute_query(query, (email,))
            if result and len(result) > 0:
                row = result[0]
                return {
                    'user_id': row[0],
                    'user_name': row[1],
                    'user_nickname': row[2],
                    'email': row[3],
                    'role': row[4] or 'User',
                    'avatar_url': row[5],
                    'google_id': row[6]
                }
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def create_google_user(self, google_id, email, user_name, avatar_url, 
                          given_name=None, family_name=None, locale=None):
        """創建 Google 用戶"""
        try:
            # 獲取最大的 User_id
            max_id_query = 'SELECT COALESCE(MAX("User_id"), 0) FROM "USER"'
            result = self.execute_query(max_id_query)
            new_user_id = result[0][0] + 1
            
            # 生成唯一帳號（使用 google_ 前綴 + user_id）
            account = f"google_{new_user_id}"
            
            # 使用 Google 名稱作為用戶名和暱稱
            # 如果有 given_name 和 family_name，組合使用
            if given_name and family_name:
                full_name = f"{family_name}{given_name}"  # 中文習慣：姓在前
                user_nickname = given_name  # 暱稱使用名字
            elif user_name:
                full_name = user_name
                user_nickname = user_name
            else:
                full_name = f"User{new_user_id}"
                user_nickname = f"User{new_user_id}"
            
            # 插入用戶資料（Google 用戶不需要密碼和其他必填欄位）
            insert_query = """
                INSERT INTO "USER" (
                    "User_id", "Account", "User_name", "User_nickname", 
                    "Email", "Register_time", "Google_id", "Avatar_url"
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING "User_id"
            """
            from datetime import datetime
            result = self.execute_query(
                insert_query,
                (new_user_id, account, full_name, user_nickname, 
                 email, datetime.now(), google_id, avatar_url)
            )
            self.conn.commit()
            
            if result and len(result) > 0:
                return result[0][0]
            return None
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating Google user: {e}")
            return None
    
    def link_google_account(self, user_id, google_id, avatar_url=None):
        """將 Google 帳戶連結到現有用戶"""
        try:
            if avatar_url:
                query = """
                    UPDATE "USER" 
                    SET "Google_id" = %s, "Avatar_url" = %s
                    WHERE "User_id" = %s
                """
                self.execute_query(query, (google_id, avatar_url, user_id))
            else:
                query = """
                    UPDATE "USER" 
                    SET "Google_id" = %s
                    WHERE "User_id" = %s
                """
                self.execute_query(query, (google_id, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error linking Google account: {e}")
            return False
    
    def get_user_avatar(self, user_id):
        """獲取用戶頭像 URL"""
        try:
            query = 'SELECT "Avatar_url" FROM "USER" WHERE "User_id" = %s'
            result = self.execute_query(query, (user_id,))
            if result and len(result) > 0:
                return result[0][0]
            return None
        except Exception as e:
            print(f"Error getting user avatar: {e}")
            return None

    # ==================== 用戶詳細資料相關方法 ====================

    def update_user_basic_info(self, field, value, user_id):
        """更新用戶基本資料（USER 表）"""
        try:
            self._ensure_connection()
            
            # 允許更新的基本資料欄位
            allowed_fields = ['User_name', 'User_nickname', 'Phone', 'Birthday', 'Nationality', 'City', 'Sex']
            
            if field not in allowed_fields:
                print(f"Field {field} is not allowed to update in USER table")
                return False
            
            # 構建更新查詢
            update_query = f"""
                UPDATE "USER" 
                SET "{field}" = %s
                WHERE "User_id" = %s
            """
            self.execute_query(update_query, (value, user_id))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating user basic info: {str(e)}")
            self.conn.rollback()
            return False

    def update_user_avatar(self, user_id, avatar_data):
        """更新用戶頭像"""
        try:
            self._ensure_connection()
            
            update_query = """
                UPDATE "USER" 
                SET "Avatar_url" = %s
                WHERE "User_id" = %s
            """
            self.execute_query(update_query, (avatar_data, user_id))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating user avatar: {str(e)}")
            self.conn.rollback()
            return False

    def update_user_detail(self, field, value, user_id):
        try:
            cursor = self.conn.cursor()

            # 檢查用戶是否已有詳細資料記錄
            check_query = """
                SELECT "Self_introduction" FROM "USER_DETAIL" WHERE "User_id" = %s
            """
            cursor.execute(check_query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                # 如果有記錄,更新現有記錄
                update_query = f"""
                    UPDATE "USER_DETAIL" 
                    SET "{field}" = %s
                    WHERE "User_id" = %s AND "Self_introduction" = %s
                """
                cursor.execute(update_query, (value, user_id, result[0]))
            else:
                # 如果沒有記錄,插入新記錄
                # 注意:這裡需要同時插入 Self_introduction,因為它是主鍵的一部分
                insert_query = """
                    INSERT INTO "USER_DETAIL" ("User_id", "Self_introduction", "{}") 
                    VALUES (%s, '', %s)
                """.format(field)
                cursor.execute(insert_query, (user_id, value))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error updating user detail: {str(e)}")
            self.conn.rollback()
            return False

    def get_all_meetings(self):
        query = """
            SELECT 
                m."Meeting_id",
                m."Content",
                m."Event_date",
                m."Start_time",
                m."End_time",
                m."Event_city",
                m."Event_place",
                m."Status",
                m."Num_participant",
                m."Max_num_participant",
                u."User_name" as holder_name,
                string_agg(ml."Language", ', ') as languages
            FROM "MEETING" m
            JOIN "USER" u ON m."Holder_id" = u."User_id"
            LEFT JOIN "MEETING_LANGUAGE" ml ON m."Meeting_id" = ml."Meeting_id"
            WHERE m."Status" = 'Ongoing'
            GROUP BY 
                m."Meeting_id", m."Content", m."Event_date", m."Start_time",
                m."End_time", m."Event_city", m."Event_place", m."Status",
                m."Num_participant", m."Max_num_participant", u."User_name"
            ORDER BY m."Event_date" DESC, m."Start_time" DESC
        """
        return self.execute_query(query)

    def create_meeting(self, meeting_data):
        try:
            self._ensure_connection()
            cur = self.conn.cursor()
            # 先獲取最大的 Meeting_id
            get_max_id_query = """
                SELECT COALESCE(MAX("Meeting_id"), 0) + 1
                FROM "MEETING"
            """
            cur.execute(get_max_id_query)
            new_meeting_id = cur.fetchone()[0]

            # 處理密碼：如果有密碼則進行雜湊
            password = meeting_data.get("password")
            hashed_password = None
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # 插入聚會基本信息
            insert_meeting_query = """
                INSERT INTO "MEETING" (
                    "Meeting_id",
                    "Holder_id",
                    "Content",
                    "Event_date",
                    "Start_time",
                    "End_time",
                    "Event_city",
                    "Event_place",
                    "Event_address",
                    "Latitude",
                    "Longitude",
                    "Status",
                    "Num_participant",
                    "Max_num_participant",
                    "Password"
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Ongoing', 1, %s, %s
                ) RETURNING "Meeting_id"
            """

            cur.execute(
                insert_meeting_query,
                (
                    new_meeting_id,
                    meeting_data["holder_id"],
                    meeting_data["content"],
                    meeting_data["date"],
                    meeting_data["start_time"],
                    meeting_data["end_time"],
                    meeting_data["city"],
                    meeting_data["place"],
                    meeting_data.get("address"),
                    meeting_data.get("latitude"),
                    meeting_data.get("longitude"),
                    meeting_data["max_participants"],
                    hashed_password,
                ),
            )

            meeting_id = cur.fetchone()[0]

            # 插入聚會語言
            for language in meeting_data["languages"]:
                insert_language_query = """
                    INSERT INTO "MEETING_LANGUAGE" ("Meeting_id", "Language")
                    VALUES (%s, %s)
                """
                cur.execute(insert_language_query, (meeting_id, language))

            # 創建者自動加入聚會
            insert_participation_query = """
                INSERT INTO "PARTICIPATION" ("Meeting_id", "User_id", "Join_time")
                VALUES (%s, %s, NOW())
            """
            cur.execute(
                insert_participation_query, (meeting_id, meeting_data["holder_id"])
            )

            self.conn.commit()
            cur.close()
            return True

        except Exception as e:
            print(f"Error creating meeting: {str(e)}")
            try:
                self.conn.rollback()
            except:
                pass
            try:
                cur.close()
            except:
                pass
            return False

    def check_meeting_availability(self, meeting_id):
        query = """
                SELECT "Meeting_id" 
                FROM "MEETING" 
                WHERE "Meeting_id" = %s 
                AND "Status" = 'Ongoing'
                AND "Num_participant" < "Max_num_participant"
                """
        result = self.execute_query(query, (meeting_id,))
        return result and len(result) > 0

    def is_user_in_meeting(self, user_id, meeting_id):
        query = """
                SELECT 1
                FROM "PARTICIPATION"
                WHERE "User_id" = %s AND "Meeting_id" = %s
                """
        result = self.execute_query(query, (user_id, meeting_id))
        return bool(result)

    def meeting_has_password(self, meeting_id):
        """檢查聚會是否有設密碼"""
        query = """
            SELECT "Password" IS NOT NULL as has_password
            FROM "MEETING"
            WHERE "Meeting_id" = %s
        """
        result = self.execute_query(query, (meeting_id,))
        return result[0][0] if result else False

    def verify_meeting_password(self, meeting_id, password):
        """驗證聚會密碼是否正確，若聚會無密碼則直接返回 True"""
        query = """
            SELECT "Password"
            FROM "MEETING"
            WHERE "Meeting_id" = %s
        """
        result = self.execute_query(query, (meeting_id,))
        if not result:
            return False
        
        stored_password = result[0][0]
        # 如果沒有設密碼，直接通過
        if stored_password is None:
            return True
        
        # 如果有密碼但用戶沒提供密碼
        if not password:
            return False
        
        # 驗證密碼
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    def get_meeting(self, meeting_id):
        """獲取單一聚會的基本資訊"""
        query = """
            SELECT 
                "Meeting_id",
                "Holder_id",
                "Content",
                "Event_date",
                "Start_time",
                "End_time",
                "Event_city",
                "Event_place",
                "Status",
                "Num_participant",
                "Max_num_participant"
            FROM "MEETING"
            WHERE "Meeting_id" = %s
        """
        result = self.execute_query(query, (meeting_id,))
        if result:
            row = result[0]
            return {
                "meeting_id": row[0],
                "holder_id": row[1],
                "content": row[2],
                "date": row[3],
                "start_time": row[4],
                "end_time": row[5],
                "city": row[6],
                "place": row[7],
                "status": row[8],
                "num_participant": row[9],
                "max_participants": row[10]
            }
        return None

    def join_meeting(self, user_id, meeting_id):
        try:
            self._ensure_connection()
            # 檢查聚會是否已滿
            check_query = """
                SELECT "Num_participant", "Max_num_participant"
                FROM "MEETING"
                WHERE "Meeting_id" = %s
                FOR UPDATE
            """
            result = self.execute_query(check_query, (meeting_id,))
            if not result:
                self.conn.rollback()
                return False

            current_participants, max_participants = result[0]
            if current_participants >= max_participants:
                self.conn.rollback()
                return False

            # 插入參與記錄
            insert_query = """
                INSERT INTO "PARTICIPATION" ("User_id", "Meeting_id", "Join_time")
                VALUES (%s, %s, NOW())
            """
            self.execute_query(insert_query, (user_id, meeting_id))

            # 更新聚會人數
            update_query = """
                UPDATE "MEETING" 
                SET "Num_participant" = "Num_participant" + 1
                WHERE "Meeting_id" = %s
            """
            self.execute_query(update_query, (meeting_id,))

            # 提交事務
            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error joining meeting: {e}")
            self.conn.rollback()
            return False

    def get_user_meetings(self, user_id):
        try:
            query = """
                SELECT 
                    m."Meeting_id",
                    m."Content",
                    m."Event_date",
                    m."Start_time",
                    m."End_time",
                    m."Event_city",
                    m."Event_place",
                    m."Num_participant",
                    m."Max_num_participant",
                    m."Status",
                    m."Holder_id",
                    u."User_nickname" as holder_name,
                    m."Event_address",
                    m."Latitude",
                    m."Longitude"
                FROM "MEETING" m
                JOIN "USER" u ON m."Holder_id" = u."User_id"
                WHERE m."Meeting_id" IN (
                    SELECT "Meeting_id" 
                    FROM "PARTICIPATION" 
                    WHERE "User_id" = %s
                )
                ORDER BY m."Event_date", m."Start_time"
            """
            result = self.execute_query(query, (user_id,))

            meetings = {"ongoing": [], "finished": [], "cancelled": []}

            for row in result:
                meeting = {
                    "meeting_id": row[0],
                    "content": row[1],
                    "date": row[2],
                    "start_time": row[3].strftime("%H:%M"),
                    "end_time": row[4].strftime("%H:%M"),
                    "city": row[5],
                    "place": row[6],
                    "num_participant": row[7],
                    "max_participants": row[8],
                    "holder_id": row[10],
                    "holder_name": row[11],
                    "address": row[12],
                    "latitude": float(row[13]) if row[13] else None,
                    "longitude": float(row[14]) if row[14] else None,
                }

                if row[9] == "Ongoing":
                    meetings["ongoing"].append(meeting)
                elif row[9] == "Finished":
                    meetings["finished"].append(meeting)
                else:
                    meetings["cancelled"].append(meeting)

            return meetings

        except Exception as e:
            print(f"Error getting user meetings: {str(e)}")
            return {"ongoing": [], "finished": [], "cancelled": []}

    def leave_meeting(self, user_id, meeting_id):
        try:
            self._ensure_connection()
            # 檢查用戶是否在聚會中
            check_query = """
                SELECT 1 FROM "PARTICIPATION"
                WHERE "User_id" = %s AND "Meeting_id" = %s
            """
            result = self.execute_query(check_query, (user_id, meeting_id))
            if not result:
                return False

            # 刪除參與記錄
            delete_query = """
                DELETE FROM "PARTICIPATION"
                WHERE "User_id" = %s AND "Meeting_id" = %s
            """
            self.execute_query(delete_query, (user_id, meeting_id))

            # 更新聚會人數
            update_query = """
                UPDATE "MEETING" 
                SET "Num_participant" = "Num_participant" - 1
                WHERE "Meeting_id" = %s
            """
            self.execute_query(update_query, (meeting_id,))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error leaving meeting: {e}")
            self.conn.rollback()
            return False

    def cancel_meeting(self, meeting_id):
        try:
            self._ensure_connection()
            query = """
                UPDATE "MEETING" 
                SET "Status" = 'Canceled'
                WHERE "Meeting_id" = %s
                AND "Status" = 'Ongoing'
            """
            self.execute_query(query, (meeting_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error canceling meeting: {e}")
            self.conn.rollback()
            return False

    def finish_meeting(self, meeting_id):
        try:
            self._ensure_connection()
            # 檢查聚會是否存在且狀態為進行中
            check_query = """
                SELECT 1 FROM "MEETING"
                WHERE "Meeting_id" = %s
                AND "Status" = 'Ongoing'
            """
            result = self.execute_query(check_query, (meeting_id,))
            if not result:
                return False

            # 更新聚會狀態
            update_query = """
                UPDATE "MEETING" 
                SET "Status" = 'Finished'
                WHERE "Meeting_id" = %s
                AND "Status" = 'Ongoing'
            """
            self.execute_query(update_query, (meeting_id,))
            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error finishing meeting: {e}")
            self.conn.rollback()
            return False

    def get_all_meetings_admin(self):
        try:
            query = """
                SELECT 
                    m."Meeting_id",
                    m."Content",
                    m."Event_date",
                    m."Event_place",
                    m."Status",
                    m."Max_num_participant",
                    m."Holder_id",
                    u."User_name" as holder_name,
                    m."Num_participant"
                FROM "MEETING" m
                LEFT JOIN "USER" u ON m."Holder_id" = u."User_id"
                ORDER BY 
                    CASE m."Status"
                        WHEN 'Ongoing' THEN 1
                        WHEN 'Finished' THEN 2
                        WHEN 'Cancelled' THEN 3
                    END,
                    m."Event_date" DESC
            """

            result = self.execute_query(query)
            if not result:
                return []

            meetings = []
            for row in result:
                # 獲取每個聚會的參與者
                participants_query = """
                    SELECT u."User_id", u."User_name", u."User_nickname"
                    FROM "USER" u
                    JOIN "PARTICIPATION" p ON u."User_id" = p."User_id"
                    WHERE p."Meeting_id" = %s
                """
                participants = self.execute_query(participants_query, (row[0],))

                meetings.append(
                    {
                        "meeting_id": row[0],
                        "content": row[1],
                        "event_date": row[2].strftime("%Y-%m-%d"),
                        "event_place": row[3],
                        "status": row[4],
                        "max_participant": row[5],
                        "holder_id": row[6],
                        "holder_name": row[7],
                        "num_participant": row[8],
                        "participants": (
                            [
                                {
                                    "user_id": p[0],
                                    "user_name": p[1],
                                    "user_nickname": p[2],
                                }
                                for p in participants
                            ]
                            if participants
                            else []
                        ),
                    }
                )

            return meetings

        except Exception as e:
            print(f"Error in get_all_meetings_admin: {e}")
            return None

    def admin_cancel_meeting(self, meeting_id):
        try:
            self._ensure_connection()
            query = """
                    UPDATE "MEETING" 
                    SET "Status" = 'Canceled'
                    WHERE "Meeting_id" = %s
                    AND "Status" = 'Ongoing'
                    """
            self.execute_query(query, (meeting_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error in admin cancel meeting: {e}")
            self.conn.rollback()
            return False

    def admin_finish_meeting(self, meeting_id):
        try:
            self._ensure_connection()
            query = """
                    UPDATE "MEETING" 
                    SET "Status" = 'Finished'
                    WHERE "Meeting_id" = %s
                    AND "Status" = 'Ongoing'
                    """
            self.execute_query(query, (meeting_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error in admin finish meeting: {e}")
            self.conn.rollback()
            return False

    def add_sns_detail(self, user_id, sns_type, sns_id):
        try:
            self._ensure_connection()
            # 先刪除舊的記錄（如果存在）
            delete_query = """
                DELETE FROM "SNS_DETAIL" 
                WHERE "User_id" = %s AND "Sns_type" = %s
            """
            self.execute_query(delete_query, (user_id, sns_type))
            
            # 插入新記錄
            insert_query = """
                INSERT INTO "SNS_DETAIL" ("User_id", "Sns_type", "Sns_id")
                VALUES (%s, %s, %s)
            """
            self.execute_query(insert_query, (user_id, sns_type, sns_id))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error in add_sns_detail: {str(e)}")
            self.conn.rollback()
            return False

    def get_sns_details(self, user_id):
        try:
            sql = """
                SELECT "Sns_type", "Sns_id" 
                FROM "SNS_DETAIL" 
                WHERE "User_id" = %s
            """
            result = self.execute_query(sql, (user_id,))
            return [{"sns_type": row[0], "sns_id": row[1]} for row in result]
        except Exception as e:
            print(f"Error in get_sns_details: {str(e)}")
            return []

    def remove_sns_detail(self, user_id, sns_type):
        try:
            self._ensure_connection()
            sql = """
                DELETE FROM "SNS_DETAIL" 
                WHERE "User_id" = %s AND "Sns_type" = %s
            """
            self.execute_query(sql, (user_id, sns_type))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error in remove_sns_detail: {str(e)}")
            self.conn.rollback()
            return False

    def get_meeting_chat_history(self, meeting_id):
        try:
            query = """
            SELECT 
                cr."Meeting_id",
                cr."Sender_id",
                u."User_name" as sender_name,
                cr."Content",
                cr."Sending_time"
            FROM "CHATTING_ROOM" cr
            JOIN "USER" u ON cr."Sender_id" = u."User_id"
            WHERE cr."Meeting_id" = %s
            ORDER BY cr."Sending_time" ASC
            """
            result = self.execute_query(query, (meeting_id,))

            messages = []
            for row in result:
                messages.append(
                    {
                        "meeting_id": row[0],
                        "sender_id": row[1],
                        "sender_name": row[2],
                        "content": row[3],
                        "timestamp": row[4].isoformat() if row[4] else None,
                    }
                )
            return messages

        except Exception as e:
            print(f"Error getting meeting chat history: {e}")
            return None

    def save_meeting_message(self, meeting_id, sender_id, content):
        try:
            self._ensure_connection()
            query = """
                INSERT INTO "CHATTING_ROOM" ("Meeting_id", "Sender_id", "Content", "Sending_time")
                VALUES (%s, %s, %s, NOW())
                RETURNING "Meeting_id"
            """
            result = self.execute_query(query, (meeting_id, sender_id, content))
            self.conn.commit()

            if result:
                return result[0][0]
            return None

        except Exception as e:
            print(f"Error saving meeting message: {e}")
            self.conn.rollback()
            return None

    def get_available_users(self, current_user_id):
        query = """
            SELECT u."User_id", u."User_nickname" as nickname
            FROM "USER" u
            LEFT JOIN "USER_ROLE" ur ON u."User_id" = ur."User_id" AND ur."Role" = 'Admin'
            WHERE u."User_id" != %s AND ur."User_id" IS NULL
            ORDER BY u."User_nickname"
        """
        result = self.execute_query(query, (current_user_id,))
        if not result:
            return []

        users = []
        for row in result:
            users.append({"user_id": row[0], "nickname": row[1]})
        return users

    def get_available_meetings(self, user_id):
        query = """
            SELECT 
                m."Meeting_id",
                m."Content",
                m."Event_city",
                m."Event_place",
                m."Event_date",
                m."Start_time",
                m."End_time",
                m."Max_num_participant",
                m."Num_participant",
                m."Holder_id",
                u."User_nickname" as holder_name,
                (
                    SELECT string_agg(ml."Language", ',')
                    FROM "MEETING_LANGUAGE" ml
                    WHERE ml."Meeting_id" = m."Meeting_id"
                ) as languages,
                (m."Password" IS NOT NULL) as has_password,
                m."Event_address",
                m."Latitude",
                m."Longitude"
            FROM "MEETING" m
            JOIN "USER" u ON m."Holder_id" = u."User_id"
            WHERE m."Status" = 'Ongoing'
            AND m."Meeting_id" NOT IN (
                SELECT "Meeting_id" 
                FROM "PARTICIPATION" 
                WHERE "User_id" = %s
            )
            AND m."Holder_id" != %s
            AND m."Num_participant" < m."Max_num_participant"
            ORDER BY m."Event_date", m."Start_time"
        """

        result = self.execute_query(query, (user_id, user_id))
        if not result:
            return []

        meetings = []
        for row in result:
            languages = row[11].split(",") if row[11] else []
            meetings.append(
                {
                    "id": row[0],
                    "type": row[1],
                    "city": row[2],
                    "place": row[3],
                    "date": row[4].strftime("%Y-%m-%d"),
                    "start_time": str(row[5]),
                    "end_time": str(row[6]),
                    "max_members": row[7],
                    "current_members": row[8],
                    "holder_id": row[9],
                    "holder_name": row[10],
                    "languages": languages,
                    "title": f"{row[2]} {row[3]} 的{row[1]}活動",
                    "has_password": row[12],
                    "address": row[13],
                    "latitude": float(row[14]) if row[14] else None,
                    "longitude": float(row[15]) if row[15] else None,
                }
            )
        return meetings

    def get_user_basic_info(self, user_id):
        query = """
            SELECT "Account", "User_name", "User_nickname", "Email", "Phone", "Birthday", 
                   "Nationality", "City", "Sex", "Avatar_url"
            FROM "USER"
            WHERE "User_id" = %s
        """
        result = self.execute_query(query, (user_id,))
        if result:
            row = result[0]
            # 安全處理可能為 NULL 的欄位
            birthday = None
            if row[5]:
                try:
                    birthday = row[5].strftime("%Y-%m-%d") if hasattr(row[5], 'strftime') else str(row[5])
                except:
                    birthday = str(row[5]) if row[5] else None
            
            return {
                "account": row[0] or "",
                "user_name": row[1] or "",
                "user_nickname": row[2] or "",
                "email": row[3] or "",
                "phone": row[4] or "",
                "birthday": birthday or "",
                "nationality": row[6] or "",
                "city": row[7] or "",
                "sex": row[8] or "",
                "avatar_url": row[9] or ""
            }
        return None

    def get_user_profile_info(self, user_id):
        query = """
            SELECT "Star_sign", "Mbti", "Blood_type", "Religion", "University",
                "Married", "Sns", "Self_introduction", "Interest", "Find_meeting_type"
            FROM "USER_DETAIL"
            WHERE "User_id" = %s
        """
        result = self.execute_query(query, (user_id,))
        if result:
            return {
                "Star_sign": result[0][0],
                "Mbti": result[0][1],
                "Blood_type": result[0][2],
                "Religion": result[0][3],
                "University": result[0][4],
                "Married": result[0][5],
                "Sns": result[0][6],
                "Self_introduction": result[0][7],
                "Interest": result[0][8],
                "Find_meeting_type": result[0][9],
            }
        return {}

    def get_meeting_participants(self, meeting_id):
        """獲取聚會的所有參與者"""
        try:
            query = """
                SELECT 
                    u."User_id", 
                    u."User_name", 
                    u."User_nickname",
                    u."Avatar_url",
                    CASE WHEN m."Holder_id" = u."User_id" THEN true ELSE false END as is_host
                FROM "USER" u
                JOIN "PARTICIPATION" p ON u."User_id" = p."User_id"
                JOIN "MEETING" m ON p."Meeting_id" = m."Meeting_id"
                WHERE p."Meeting_id" = %s
                ORDER BY is_host DESC, p."Join_time" ASC
            """
            result = self.execute_query(query, (meeting_id,))
            
            participants = []
            for row in result:
                participants.append({
                    'user_id': row[0],
                    'user_name': row[1],
                    'user_nickname': row[2],
                    'avatar_url': row[3],
                    'is_host': row[4]
                })
            return participants
        except Exception as e:
            print(f"Error getting meeting participants: {e}")
            return []

    def get_user_public_profile(self, user_id):
        """獲取用戶的公開個人資料（供其他用戶查看）"""
        try:
            # 獲取基本資料（包含生日）
            basic_query = """
                SELECT "User_name", "User_nickname", "Sex", "Nationality", "City", "Avatar_url", "Birthday"
                FROM "USER"
                WHERE "User_id" = %s
            """
            basic_result = self.execute_query(basic_query, (user_id,))
            
            if not basic_result:
                return None
            
            row = basic_result[0]
            # 處理生日格式
            birthday_str = ''
            if row[6]:
                try:
                    birthday_str = row[6].strftime('%Y-%m-%d') if hasattr(row[6], 'strftime') else str(row[6])
                except:
                    birthday_str = ''
            
            profile = {
                'user_name': row[0] or '',
                'user_nickname': row[1] or '',
                'sex': row[2] or '',
                'nationality': row[3] or '',
                'city': row[4] or '',
                'avatar_url': row[5] or '',
                'birthday': birthday_str
            }
            
            # 獲取詳細資料（所有欄位）
            detail_query = """
                SELECT "Star_sign", "Mbti", "Blood_type", "University", 
                       "Self_introduction", "Interest", "Religion", "Married", 
                       "Sns", "Find_meeting_type"
                FROM "USER_DETAIL"
                WHERE "User_id" = %s
            """
            detail_result = self.execute_query(detail_query, (user_id,))
            
            if detail_result:
                detail_row = detail_result[0]
                sns_willing = detail_row[8] or ''
                profile.update({
                    'star_sign': detail_row[0] or '',
                    'mbti': detail_row[1] or '',
                    'blood_type': detail_row[2] or '',
                    'university': detail_row[3] or '',
                    'self_introduction': detail_row[4] or '',
                    'interest': detail_row[5] or '',
                    'religion': detail_row[6] or '',
                    'married': detail_row[7] or '',
                    'sns': sns_willing,
                    'find_meeting_type': detail_row[9] or ''
                })
                
                # 如果願意交換社群 (sns = 'YES')，則獲取社群帳號
                if sns_willing == 'YES':
                    sns_accounts = self.get_sns_details(user_id)
                    profile['sns_accounts'] = sns_accounts
                else:
                    profile['sns_accounts'] = []
            
            return profile
        except Exception as e:
            print(f"Error getting user public profile: {e}")
            return None

    def remove_user_from_meeting(self, meeting_id, user_id):
        try:
            self._ensure_connection()
            # 先檢查用戶是否在聚會中
            check_query = """
                SELECT 1 FROM "PARTICIPATION" 
                WHERE "Meeting_id" = %s AND "User_id" = %s
            """
            result = self.execute_query(check_query, (meeting_id, user_id))

            if not result:
                return False

            # 從聚會中移除用戶
            delete_query = """
                DELETE FROM "PARTICIPATION" 
                WHERE "Meeting_id" = %s AND "User_id" = %s
            """
            self.execute_query(delete_query, (meeting_id, user_id))

            # 更新聚會參與人數
            update_query = """
                UPDATE "MEETING" 
                SET "Num_participant" = "Num_participant" - 1
                WHERE "Meeting_id" = %s
            """
            self.execute_query(update_query, (meeting_id,))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error in remove_user_from_meeting: {str(e)}")
            self.conn.rollback()
            return False

    def get_all_users(self, page=1, limit=100, search_id=None):
        try:
            if search_id:
                count_query = """
                    SELECT COUNT(*) 
                    FROM "USER" u
                    WHERE u."User_id"::text LIKE %s
                """
                count_result = self.execute_query(count_query, (f"%{search_id}%",))
                total_count = count_result[0][0] if count_result else 0

                query = """
                    SELECT u."User_id", u."Account", u."User_name", u."User_nickname", 
                           u."Email", u."Phone", u."Birthday", u."Sex", u."City"
                    FROM "USER" u
                    WHERE u."User_id"::text LIKE %s
                    ORDER BY u."User_id"
                    LIMIT %s OFFSET %s
                """
                params = (f"%{search_id}%", limit, (page - 1) * limit)
            else:
                count_query = 'SELECT COUNT(*) FROM "USER"'
                count_result = self.execute_query(count_query)
                total_count = count_result[0][0] if count_result else 0

                query = """
                    SELECT u."User_id", u."Account", u."User_name", u."User_nickname", 
                           u."Email", u."Phone", u."Birthday", u."Sex", u."City"
                    FROM "USER" u
                    ORDER BY u."User_id"
                    LIMIT %s OFFSET %s
                """
                params = (limit, (page - 1) * limit)

            result = self.execute_query(query, params)
            users = []
            if result:
                for row in result:
                    users.append(
                        {
                            "user_id": row[0],
                            "account": row[1],
                            "user_name": row[2],
                            "user_nickname": row[3],
                            "email": row[4],
                            "phone": row[5],
                            "birthday": row[6].strftime("%Y-%m-%d") if row[6] else None,
                            "sex": row[7],
                            "city": row[8],
                        }
                    )
            return users, total_count

        except Exception as e:
            print(f"Error in get_all_users: {str(e)}")
            return [], 0

    def get_user_chat_partners(self, user_id):
        try:
            query = """
            SELECT DISTINCT 
                u."User_id",
                u."User_name",
                u."User_nickname",
                COUNT(pm."Sender_id") as message_count
            FROM "USER" u
            INNER JOIN "PRIVATE_MESSAGE" pm 
            ON (u."User_id" = pm."Sender_id" OR u."User_id" = pm."Receiver_id")
            WHERE (pm."Sender_id" = %s OR pm."Receiver_id" = %s)
            AND u."User_id" != %s
            GROUP BY u."User_id", u."User_name", u."User_nickname"
            ORDER BY message_count DESC
            """

            result = self.execute_query(query, (user_id, user_id, user_id))
            if not result:
                return []

            partners = []
            for row in result:
                partners.append(
                    {
                        "user_id": row[0],
                        "user_name": row[1],
                        "nickname": row[2],
                        "message_count": row[3],
                    }
                )
            return partners

        except Exception as e:
            print(f"Error getting chat partners: {e}")
            return None

    def get_user_chat_history(self, user1_id, user2_id, limit=20):
        try:
            query = """
            SELECT 
                pm."Sender_id",
                pm."Receiver_id",
                pm."Sending_time",
                pm."Content",
                u."User_name" as sender_name
            FROM "PRIVATE_MESSAGE" pm
            INNER JOIN "USER" u ON pm."Sender_id" = u."User_id"
            WHERE (pm."Sender_id" = %s AND pm."Receiver_id" = %s)
            OR (pm."Sender_id" = %s AND pm."Receiver_id" = %s)
            ORDER BY pm."Sending_time" DESC
            LIMIT %s
            """

            result = self.execute_query(
                query, (user1_id, user2_id, user2_id, user1_id, limit)
            )
            if not result:
                return []

            messages = []
            for row in result:
                messages.append(
                    {
                        "sender_id": row[0],
                        "receiver_id": row[1],
                        "timestamp": row[2].strftime("%Y-%m-%d %H:%M:%S"),
                        "content": row[3],
                        "sender_name": row[4],
                    }
                )
            return messages

        except Exception as e:
            print(f"Error getting chat history: {e}")
            return None

    def get_meeting_info(self, meeting_id):
        try:
            query = """
            SELECT 
                "Meeting_id",
                "Content",
                "Event_date",
                "Event_place",
                "Num_participant",
                "Max_num_participant",
                "Status"
            FROM "MEETING"
            WHERE "Meeting_id" = %s
            """

            result = self.execute_query(query, (meeting_id,))
            if not result:
                return None

            row = result[0]
            return {
                "meeting_id": row[0],
                "content": row[1],
                "event_date": row[2],
                "event_place": row[3],
                "num_participant": row[4],
                "max_participant": row[5],
                "status": row[6],
            }

        except Exception as e:
            print(f"Error getting meeting info: {e}")
            return None

    def get_meeting_chat_history(self, meeting_id):
        try:
            query = """
            SELECT 
                mm."Meeting_id",
                mm."Sender_id",
                COALESCE(u."User_nickname", u."User_name") as display_name,
                u."User_name",
                u."User_nickname",
                mm."Content",
                mm."Sending_time"
            FROM "CHATTING_ROOM" mm
            INNER JOIN "USER" u ON mm."Sender_id" = u."User_id"
            WHERE mm."Meeting_id" = %s
            ORDER BY mm."Sending_time" ASC
            """

            result = self.execute_query(query, (meeting_id,))
            if not result:
                return []
            messages = []
            for row in result:
                messages.append(
                    {
                        "meeting_id": row[0],
                        "sender_id": row[1],
                        "sender_name": row[2],  # 顯示名稱（優先暱稱）
                        "sender_real_name": row[3],  # 真實姓名
                        "sender_nickname": row[4],  # 暱稱
                        "content": row[5],
                        "timestamp": row[6].strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
            return messages

        except Exception as e:
            print(f"Error getting meeting chat history: {e}")
            return None

    def get_user_chat_list(self, user_id):
        """獲取用戶的聊天列表"""
        try:
            self._ensure_connection()
            cursor = self.conn.cursor()
            query = """
                WITH chat_partners AS (
                    SELECT DISTINCT 
                        CASE 
                            WHEN pm."Sender_id" = %s THEN pm."Receiver_id"
                            ELSE pm."Sender_id" 
                        END as partner_id
                    FROM "PRIVATE_MESSAGE" pm
                    WHERE pm."Sender_id" = %s OR pm."Receiver_id" = %s
                )
                SELECT 
                    cp.partner_id,
                    u."User_name",
                    u."Avatar_url",
                    (
                        SELECT "Sending_time" 
                        FROM "PRIVATE_MESSAGE" pm2
                        WHERE (
                            (pm2."Sender_id" = %s AND pm2."Receiver_id" = cp.partner_id)
                            OR 
                            (pm2."Sender_id" = cp.partner_id AND pm2."Receiver_id" = %s)
                        )
                        ORDER BY "Sending_time" DESC
                        LIMIT 1
                    ) as last_message_time
                FROM chat_partners cp
                JOIN "USER" u ON u."User_id" = cp.partner_id
                ORDER BY last_message_time DESC NULLS LAST
            """
            cursor.execute(query, (user_id, user_id, user_id, user_id, user_id))
            result = cursor.fetchall()
            cursor.close()

            if not result:
                return []

            chats = []
            for row in result:
                chats.append(
                    {
                        "other_user_id": row[0],
                        "other_user_name": row[1],
                        "avatar_url": row[2],
                        "last_message_time": (
                            row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else None
                        ),
                    }
                )
            return chats

        except Exception as e:
            print(f"Error getting user chat list: {str(e)}")
            if cursor:
                cursor.close()
            return None

    def get_private_chat_history(self, user1_id, user2_id):
        """獲取兩個用戶之間的聊天記錄"""
        try:
            query = """
                SELECT 
                    pm."Sender_id",
                    u."User_name" as sender_name,
                    pm."Content",
                    pm."Sending_time"
                FROM "PRIVATE_MESSAGE" pm
                JOIN "USER" u ON pm."Sender_id" = u."User_id"
                WHERE (
                    (pm."Sender_id" = %s AND pm."Receiver_id" = %s)
                    OR 
                    (pm."Sender_id" = %s AND pm."Receiver_id" = %s)
                )
                ORDER BY pm."Sending_time" ASC
            """
            result = self.execute_query(query, (user1_id, user2_id, user2_id, user1_id))

            if not result:
                return []

            messages = []
            for row in result:
                messages.append(
                    {
                        "sender_id": row[0],
                        "sender_name": row[1],
                        "content": row[2],
                        "timestamp": row[3].strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
            return messages

        except Exception as e:
            print(f"Error getting private chat history: {str(e)}")
            return None

    def save_private_message(self, sender_id, receiver_id, content):
        """保存私人訊息"""
        try:
            self._ensure_connection()
            query = """
                INSERT INTO "PRIVATE_MESSAGE" ("Sender_id", "Receiver_id", "Content", "Sending_time")
                VALUES (%s, %s, %s, NOW())
                RETURNING "Sender_id"
            """
            result = self.execute_query(query, (sender_id, receiver_id, content))

            if result:
                self.conn.commit()
                return result[0][0]  # 返回新插入的 sender_id
            return None

        except Exception as e:
            print(f"Error saving private message: {str(e)}")
            self.conn.rollback()
            return None

    def get_available_chat_users(self, current_user_id):
        """獲取可聊天的用戶列表（除了管理員和自己）"""
        try:
            query = """
                SELECT 
                    u."User_id",
                    u."User_name"
                FROM "USER" u
                LEFT JOIN "USER_ROLE" ur ON u."User_id" = ur."User_id"
                WHERE u."User_id" != %s 
                AND (ur."Role" != 'Admin' OR ur."Role" IS NULL)
                ORDER BY u."User_name"
            """
            result = self.execute_query(query, (current_user_id,))

            if not result:
                return []

            users = []
            for row in result:
                users.append({"user_id": row[0], "user_name": row[1]})
            return users

        except Exception as e:
            print(f"Error getting available chat users: {str(e)}")
            return None

    def search_chat_users(self, query, current_user, limit=10):
        try:
            sql = """
                SELECT "User_id", "User_name", "User_nickname"
                FROM "USER"
                WHERE ("User_id"::text LIKE %s 
                      OR "User_nickname" LIKE %s 
                      OR "User_name" LIKE %s)
                AND "User_id" != %s
                LIMIT %s
            """
            search_pattern = f"%{query}%"
            params = (
                search_pattern,
                search_pattern,
                search_pattern,
                current_user,
                limit,
            )

            result = self.execute_query(sql, params)

            return [
                {"user_id": row[0], "user_name": row[1], "user_nickname": row[2]}
                for row in result
            ]

        except Exception as e:
            print(f"Error in search_chat_users: {str(e)}")
            return []

    # ==================== 好友功能 ====================

    def send_friend_request(self, user_id, friend_id):
        """發送好友請求"""
        try:
            self._ensure_connection()
            
            # 確保參數是整數
            user_id = int(user_id)
            friend_id = int(friend_id)
            
            # 檢查是否已經存在好友關係
            check_query = """
                SELECT "Status" FROM "FRIENDSHIP"
                WHERE ("User_id" = %s AND "Friend_id" = %s)
                OR ("User_id" = %s AND "Friend_id" = %s)
            """
            result = self.execute_query(check_query, (user_id, friend_id, friend_id, user_id))
            
            if result and len(result) > 0:
                status = result[0][0]
                if status == 'accepted':
                    return {'success': False, 'message': '你們已經是好友了'}
                elif status == 'pending':
                    return {'success': False, 'message': '已有待處理的好友請求'}
            
            # 發送好友請求
            insert_query = """
                INSERT INTO "FRIENDSHIP" ("User_id", "Friend_id", "Status", "Created_at", "Updated_at")
                VALUES (%s, %s, 'pending', NOW(), NOW())
                ON CONFLICT ("User_id", "Friend_id") 
                DO UPDATE SET "Status" = 'pending', "Updated_at" = NOW()
            """
            self.execute_query(insert_query, (user_id, friend_id))
            self.conn.commit()
            return {'success': True, 'message': '好友請求已發送'}
            
        except Exception as e:
            import traceback
            print(f"Error sending friend request: {str(e)}")
            print(f"User ID: {user_id}, Friend ID: {friend_id}")
            print(traceback.format_exc())
            if hasattr(self, 'conn'):
                try:
                    self.conn.rollback()
                except:
                    pass
            return {'success': False, 'message': f'資料庫錯誤: {str(e)}'}

    def accept_friend_request(self, user_id, friend_id):
        """接受好友請求"""
        try:
            self._ensure_connection()
            # 更新原來的請求狀態
            update_query = """
                UPDATE "FRIENDSHIP"
                SET "Status" = 'accepted', "Updated_at" = NOW()
                WHERE "User_id" = %s AND "Friend_id" = %s AND "Status" = 'pending'
            """
            self.execute_query(update_query, (friend_id, user_id))
            
            # 建立雙向好友關係
            insert_query = """
                INSERT INTO "FRIENDSHIP" ("User_id", "Friend_id", "Status", "Created_at", "Updated_at")
                VALUES (%s, %s, 'accepted', NOW(), NOW())
                ON CONFLICT ("User_id", "Friend_id") 
                DO UPDATE SET "Status" = 'accepted', "Updated_at" = NOW()
            """
            self.execute_query(insert_query, (user_id, friend_id))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error accepting friend request: {str(e)}")
            self.conn.rollback()
            return False

    def reject_friend_request(self, user_id, friend_id):
        """拒絕好友請求"""
        try:
            self._ensure_connection()
            update_query = """
                UPDATE "FRIENDSHIP"
                SET "Status" = 'rejected', "Updated_at" = NOW()
                WHERE "User_id" = %s AND "Friend_id" = %s AND "Status" = 'pending'
            """
            self.execute_query(update_query, (friend_id, user_id))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error rejecting friend request: {str(e)}")
            self.conn.rollback()
            return False

    def remove_friend(self, user_id, friend_id):
        """刪除好友"""
        try:
            self._ensure_connection()
            # 刪除雙向好友關係
            delete_query = """
                DELETE FROM "FRIENDSHIP"
                WHERE ("User_id" = %s AND "Friend_id" = %s)
                OR ("User_id" = %s AND "Friend_id" = %s)
            """
            self.execute_query(delete_query, (user_id, friend_id, friend_id, user_id))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error removing friend: {str(e)}")
            self.conn.rollback()
            return False

    def get_friends_list(self, user_id):
        """獲取好友列表（包含在線狀態）"""
        try:
            # 使用 DISTINCT 避免雙向記錄造成的重複
            # 在線狀態判斷：Is_online 為 TRUE 且 Last_active 在 60 秒內才算在線
            query = """
                SELECT DISTINCT
                    u."User_id",
                    u."User_name",
                    u."User_nickname",
                    u."Avatar_url",
                    CASE 
                        WHEN os."Is_online" = TRUE 
                             AND os."Last_active" > NOW() - INTERVAL '60 seconds'
                        THEN TRUE
                        ELSE FALSE
                    END as is_online,
                    os."Last_active"
                FROM "USER" u
                INNER JOIN "FRIENDSHIP" f ON (
                    (f."Friend_id" = u."User_id" AND f."User_id" = %s)
                    OR (f."User_id" = u."User_id" AND f."Friend_id" = %s)
                )
                LEFT JOIN "USER_ONLINE_STATUS" os ON u."User_id" = os."User_id"
                WHERE f."Status" = 'accepted'
                AND u."User_id" != %s
                ORDER BY is_online DESC, u."User_name" ASC
            """
            result = self.execute_query(query, (user_id, user_id, user_id))
            
            if not result:
                return []
            
            friends = []
            for row in result:
                friends.append({
                    'user_id': row[0],
                    'user_name': row[1],
                    'user_nickname': row[2],
                    'avatar_url': row[3],
                    'is_online': row[4],
                    'last_active': row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None
                })
            return friends
            
        except Exception as e:
            print(f"Error getting friends list: {str(e)}")
            return []

    def get_pending_friend_requests(self, user_id):
        """獲取待處理的好友請求"""
        try:
            query = """
                SELECT 
                    u."User_id",
                    u."User_name",
                    u."User_nickname",
                    u."Avatar_url",
                    f."Created_at"
                FROM "USER" u
                INNER JOIN "FRIENDSHIP" f ON f."User_id" = u."User_id"
                WHERE f."Friend_id" = %s AND f."Status" = 'pending'
                ORDER BY f."Created_at" DESC
            """
            result = self.execute_query(query, (user_id,))
            
            if not result:
                return []
            
            requests = []
            for row in result:
                requests.append({
                    'user_id': row[0],
                    'user_name': row[1],
                    'user_nickname': row[2],
                    'avatar_url': row[3],
                    'created_at': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None
                })
            return requests
            
        except Exception as e:
            print(f"Error getting pending friend requests: {str(e)}")
            return []

    def get_sent_friend_requests(self, user_id):
        """獲取已發送的好友請求"""
        try:
            query = """
                SELECT 
                    u."User_id",
                    u."User_name",
                    u."User_nickname",
                    u."Avatar_url",
                    f."Created_at"
                FROM "USER" u
                INNER JOIN "FRIENDSHIP" f ON f."Friend_id" = u."User_id"
                WHERE f."User_id" = %s AND f."Status" = 'pending'
                ORDER BY f."Created_at" DESC
            """
            result = self.execute_query(query, (user_id,))
            
            if not result:
                return []
            
            requests = []
            for row in result:
                requests.append({
                    'user_id': row[0],
                    'user_name': row[1],
                    'user_nickname': row[2],
                    'avatar_url': row[3],
                    'created_at': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None
                })
            return requests
            
        except Exception as e:
            print(f"Error getting sent friend requests: {str(e)}")
            return []

    def check_friendship_status(self, user_id, other_user_id):
        """檢查兩個用戶之間的好友狀態"""
        try:
            query = """
                SELECT "Status", "User_id"
                FROM "FRIENDSHIP"
                WHERE ("User_id" = %s AND "Friend_id" = %s)
                OR ("User_id" = %s AND "Friend_id" = %s)
                LIMIT 1
            """
            result = self.execute_query(query, (user_id, other_user_id, other_user_id, user_id))
            
            if not result:
                return {'status': 'none', 'is_friend': False}
            
            status = result[0][0]
            requester_id = result[0][1]
            
            if status == 'accepted':
                return {'status': 'accepted', 'is_friend': True}
            elif status == 'pending':
                if requester_id == user_id:
                    return {'status': 'pending_sent', 'is_friend': False}
                else:
                    return {'status': 'pending_received', 'is_friend': False}
            else:
                return {'status': 'none', 'is_friend': False}
            
        except Exception as e:
            print(f"Error checking friendship status: {str(e)}")
            return {'status': 'error', 'is_friend': False}

    def search_users_for_friend(self, query, current_user_id, limit=20):
        """搜尋用戶以添加好友"""
        try:
            sql = """
                SELECT DISTINCT ON (u."User_id")
                    u."User_id", 
                    u."User_name", 
                    u."User_nickname",
                    u."Avatar_url",
                    CASE 
                        WHEN f."Status" = 'accepted' THEN 'friend'
                        WHEN f."Status" = 'pending' AND f."User_id" = %s THEN 'pending_sent'
                        WHEN f."Status" = 'pending' AND f."Friend_id" = %s THEN 'pending_received'
                        ELSE 'none'
                    END as friendship_status
                FROM "USER" u
                LEFT JOIN "USER_ROLE" ur ON u."User_id" = ur."User_id" AND ur."Role" = 'Admin'
                LEFT JOIN "FRIENDSHIP" f ON (
                    (f."User_id" = %s AND f."Friend_id" = u."User_id")
                    OR (f."Friend_id" = %s AND f."User_id" = u."User_id")
                )
                WHERE (u."User_id"::text LIKE %s 
                      OR u."User_nickname" ILIKE %s 
                      OR u."User_name" ILIKE %s
                      OR u."Account" ILIKE %s)
                AND u."User_id" != %s
                AND ur."User_id" IS NULL
                ORDER BY u."User_id"
                LIMIT %s
            """
            search_pattern = f"%{query}%"
            params = (
                current_user_id, current_user_id,
                current_user_id, current_user_id,
                search_pattern, search_pattern, search_pattern, search_pattern,
                current_user_id, limit
            )
            
            result = self.execute_query(sql, params)
            
            return [
                {
                    'user_id': row[0], 
                    'user_name': row[1], 
                    'user_nickname': row[2],
                    'avatar_url': row[3],
                    'friendship_status': row[4] if row[4] else 'none'
                }
                for row in result
            ]
            
        except Exception as e:
            print(f"Error in search_users_for_friend: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    # ==================== 在線狀態功能 ====================

    def update_online_status(self, user_id, is_online):
        """更新用戶在線狀態"""
        try:
            self._ensure_connection()
            query = """
                INSERT INTO "USER_ONLINE_STATUS" ("User_id", "Is_online", "Last_active")
                VALUES (%s, %s, NOW())
                ON CONFLICT ("User_id") 
                DO UPDATE SET "Is_online" = %s, "Last_active" = NOW()
            """
            self.execute_query(query, (user_id, is_online, is_online))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating online status: {str(e)}")
            self.conn.rollback()
            return False

    def get_user_online_status(self, user_id):
        """獲取用戶在線狀態（超過 60 秒沒心跳視為離線）"""
        try:
            query = """
                SELECT 
                    CASE 
                        WHEN "Is_online" = TRUE 
                             AND "Last_active" > NOW() - INTERVAL '60 seconds'
                        THEN TRUE
                        ELSE FALSE
                    END as is_online,
                    "Last_active"
                FROM "USER_ONLINE_STATUS"
                WHERE "User_id" = %s
            """
            result = self.execute_query(query, (user_id,))
            
            if result:
                return {
                    'is_online': result[0][0],
                    'last_active': result[0][1].strftime('%Y-%m-%d %H:%M:%S') if result[0][1] else None
                }
            return {'is_online': False, 'last_active': None}
            
        except Exception as e:
            print(f"Error getting user online status: {str(e)}")
            return {'is_online': False, 'last_active': None}

    def get_all_private_chat_conversations(self, page=1, limit=50):
        """獲取所有私人聊天對話列表（管理員用）"""
        try:
            # 獲取總數
            count_query = """
                SELECT COUNT(DISTINCT LEAST("Sender_id", "Receiver_id") || '-' || GREATEST("Sender_id", "Receiver_id"))
                FROM "PRIVATE_MESSAGE"
            """
            count_result = self.execute_query(count_query)
            total_count = count_result[0][0] if count_result and count_result[0] else 0
            
            if total_count == 0:
                return [], 0
            
            # 獲取對話列表，包含最後一則訊息和訊息數量
            query = """
                WITH conversation_pairs AS (
                    SELECT 
                        LEAST("Sender_id", "Receiver_id") as user1_id,
                        GREATEST("Sender_id", "Receiver_id") as user2_id,
                        COUNT(*) as message_count,
                        MAX("Sending_time") as last_message_time
                    FROM "PRIVATE_MESSAGE"
                    GROUP BY LEAST("Sender_id", "Receiver_id"), GREATEST("Sender_id", "Receiver_id")
                )
                SELECT 
                    cp.user1_id,
                    cp.user2_id,
                    u1."User_name" as user1_name,
                    u1."User_nickname" as user1_nickname,
                    u2."User_name" as user2_name,
                    u2."User_nickname" as user2_nickname,
                    cp.message_count,
                    cp.last_message_time
                FROM conversation_pairs cp
                JOIN "USER" u1 ON cp.user1_id = u1."User_id"
                JOIN "USER" u2 ON cp.user2_id = u2."User_id"
                ORDER BY cp.last_message_time DESC
                LIMIT %s OFFSET %s
            """
            result = self.execute_query(query, (limit, (page - 1) * limit))
            
            conversations = []
            if result:
                for row in result:
                    conversations.append({
                        'user1_id': row[0],
                        'user2_id': row[1],
                        'user1_name': row[2] or '',
                        'user1_nickname': row[3] or '',
                        'user2_name': row[4] or '',
                        'user2_nickname': row[5] or '',
                        'message_count': row[6],
                        'last_message_time': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None
                    })
            
            return conversations, total_count
            
        except Exception as e:
            print(f"Error in get_all_private_chat_conversations: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], 0

    def get_all_meeting_chat_list(self, page=1, limit=50):
        """獲取所有有聊天記錄的聚會列表（管理員用）"""
        try:
            # 獲取有聊天記錄的聚會總數
            count_query = """
                SELECT COUNT(DISTINCT cr."Meeting_id")
                FROM "CHATTING_ROOM" cr
            """
            count_result = self.execute_query(count_query)
            total_count = count_result[0][0] if count_result and count_result[0] else 0
            
            if total_count == 0:
                return [], 0
            
            # 獲取聚會列表，包含聊天訊息數量
            # 注意：MEETING 表的 Content 欄位就是聚會類型（午餐、咖啡/下午茶等）
            query = """
                SELECT 
                    m."Meeting_id",
                    m."Content",
                    m."Event_date",
                    m."Event_place",
                    m."Status",
                    u."User_name" as holder_name,
                    COUNT(cr."Sender_id") as message_count,
                    MAX(cr."Sending_time") as last_message_time
                FROM "MEETING" m
                JOIN "USER" u ON m."Holder_id" = u."User_id"
                JOIN "CHATTING_ROOM" cr ON m."Meeting_id" = cr."Meeting_id"
                GROUP BY m."Meeting_id", m."Content", m."Event_date", m."Event_place", 
                         m."Status", u."User_name"
                ORDER BY last_message_time DESC
                LIMIT %s OFFSET %s
            """
            result = self.execute_query(query, (limit, (page - 1) * limit))
            
            meetings = []
            if result:
                for row in result:
                    meetings.append({
                        'meeting_id': row[0],
                        'content': row[1] or '',  # Content 就是聚會類型
                        'event_date': row[2].strftime('%Y-%m-%d') if row[2] else None,
                        'event_place': row[3] or '',
                        'meeting_type': row[1] or '',  # 用 Content 作為 meeting_type
                        'status': row[4] or '',
                        'holder_name': row[5] or '',
                        'message_count': row[6],
                        'last_message_time': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None
                    })
            
            return meetings, total_count
            
        except Exception as e:
            print(f"Error in get_all_meeting_chat_list: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], 0

    def delete_user(self, user_id):
        """完全刪除用戶（管理員功能）"""
        try:
            self._ensure_connection()
            
            # 由於資料庫有設定 ON DELETE CASCADE，刪除 USER 會自動刪除相關資料
            # 但需要先處理一些特殊情況
            
            # 1. 取消該用戶舉辦的聚會（先更新狀態，避免其他人受影響）
            cancel_meetings_query = """
                UPDATE "MEETING" 
                SET "Status" = 'Cancelled'
                WHERE "Holder_id" = %s AND "Status" != 'Cancelled'
            """
            self.execute_query(cancel_meetings_query, (user_id,))
            
            # 2. 刪除用戶（CASCADE 會自動刪除相關記錄）
            delete_query = """
                DELETE FROM "USER" WHERE "User_id" = %s
            """
            self.execute_query(delete_query, (user_id,))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False