import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime
from flask import jsonify


class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.conn = psycopg2.connect(
            dbname="bello", 
            user="postgres", 
            password=0000, 
            host="127.0.0.1,", 
            port=5432
        )
        print()

    def execute_query(self, query, params=None):
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)

            if (
                query.strip().upper().startswith("SELECT")
                or "RETURNING" in query.upper()
            ):
                result = cur.fetchall()
            else:
                self.conn.commit()
                result = cur.fetchall() if "RETURNING" in query.upper() else True

            cur.close()
            return result

        except Exception as e:
            print(f"Query execution error: {e}")
            raise e

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()

    def check_account_exists(self, account):
        query = 'SELECT COUNT(*) FROM "USER" WHERE Account = %s'
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
            max_id_query = 'SELECT COALESCE(MAX(User_id), 0) FROM "USER"'
            result = self.execute_query(max_id_query)
            new_user_id = result[0][0] + 1

            # 插入用戶資料
            insert_query = """
                INSERT INTO "USER" (
                    User_id, Account, Password, User_name, User_nickname, 
                    Nationality, City, Phone, Email, Sex, Birthday, Register_time
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING User_id
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
                INSERT INTO "user_role" (User_id, Role)
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
                SELECT u.User_id, u.User_name, u.User_nickname, u.Email, r.Role
                FROM "USER" u
                JOIN "user_role" r ON u.User_id = r.User_id
                WHERE u.Account = %s AND u.Password = %s
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

    def update_user_detail(self, field, value, user_id):
        try:
            cursor = self.conn.cursor()

            # 檢查用戶是否已有詳細資料記錄
            check_query = """
                SELECT Self_introduction FROM USER_DETAIL WHERE User_id = %s
            """
            cursor.execute(check_query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                # 如果有記錄,更新現有記錄
                update_query = f"""
                    UPDATE USER_DETAIL 
                    SET {field} = %s
                    WHERE User_id = %s AND Self_introduction = %s
                """
                cursor.execute(update_query, (value, user_id, result[0]))
            else:
                # 如果沒有記錄,插入新記錄
                # 注意:這裡需要同時插入 Self_introduction,因為它是主鍵的一部分
                insert_query = """
                    INSERT INTO USER_DETAIL (User_id, Self_introduction, {}) 
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
                m.Meeting_id,
                m.Content,
                m.Event_date,
                m.Start_time,
                m.End_time,
                m.Event_city,
                m.Event_place,
                m.Status,
                m.Num_participant,
                m.Max_num_participant,
                u.User_name as holder_name,
                string_agg(ml.Language, ', ') as languages
            FROM MEETING m
            JOIN "USER" u ON m.Holder_id = u.User_id
            LEFT JOIN MEETING_LANGUAGE ml ON m.Meeting_id = ml.Meeting_id
            WHERE m.Status = 'Ongoing'
            GROUP BY 
                m.Meeting_id, m.Content, m.Event_date, m.Start_time,
                m.End_time, m.Event_city, m.Event_place, m.Status,
                m.Num_participant, m.Max_num_participant, u.User_name
            ORDER BY m.Event_date DESC, m.Start_time DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def create_meeting(self, meeting_data):
        try:
            with self.conn.cursor() as cur:
                # 先獲取最大的 Meeting_id
                get_max_id_query = """
                    SELECT COALESCE(MAX(Meeting_id), 0) + 1
                    FROM MEETING
                """
                cur.execute(get_max_id_query)
                new_meeting_id = cur.fetchone()[0]

                # 插入聚會基本信息
                insert_meeting_query = """
                    INSERT INTO MEETING (
                        Meeting_id,
                        Holder_id,
                        Content,
                        Event_date,
                        Start_time,
                        End_time,
                        Event_city,
                        Event_place,
                        Status,
                        Num_participant,
                        Max_num_participant
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, 'Ongoing', 1, %s
                    ) RETURNING Meeting_id
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
                        meeting_data["max_participants"],
                    ),
                )

                meeting_id = cur.fetchone()[0]

                # 插入聚會語言
                for language in meeting_data["languages"]:
                    insert_language_query = """
                        INSERT INTO MEETING_LANGUAGE (Meeting_id, Language)
                        VALUES (%s, %s)
                    """
                    cur.execute(insert_language_query, (meeting_id, language))

                # 創建者自動加入聚會
                insert_participation_query = """
                    INSERT INTO PARTICIPATION (Meeting_id, User_id, Join_time)
                    VALUES (%s, %s, NOW())
                """
                cur.execute(
                    insert_participation_query, (meeting_id, meeting_data["holder_id"])
                )

                self.conn.commit()
                return True

        except Exception as e:
            print(f"Error creating meeting: {str(e)}")
            self.conn.rollback()
            return False

    def check_meeting_availability(self, meeting_id):
        query = """
                SELECT Meeting_id 
                FROM MEETING 
                WHERE Meeting_id = %s 
                AND Status = 'Ongoing'
                AND Num_participant < Max_num_participant
                """
        result = self.execute_query(query, (meeting_id,))
        return result and len(result) > 0

    def is_user_in_meeting(self, user_id, meeting_id):
        query = """
                SELECT 1
                FROM participation
                WHERE User_id = %s AND Meeting_id = %s
                """
        result = self.execute_query(query, (user_id, meeting_id))
        return bool(result)

    def join_meeting(self, user_id, meeting_id):
        try:
            # 檢查聚會是否已滿
            check_query = """
                SELECT Num_participant, Max_num_participant
                FROM MEETING
                WHERE Meeting_id = %s
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
                INSERT INTO PARTICIPATION (User_id, Meeting_id, Join_time)
                VALUES (%s, %s, NOW())
            """
            self.execute_query(insert_query, (user_id, meeting_id))

            # 更新聚會人數
            update_query = """
                UPDATE MEETING 
                SET Num_participant = Num_participant + 1
                WHERE Meeting_id = %s
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
                    m.Meeting_id,
                    m.Content,
                    m.Event_date,
                    m.Start_time,
                    m.End_time,
                    m.Event_city,
                    m.Event_place,
                    m.Num_participant,
                    m.Max_num_participant,
                    m.Status,
                    m.Holder_id,
                    u.User_nickname as holder_name
                FROM MEETING m
                JOIN "USER" u ON m.Holder_id = u.User_id
                WHERE m.Meeting_id IN (
                    SELECT Meeting_id 
                    FROM PARTICIPATION 
                    WHERE User_id = %s
                )
                ORDER BY m.Event_date, m.Start_time
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
            # 檢查用戶是否在聚會中
            check_query = """
                SELECT 1 FROM PARTICIPATION
                WHERE User_id = %s AND Meeting_id = %s
            """
            result = self.execute_query(check_query, (user_id, meeting_id))
            if not result:
                return False

            # 刪除參與記錄
            delete_query = """
                DELETE FROM PARTICIPATION
                WHERE User_id = %s AND Meeting_id = %s
            """
            self.execute_query(delete_query, (user_id, meeting_id))

            # 更新聚會人數
            update_query = """
                UPDATE MEETING 
                SET Num_participant = Num_participant - 1
                WHERE Meeting_id = %s
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
            query = """
                UPDATE MEETING 
                SET Status = 'Canceled'
                WHERE Meeting_id = %s
                AND Status = 'Ongoing'
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
            # 檢查聚會是否存在且狀態為進行中
            check_query = """
                SELECT 1 FROM MEETING
                WHERE Meeting_id = %s
                AND Status = 'Ongoing'
            """
            result = self.execute_query(check_query, (meeting_id,))
            if not result:
                return False

            # 更新聚會狀態
            update_query = """
                UPDATE MEETING 
                SET Status = 'Finished'
                WHERE Meeting_id = %s
                AND Status = 'Ongoing'
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
                    m.Meeting_id,
                    m.Content,
                    m.Event_date,
                    m.Event_place,
                    m.Status,
                    m.max_num_participant,
                    m.Holder_id,
                    u.User_name as holder_name,
                    m.Num_participant
                FROM MEETING m
                LEFT JOIN "USER" u ON m.Holder_id = u.User_id
                ORDER BY 
                    CASE m.Status
                        WHEN 'Ongoing' THEN 1
                        WHEN 'Finished' THEN 2
                        WHEN 'Cancelled' THEN 3
                    END,
                    m.Event_date DESC
            """

            result = self.execute_query(query)
            if not result:
                return []

            meetings = []
            for row in result:
                # 獲取每個聚會的參與者
                participants_query = """
                    SELECT u.User_id, u.User_name, u.User_nickname
                    FROM "USER" u
                    JOIN PARTICIPATION p ON u.User_id = p.User_id
                    WHERE p.Meeting_id = %s
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
            query = """
                    UPDATE MEETING 
                    SET Status = 'Canceled'
                    WHERE Meeting_id = %s
                    AND Status = 'Ongoing'
                    """
            self.execute_query(query, (meeting_id,))
            return True
        except Exception as e:
            print(f"Error in admin cancel meeting: {e}")
            return False

    def admin_finish_meeting(self, meeting_id):
        try:
            query = """
                    UPDATE MEETING 
                    SET Status = 'Finished'
                    WHERE Meeting_id = %s
                    AND Status = 'Ongoing'
                    """
            self.execute_query(query, (meeting_id,))
            return True
        except Exception as e:
            print(f"Error in admin finish meeting: {e}")
            return False

    def add_sns_detail(self, user_id, sns_type, sns_id):
        try:
            # 先刪除舊的記錄（如果存在）
            delete_query = """
                DELETE FROM SNS_DETAIL 
                WHERE User_id = %s AND Sns_type = %s
            """
            self.execute_query(delete_query, (user_id, sns_type))
            
            # 插入新記錄
            insert_query = """
                INSERT INTO SNS_DETAIL (User_id, Sns_type, Sns_id)
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
                SELECT sns_type, sns_id 
                FROM SNS_DETAIL 
                WHERE User_id = %s
            """
            result = self.execute_query(sql, (user_id,))
            return [{"sns_type": row[0], "sns_id": row[1]} for row in result]
        except Exception as e:
            print(f"Error in get_sns_details: {str(e)}")
            return []

    def remove_sns_detail(self, user_id, sns_type):
        try:
            sql = """
                DELETE FROM SNS_DETAIL 
                WHERE User_id = %s AND sns_type = %s
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
                cr.meeting_id,
                cr.sender_id,
                u.User_name as sender_name,
                cr.content,
                cr.sending_time
            FROM chatting_room cr
            JOIN "USER" u ON cr.sender_id = u.User_id
            WHERE cr.meeting_id = %s
            ORDER BY cr.sending_time ASC
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
            query = """
                INSERT INTO chatting_room (meeting_id, sender_id, content, sending_time)
                VALUES (%s, %s, %s, NOW())
                RETURNING meeting_id
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
            SELECT u.User_id, u.User_nickname as nickname
            FROM "USER" u
            LEFT JOIN user_role ur ON u.User_id = ur.User_id AND ur.Role = 'Admin'
            WHERE u.User_id != %s AND ur.User_id IS NULL
            ORDER BY u.User_nickname
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
                m.Meeting_id,
                m.Content,
                m.Event_city,
                m.Event_place,
                m.Event_date,
                m.Start_time,
                m.End_time,
                m.Max_num_participant,
                m.Num_participant,
                m.Holder_id,
                u.User_nickname as holder_name,
                (
                    SELECT string_agg(ml.Language, ',')
                    FROM MEETING_LANGUAGE ml
                    WHERE ml.Meeting_id = m.Meeting_id
                ) as languages
            FROM MEETING m
            JOIN "USER" u ON m.Holder_id = u.User_id
            WHERE m.Status = 'Ongoing'
            AND m.Meeting_id NOT IN (
                SELECT Meeting_id 
                FROM PARTICIPATION 
                WHERE User_id = %s
            )
            AND m.Holder_id != %s
            AND m.Num_participant < m.Max_num_participant
            ORDER BY m.Event_date, m.Start_time
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
                }
            )
        return meetings

    def get_user_basic_info(self, user_id):
        query = """
            SELECT Account, User_name, User_nickname, Email, Phone, Birthday
            FROM "USER"
            WHERE User_id = %s
        """
        result = self.execute_query(query, (user_id,))
        if result:
            return {
                "account": result[0][0],
                "user_name": result[0][1],
                "user_nickname": result[0][2],
                "email": result[0][3],
                "phone": result[0][4],
                "birthday": result[0][5].strftime("%Y-%m-%d"),
            }
        return None

    def get_user_profile_info(self, user_id):
        query = """
            SELECT Star_sign, Mbti, Blood_type, Religion, University,
                Married, Sns, Self_introduction, Interest, Find_meeting_type
            FROM USER_DETAIL
            WHERE User_id = %s
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

    def remove_user_from_meeting(self, meeting_id, user_id):
        try:
            # 先檢查用戶是否在聚會中
            check_query = """
                SELECT 1 FROM PARTICIPATION 
                WHERE Meeting_id = %s AND User_id = %s
            """
            result = self.execute_query(check_query, (meeting_id, user_id))

            if not result:
                return False

            # 從聚會中移除用戶
            delete_query = """
                DELETE FROM PARTICIPATION 
                WHERE Meeting_id = %s AND User_id = %s
            """
            self.execute_query(delete_query, (meeting_id, user_id))

            # 更新聚會參與人數
            update_query = """
                UPDATE MEETING 
                SET Num_participant = Num_participant - 1
                WHERE Meeting_id = %s
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
                    WHERE u.User_id::text LIKE %s
                """
                count_result = self.execute_query(count_query, (f"%{search_id}%",))
                total_count = count_result[0][0] if count_result else 0

                query = """
                    SELECT u.User_id, u.Account, u.User_name, u.User_nickname, 
                           u.Email, u.Phone, u.Birthday, u.Sex, u.City
                    FROM "USER" u
                    WHERE u.User_id::text LIKE %s
                    ORDER BY u.User_id
                    LIMIT %s OFFSET %s
                """
                params = (f"%{search_id}%", limit, (page - 1) * limit)
            else:
                count_query = 'SELECT COUNT(*) FROM "USER"'
                count_result = self.execute_query(count_query)
                total_count = count_result[0][0] if count_result else 0

                query = """
                    SELECT u.User_id, u.Account, u.User_name, u.User_nickname, 
                           u.Email, u.Phone, u.Birthday, u.Sex, u.City
                    FROM "USER" u
                    ORDER BY u.User_id
                    LIMIT %s OFFSET %s
                """
                params = (limit, (page - 1) * limit)

            result = self.execute_query(query, params)
            users = []
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
                u.user_id,
                u.user_name,
                u.User_nickname,
                COUNT(pm.sender_id) as message_count
            FROM "USER" u
            INNER JOIN private_message pm 
            ON (u.user_id = pm.sender_id OR u.user_id = pm.receiver_id)
            WHERE (pm.sender_id = %s OR pm.receiver_id = %s)
            AND u.user_id != %s
            GROUP BY u.user_id, u.user_name, u.User_nickname
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
                pm.sender_id,
                pm.receiver_id,
                pm.sending_time,
                pm.content,
                u.user_name as sender_name
            FROM private_message pm
            INNER JOIN "USER" u ON pm.sender_id = u.user_id
            WHERE (pm.sender_id = %s AND pm.receiver_id = %s)
            OR (pm.sender_id = %s AND pm.receiver_id = %s)
            ORDER BY pm.sending_time DESC
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
                Meeting_id,
                Content,
                Event_date,
                Event_place,
                Num_participant,
                Max_num_participant,
                Status
            FROM MEETING
            WHERE Meeting_id = %s
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
                mm.meeting_id,
                mm.sender_id,
                u.User_name,
                mm.content,
                mm.sending_time
            FROM chatting_room mm
            INNER JOIN "USER" u ON mm.sender_id = u.User_id
            WHERE mm.meeting_id = %s
            ORDER BY mm.sending_time ASC
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
                        "sender_name": row[2],
                        "content": row[3],
                        "timestamp": row[4].strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
            return messages

        except Exception as e:
            print(f"Error getting meeting chat history: {e}")
            return None

    def get_user_chat_list(self, user_id):
        """獲取用戶的聊天列表"""
        try:
            cursor = self.conn.cursor()
            query = """
                WITH chat_partners AS (
                    SELECT DISTINCT 
                        CASE 
                            WHEN pm.sender_id = %s THEN pm.receiver_id
                            ELSE pm.sender_id 
                        END as partner_id
                    FROM private_message pm
                    WHERE pm.sender_id = %s OR pm.receiver_id = %s
                )
                SELECT 
                    cp.partner_id,
                    u.user_name,
                    (
                        SELECT sending_time 
                        FROM private_message pm2
                        WHERE (
                            (pm2.sender_id = %s AND pm2.receiver_id = cp.partner_id)
                            OR 
                            (pm2.sender_id = cp.partner_id AND pm2.receiver_id = %s)
                        )
                        ORDER BY sending_time DESC
                        LIMIT 1
                    ) as last_message_time
                FROM chat_partners cp
                JOIN "USER" u ON u.user_id = cp.partner_id
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
                        "last_message_time": (
                            row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else None
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
                    pm.sender_id,
                    u.User_name as sender_name,
                    pm.content,
                    pm.sending_time
                FROM private_message pm
                JOIN "USER" u ON pm.sender_id = u.User_id
                WHERE (
                    (pm.sender_id = %s AND pm.receiver_id = %s)
                    OR 
                    (pm.sender_id = %s AND pm.receiver_id = %s)
                )
                ORDER BY pm.sending_time ASC
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
            query = """
                INSERT INTO private_message (sender_id, receiver_id, content, sending_time)
                VALUES (%s, %s, %s, NOW())
                RETURNING sender_id
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
                    u.user_id,
                    u.user_name
                FROM "USER" u
                LEFT JOIN user_role ur ON u.user_id = ur.user_id
                WHERE u.user_id != %s 
                AND (ur.role != 'admin' OR ur.role IS NULL)
                ORDER BY u.user_name
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
                SELECT User_id, User_name, User_nickname
                FROM "USER"
                WHERE (User_id::text LIKE %s 
                      OR User_nickname LIKE %s 
                      OR User_name LIKE %s)
                AND User_id != %s
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