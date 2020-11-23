from flask import Flask, render_template, redirect, request, url_for, session, flash
import data_manager
import auth
import secrets
from datetime import date, time, datetime


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route("/")
def landing_page():
    return redirect(url_for("list"))


@app.route("/list")
def list():
    user_id = session.get('id', None)
    question_header = data_manager.QUESTION_HEADER
    order_direction = request.args.get("order_direction")
    order_by = request.args.get("order_by")
    args = request.args
    if order_direction == 'descending':
        order_direction = 'DESC'
    elif order_direction == "ascending":
        order_direction = 'ASC'
    if "order_direction" and "order_by" in args:
        questions = data_manager.get_all_questions()
    else:
        order_direction = 'DESC'
        order_by = 'submission_time'
    if request.args.get("all_question"):
        questions = data_manager.get_all_questions()
    else:
        questions = data_manager.get_5_question(5, order_by, order_direction)

    return render_template("index.html", questions=questions, question_header=question_header,
                           order_by=order_by, order_direction=order_direction, user_id=user_id)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        new_user_data = {
            'user_name': request.form['user_name'],
            'password': auth.hash_password(request.form['password'])}
        data_manager.add_user(new_user_data)
        return redirect(url_for('list'))


@app.route('/users', methods=['GET', 'POST'])
def list_users():
    if request.method == 'GET':
        users = data_manager.get_users()
        return render_template('users.html', users=users)
    return redirect(url_for('list'))


@app.route('/user_page/<user_id>', methods=['POST', 'GET'])
def user_page(user_id):
    if request.method == 'GET':
        user = data_manager.get_user_by_id(user_id)
        count_questions = data_manager.count_questions(user_id)
        count_answer = data_manager.count_answers(user_id)
        user_question = data_manager.user_page_questions(user_id)
        user_answer = data_manager.user_page_answer(user_id)
        user_comment = data_manager.user_page_comment(user_id)
        count_comment = data_manager.count_comments(user_id)
        reputation = data_manager.get_reputation(user_id)
        return render_template('user_page.html', user=user, count_questions=count_questions,
                                count_answer=count_answer, user_question=user_question,
                                user_answer=user_answer, user_comment=user_comment, count_comment=count_comment,
                                reputation=reputation)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_password = request.form['password']
        db_password = data_manager.login(request.form['user_name'])
        if auth.verify_password(input_password, db_password['password']):
            session['user_name'] = request.form['user_name']
            user_name = session['user_name']
            user_id = data_manager.get_user_id_from_user_name(user_name)
            session['id'] = user_id['id']
            return redirect(url_for('list', user_name=user_name, user_id=session['id']))
        else:
            flash("Wrong password")
    return render_template('login.html')


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.clear()
   return redirect(url_for('list'))


@app.route("/list/question/<question_id>")
def display_question(question_id):
    questions = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answer_by_id(question_id)
    comments = data_manager.get_comments(question_id)
    tag = data_manager.get_tagz(question_id)
    user_id = session.get('id', None)
    question_user_id = [question['user_id'] for question in questions]
    return render_template("display_question.html", questions=questions, answers=answers,
                           question_id=question_id, comments=comments, tag=tag, user_id=user_id, question_user_id=question_user_id)


@app.route('/search', methods=['GET', 'POST'])
def search_questions():
    if request.args:
        text = request.args.get('search')
        questions = data_manager.search_result(text)
        search_results = data_manager.search_fancy_question(text)
        question_answer = data_manager.search_in_answers(text)
        return render_template("search.html", questions=questions, question_header=data_manager.QUESTION_HEADER,
                               text=text, question_answer=question_answer, search_results=search_results)


@app.route("/list/question/<question_id>/answer/<answer_id>")
def answer_page(question_id, answer_id):
    answers = data_manager.get_answer_by_id(question_id)
    all_comment = data_manager.get_comments(answer_id)
    comments = []
    for comment in all_comment:
        if comment['answer_id'] == answer_id:
            comments.append(comment)
    return render_template("answer.html", question_id=question_id, answer_id=answer_id, answers=answers, comments=comments)


@app.route("/list/question/<question_id>/answer/<answer_id>/accept")
def accept_answer(answer_id, question_id):
    if session['id']:
        user_id = session['id']
    else:
        pass
    data_manager.accept_answer(answer_id, user_id)
    return redirect("/list/question/" + question_id)


@app.route("/list/question/<question_id>/answer/<answer_id>/not_accept")
def not_accept_answer(answer_id, question_id):
    if session['id']:
        user_id = session['id']
    else:
        pass
    data_manager.not_accept_answer(answer_id, user_id)
    return redirect("/list/question/" + question_id)


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        image = request.form["image"]
        user_id = session.get('id', None)
        data_manager.add_question(title, message, image, user_id)
        return redirect("/list")
    return render_template("add_question.html")


@app.route("/list/question/<question_id>/new_comment", methods=["GET", "POST"])
def add_comment_to_question(question_id):
    if request.method == "POST":
        message = request.form["message"]
        user_id = session['id']
        data_manager.add_comment_to_question(message, question_id, user_id)
        return redirect("/list/question/" + question_id)
    return render_template("add_comment_to_question.html", question_id=question_id)


