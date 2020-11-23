import csv
from datetime import date, time, datetime
import database_common
from psycopg2 import extensions
from psycopg2.extras import RealDictCursor
import re

QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


@database_common.connection_handler
def add_user(cursor, new_user_data):
    cursor.execute("""
        INSERT INTO users(user_name, password, registration_date)
        VALUES (%s, %s, date_trunc('second', CURRENT_TIMESTAMP));
    """,
        (new_user_data['user_name'],
        new_user_data['password']))


@database_common.connection_handler
def login(cursor, user_name):
    query = """
        SELECT password FROM users
        WHERE user_name = %(user_name)s;
    """
    cursor.execute(query, {'user_name': user_name})
    password = cursor.fetchone()
    return password


@database_common.connection_handler
def get_5_question(cursor, limit, order_by, order_direction):
    query = f"""
                SELECT *
                FROM question
                ORDER BY %(order_by)s %(order_direction)s
                LIMIT %(limit)s
                """
    cursor.execute(query, {"order_by": extensions.AsIs(order_by), "order_direction": extensions.AsIs(order_direction), "limit": limit})
    return cursor.fetchall()


@database_common.connection_handler
def get_all_questions(cursor):
    query = f"""
            SELECT *
            FROM question
            ORDER BY submission_time DESC
            """
    cursor.execute(query)
    return cursor.fetchall()

@database_common.connection_handler
def get_users(cursor):
    query = f"""
            SELECT *
            FROM users
            ORDER BY user_name
        """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_user_by_id(cursor, id):
    query = f"""
            SELECT *
            FROM users
            WHERE id=%(id)s
            """
    cursor.execute(query, {'id': id})
    return cursor.fetchall()

@database_common.connection_handler
def count_for_delete(cursor, answer_id):
    query = f"""
            SELECT COUNT(*)
            FROM comment
            WHERE answer_id=%(answer_id)s;
            """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchall()





@database_common.connection_handler
def count_for_question_delete(cursor, question_id):
    query = f"""
            SELECT COUNT(*)
            FROM answer
            WHERE question_id=%(question_id)s;
            """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()

@database_common.connection_handler
def count_questions(cursor, user_id):
    query = f"""
            SELECT COUNT(*)
            FROM question
            WHERE user_id=%(user_id)s
            """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@database_common.connection_handler
def count_answers(cursor, user_id):
    query = f"""
            SELECT COUNT(*)
            FROM answer
            WHERE user_id=%(user_id)s
            """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@database_common.connection_handler
def count_comments(cursor, user_id):
    query = f"""
            SELECT COUNT(*)
            FROM comment
            WHERE user_id=%(user_id)s
            """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_reputation(cursor, user_id):
    query = """
                SELECT reputation
                FROM users
                WHERE id = %(user_id)s
                """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@database_common.connection_handler
def user_page_questions(cursor, user_id):
    query = f"""
            SELECT *
            FROM question
            WHERE user_id=%(user_id)s
            """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()

@database_common.connection_handler
def user_page_answer(cursor, user_id):
    query = f"""
            SELECT *
            FROM answer
            WHERE user_id=%(user_id)s
            """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()

@database_common.connection_handler
def user_page_comment(cursor, user_id):
    query = f"""
            SELECT *
            FROM comment
            WHERE user_id=%(user_id)s
            """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()

@database_common.connection_handler
def get_user_id_from_user_name(cursor, user_name):
    query = """
            SELECT id FROM users WHERE users.user_name = %(user_name)s
                """
    cursor.execute(query, {'user_name': user_name})
    return cursor.fetchone()