@app.route("/list/question/<question_id>/answer/<answer_id>/new_comment", methods=["GET", "POST"])
def add_comment_to_answer(question_id, answer_id):
    if request.method == "POST":
        message = request.form["message"]
        user_id = session['id']
        data_manager.add_comment_to_answer(message, question_id, answer_id, user_id)
        return redirect("/list/question/" + question_id)
    return render_template("add_comment_to_answer.html", question_id=question_id, answer_id=answer_id)


@app.route("/list/question/<question_id>/new-answer", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == "POST":
        message = request.form["answer"]
        image = request.form["image"]
        user_id = session['id']
        data_manager.add_answer(message, question_id, image, user_id)
        return redirect("/list/question/" + question_id)
    return render_template("add_answer.html", question_id=question_id)


@app.route("/list/question/<question_id>/delete")
def delete_question(question_id):
    user_id = session['id']
    count_question = data_manager.count_for_question_delete(question_id)
    count_answer = data_manager.count_for_delete(question_id)
    data_manager.delete_question(question_id, user_id, count_question[0]['count'], count_answer[0]['count'])
    return redirect("/list")


@app.route("/list/question/<question_id>/answer/<answer_id>/delete",  methods=["GET", "POST"])
def delete_answer(question_id, answer_id):
    user_id = session['id']
    count_delete = data_manager.count_for_delete(answer_id)
    counted = [count['count'] for count in count_delete]
    data_manager.delete_answer(answer_id, user_id, counted[0])
    return redirect("/list/question/" + question_id)


@app.route("/list/question/<question_id>/comment/<comment_id>/delete")
def delete_answer_comment(question_id, comment_id):
    user_id = session['id']
    data_manager.delete_comment(comment_id, user_id)
    return redirect("/list/question/" + question_id)

@app.route("/list/question/<question_id>/comment/<comment_id>/delete", methods=["GET", "POST"])
def delete_comment(question_id, comment_id):
    user_id = session['id']
    data_manager.delete_comment(comment_id, user_id)
    return redirect("/list/question/" + str(question_id))


@app.route("/list/question/<question_id>/vote_up")
def vote_up_question(question_id):
    if session['id']:
        user_id = session['id']
    else:
        pass
    data_manager.vote_up_question(question_id, 1, user_id)
    return redirect("/list/question/" + question_id)


@app.route("/list/question/<question_id>/vote_down")
def vote_down_question(question_id):
    if session['id']:
        user_id = session['id']
    else:
        pass
    data_manager.vote_down_question(question_id, -1, user_id)
    return redirect("/list/question/" + question_id)


@app.route("/list/question/<question_id>/answer/<answer_id>/vote_up")
def vote_up_answer(question_id, answer_id):
    if session['id']:
        user_id = session['id']
    else:
        pass
    data_manager.vote_up_answer(answer_id, 1, user_id)
    return redirect("/list/question/" + question_id)


@app.route("/list/question/<question_id>/answer/<answer_id>/vote_down")
def vote_down_answer(question_id, answer_id):
    if session['id']:
        user_id = session['id']
    else:
        pass
    data_manager.vote_down_answer(answer_id, -1, user_id)
    return redirect("/list/question/" + question_id)


@app.route("/list/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == "POST":
        question_id = question_id
        title = request.form["title"]
        message = request.form["message"]
        image = request.form["image"]
        data_manager.edit_question(question_id, title, message, image)
        return redirect("/list/question/" + str(question_id))
    question = data_manager.get_question_by_id(question_id)
    return render_template("edit_question.html", question=question, question_id=question_id)


@app.route("/list/question/<question_id>/answer/<answer_id>/edit", methods=["GET", "POST"])
def edit_answer(question_id, answer_id):
    if request.method == "POST":
        question_id = question_id
        answer_id = answer_id
        message = request.form["message"]
        image = request.form["image"]
        data_manager.edit_answer(answer_id, message, image)
        return redirect("/list/question/" + str(question_id))
    answer = data_manager.get_unique_answer(answer_id)
    return render_template("edit_answer.html", answer=answer, answer_id=answer_id, question_id=question_id)


@app.route("/list/question/<question_id>/comment/<comment_id>/edit", methods=["GET", "POST"])
def edit_comment(question_id, comment_id):
    if request.method == "POST":
        question_id = question_id
        message = request.form["message"]
        data_manager.edit_comment(comment_id, message)
        return redirect("/list/question/" + question_id)
    comment = data_manager.get_unique_comment(comment_id)
    return render_template("edit_comment.html", comment=comment, question_id=question_id, comment_id=comment_id)


@app.route("/list/question/<question_id>/new-tag", methods=['GET', 'POST'])
def add_tag(question_id):
    if request.method == 'POST':
        tag = request.form['tag']
        data_manager.add_new_tag(tag)
        return redirect("/list/question/" + question_id)
    return render_template("add_tags.html", question_id=question_id)


if __name__ == "__main__":
    app.run(
        debug=True,
    )