@database_common.connection_handler
def get_all_answers(cursor):
    query = f"""
            SELECT *
            FROM answer
            ORDER BY submission_time
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question_by_id(cursor, id):
    query = f"""
            SELECT *
            FROM question
            WHERE id=%(id)s
            """
    cursor.execute(query, {'id': id})
    return cursor.fetchall()


@database_common.connection_handler
def get_comments(cursor, question_id):
    query = """
            SELECT * FROM comment
                """
    cursor.execute(query, {'question_id': question_id})
    comments = cursor.fetchall()
    return comments


@database_common.connection_handler
def get_answer_by_id(cursor, question_id):
    query = f"""
            SELECT *
            FROM answer
            WHERE question_id=%(question_id)s
            """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_unique_answer(cursor, id):
    query = f"""
            SELECT *
            FROM answer
            WHERE id=%(id)s
            """
    cursor.execute(query, {'id': id})
    return cursor.fetchall()


@database_common.connection_handler
def get_unique_comment(cursor, id):
    query = f"""
            SELECT *
            FROM comment
            WHERE id=%(id)s
            """
    cursor.execute(query, {'id': id})
    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor, title, message, image, user_id):
    query = f"""
            INSERT INTO question (submission_time, vote_number, view_number, title, message, image, user_id)
            VALUES (date_trunc('second', CURRENT_TIMESTAMP), 0, 0, %(title)s,  %(message)s,  %(image)s, %(user_id)s);
            UPDATE users
            SET count_asked_question = count_asked_question + 1
            WHERE id=%(user_id)s
            """
    cursor.execute(query, {'title': title, 'message': message, 'image': image, 'user_id': user_id})


@database_common.connection_handler
def add_comment_to_question(cursor, message, question_id, user_id):
    query = f"""
            INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count, user_id)
            VALUES (%(question_id)s, NULL , %(message)s, date_trunc('second', CURRENT_TIMESTAMP), 0, %(user_id)s);
            UPDATE users
            SET count_of_comments = count_of_comments + 1
            WHERE id=%(user_id)s
            """
    cursor.execute(query, {'question_id': question_id, 'message': message, 'user_id': user_id})


@database_common.connection_handler
def add_comment_to_answer(cursor, message, question_id, answer_id, user_id):
    query = f"""
            INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count, user_id)
            VALUES ( %(question_id)s , %(answer_id)s, %(message)s, date_trunc('second', CURRENT_TIMESTAMP),
            0, %(user_id)s );
            UPDATE users
            SET count_of_comments = count_of_comments + 1
            WHERE id=%(user_id)s
            """
    cursor.execute(query, {'question_id': question_id, 'answer_id': answer_id, 'message': message, 'user_id': user_id})


@database_common.connection_handler
def add_answer(cursor, message, image, question_id, user_id):
    query = f"""
            INSERT INTO answer (submission_time, vote_number, message, image, question_id, user_id)
            VALUES (CURRENT_TIMESTAMP, 0,  %(message)s, %(question_id)s, %(image)s, %(user_id)s);
            UPDATE users
            SET count_of_answers = count_of_answers + 1
            WHERE id=%(user_id)s
            """
    cursor.execute(query, {'message': message, 'question_id': question_id, 'image': image, 'user_id': user_id})


@database_common.connection_handler
def delete_comment(cursor, comment_id, user_id):
    query = f"""
                DELETE
                FROM comment
                WHERE id=%(comment_id)s;
                UPDATE users
                SET count_of_comments = count_of_comments - 1
                WHERE id=%(user_id)s 
                """
    cursor.execute(query, {'comment_id': comment_id, 'user_id': user_id})


@database_common.connection_handler
def delete_question(cursor, question_id, user_id, count_delete_question, counted_delete):
    query3 = f"""
                DELETE
                FROM comment
                WHERE question_id=%(question_id)s;
                UPDATE users
                SET count_of_comments = count_of_comments - %(counted_delete)s
                WHERE  count_of_comments > 0 AND id=%(user_id)s 
                """
    cursor.execute(query3, {'question_id': question_id, 'user_id': user_id, 'counted_delete': counted_delete})
    query = f"""
            DELETE
            FROM answer
            WHERE question_id=%(question_id)s;
            UPDATE users
            SET count_of_answers = count_of_answers - %(count_delete_question)s
            WHERE id=%(user_id)s
            """
    cursor.execute(query, {'question_id': question_id, 'user_id': user_id, 'counted_delete': counted_delete, 'count_delete_question': count_delete_question})

    query2 = f"""
            DELETE
            FROM question
            WHERE id=%(question_id)s;
            UPDATE users
            SET count_asked_question = count_asked_question - 1
            WHERE id=%(user_id)s
            """
    cursor.execute(query2, {'question_id': question_id, 'user_id': user_id, 'count_delete_question': count_delete_question})



@database_common.connection_handler
def delete_answer(cursor, answer_id, user_id, counted_delete):
    query2 = f"""
                DELETE
                FROM comment
                WHERE answer_id=%(answer_id)s;
                UPDATE users
                SET count_of_comments = count_of_comments - %(counted_delete)s
                WHERE id=%(user_id)s
                """
    cursor.execute(query2, {'answer_id': answer_id, 'user_id': user_id, 'counted_delete': counted_delete})
    query = f"""
                DELETE
                FROM answer
                WHERE id=%(answer_id)s;
                UPDATE users
                SET count_of_answers = count_of_answers - 1
                WHERE id=%(user_id)s
                """
    cursor.execute(query, {'answer_id': answer_id, 'user_id': user_id})

@database_common.connection_handler
def delete_comment(cursor, comment_id, user_id):
    query = f"""
                DELETE
                FROM comment
                WHERE id=%(comment_id)s;
                UPDATE users
                SET count_of_comments = count_of_comments - 1
                WHERE id=%(user_id)s
            """
    cursor.execute(query, {'comment_id': comment_id, 'user_id': user_id})

@database_common.connection_handler
def vote_up_question(cursor, question_id, vote, user_id):
    query = f"""
                UPDATE question
                SET vote_number = vote_number + %(vote)s
                WHERE id=%(question_id)s;
                UPDATE users
                SET reputation = reputation + 5
                WHERE id =%(user_id)s;
                """
    cursor.execute(query, {'question_id': question_id, 'vote': vote, 'user_id': user_id})


@database_common.connection_handler
def vote_down_question(cursor, question_id, vote, user_id):
    query = f"""
                UPDATE question
                SET vote_number = vote_number + %(vote)s
                WHERE id=%(question_id)s;
                UPDATE users
                SET reputation = reputation - 2
                WHERE id =%(user_id)s;
                """
    cursor.execute(query, {'question_id': question_id, 'vote': vote, 'user_id': user_id})


@database_common.connection_handler
def vote_up_answer(cursor, answer_id, vote, user_id):
    query = f"""
                UPDATE answer
                SET vote_number = vote_number + %(vote)s 
                WHERE id=%(answer_id)s;
                UPDATE users
                SET reputation = reputation + 10
                WHERE id =%(user_id)s;
                """
    cursor.execute(query, {'answer_id': answer_id, 'vote': vote, 'user_id': user_id})


@database_common.connection_handler
def vote_down_answer(cursor, answer_id, vote, user_id):
    query = f"""
                UPDATE answer
                SET vote_number = vote_number + %(vote)s 
                WHERE id=%(answer_id)s;
                UPDATE users
                SET reputation = reputation - 2
                WHERE id =%(user_id)s;
                """
    cursor.execute(query, {'answer_id': answer_id, 'vote': vote, 'user_id': user_id})



@database_common.connection_handler
def edit_question(cursor, question_id, title, message, image):
    query = f"""
                UPDATE question
                SET title=%(title)s,
                    message=%(message)s,
                    image=%(image)s
                WHERE id=%(question_id)s 
                """
    cursor.execute(query, {'question_id': question_id, 'title': title, 'message': message, 'image': image})


@database_common.connection_handler
def edit_answer(cursor, answer_id, message, image):
    query = f"""
                UPDATE answer
                SET message=%(message)s,
                    image=%(image)s
                WHERE id=%(answer_id)s 
                """
    cursor.execute(query, {'answer_id': answer_id, 'message': message, 'image': image})


@database_common.connection_handler
def edit_comment(cursor, comment_id, message):
    query = f"""
                UPDATE comment
                SET message=%(message)s
                WHERE id=%(comment_id)s 
                """
    cursor.execute(query, {'comment_id': comment_id, 'message': message})


@database_common.connection_handler
def accept_answer(cursor, answer_id, user_id):
    query = f"""
                UPDATE answer
                SET accepted = TRUE
                WHERE id=%(answer_id)s;
                UPDATE users
                SET reputation = reputation + 15
                WHERE id = %(user_id)s;
                """
    cursor.execute(query, {'answer_id': answer_id, 'user_id': user_id})


@database_common.connection_handler
def not_accept_answer(cursor, answer_id, user_id):
    query = f"""
                UPDATE answer
                SET accepted = FALSE
                WHERE id=%(answer_id)s;
                UPDATE users
                SET reputation = reputation - 15
                WHERE id = %(user_id)s;
                """
    cursor.execute(query, {'answer_id': answer_id, 'user_id': user_id})


@database_common.connection_handler
def search_fancy_question(cursor, text) -> list:
    query = """
        SELECT *
        FROM question
        WHERE "message" ILIKE %(text)s OR "title" ILIKE %(text)s
        """
    cursor.execute(query, {'text': '%' + text + '%'})
    search_results = cursor.fetchall()
    highlighted_list = []
    for dictionary in search_results:
        pattern = re.compile(re.escape(text), re.IGNORECASE)
        temp = pattern.sub(f'<span class = "highlight">{text}</span>', dictionary['title'], re.I)
        highlighted_list.append(temp)
    return highlighted_list


@database_common.connection_handler
def search_result(cursor, text):
    query = """
            SELECT *
            FROM question
            WHERE "message" ILIKE %(text)s OR "title" ILIKE %(text)s
            """
    cursor.execute(query, {'text': '%' + text + '%'})
    return cursor.fetchall()


@database_common.connection_handler
def search_in_answers(cursor: RealDictCursor, text) -> list:
    query = """
        SELECT question_id
        FROM answer
        WHERE message LIKE %s
        """
    var1 = (f'%{text}%',)
    cursor.execute(query, var1)
    # result = cursor.fetchall()
    # ids = [answer.questio for answer in result]
    # query2 = """
    #     SELECT *
    #     FROM question
    #     WHERE id IN %s AND LOWER(%s) NOT IN LOWER(concat(question.title, question.message))
    #     """
    # var2 = (f"%{ids}%", f"%{text}%")
    # cursor.execute(query2, var2)
    return cursor.fetchall()


@database_common.connection_handler
def add_new_tag(cursor, tag):
    cursor.execute("""
    INSERT INTO tag (name) VALUES ( %(tag)s);""",
                   {'tag': tag})


@database_common.connection_handler
def get_tagz(cursor, question_id):
    cursor.execute("""
                SELECT tag.name
                FROM tag
                LEFT JOIN question_tag  on tag.id = question_tag.tag_id
                GROUP BY tag.name
        """)
    all_tags = cursor.fetchall()
    return all_tags








