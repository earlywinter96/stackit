from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from app.extensions import db
from app.models import User, Question, Answer, Tag, Notification
import re

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    query = request.args.get('q', '').strip().lower()
    questions = Question.query
    tags = Tag.query.order_by(Tag.name).all()

    if query:
        questions = questions.filter(
            db.or_(
                Question.title.ilike(f"%{query}%"),
                Question.description.ilike(f"%{query}%"),
                Question.tags.any(Tag.name.ilike(f"%{query}%"))
            )
        )

    questions = questions.order_by(Question.timestamp.desc()).all()
    return render_template('index.html', questions=questions, all_tags=tags, Answer=Answer)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('main.register'))

        hashed_pw = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid credentials.')
        return redirect(url_for('main.login'))

    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))

@bp.route('/ask', methods=['GET', 'POST'])
@login_required
def ask_question():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tags_input = request.form.get('tags', '')

        tags = []
        if tags_input:
            tag_names = [t.strip().lower() for t in tags_input.split(',')]
            for name in tag_names:
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    tag = Tag(name=name)
                    db.session.add(tag)
                tags.append(tag)

        question = Question(
            title=title,
            description=description,
            author=current_user,
            timestamp=datetime.utcnow(),
            tags=tags
        )

        db.session.add(question)
        db.session.commit()
        flash('Your question has been posted!')
        return redirect(url_for('main.index'))

    return render_template('ask.html')

@bp.route('/questions')
def list_questions():
    questions = Question.query.order_by(Question.timestamp.desc()).all()
    return render_template('questions.html', questions=questions, Answer=Answer)

@bp.route('/questions/<int:question_id>', methods=['GET', 'POST'])
def view_question(question_id):
    question = Question.query.get_or_404(question_id)
    answers = question.answers.order_by(Answer.timestamp.desc()).all()

    if request.method == 'POST':
        content = request.form['content']
        answer = Answer(content=content, author=current_user, question=question)
        db.session.add(answer)

        mentioned_usernames = re.findall(r'@(\w+)', content)
        for uname in mentioned_usernames:
            mentioned_user = User.query.filter_by(username=uname).first()
            if mentioned_user and mentioned_user.id != current_user.id:
                mention_note = Notification(
                    message=f"You were mentioned in an answer by @{current_user.username}",
                    recipient=mentioned_user
                )
                db.session.add(mention_note)

        if current_user.is_authenticated and question.author.id != current_user.id:
            new_notification = Notification(
                message=f"{current_user.username} answered your question: {question.title}",
                recipient=question.author
            )
            db.session.add(new_notification)

        db.session.commit()
        flash('Your answer has been posted!')
        return redirect(url_for('main.view_question', question_id=question.id))

    return render_template('view_question.html', question=question, answers=answers)

@bp.route('/answers/<int:answer_id>/accept', methods=['POST'])
@login_required
def accept_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question = answer.question

    if current_user.id != question.author.id:
        flash('Only the question author can accept an answer.')
        return redirect(url_for('main.view_question', question_id=question.id))

    for ans in question.answers:
        ans.is_accepted = False

    answer.is_accepted = True
    db.session.commit()
    flash('Answer accepted successfully.')
    return redirect(url_for('main.view_question', question_id=question.id))

# Admin route protection
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ADMIN':
            flash('Admin access required.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    questions = Question.query.order_by(Question.timestamp.desc()).all()
    answers = Answer.query.order_by(Answer.timestamp.desc()).all()
    return render_template('admin_dashboard.html', users=users, questions=questions, answers=answers)

@bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_question(question_id):
    q = Question.query.get_or_404(question_id)
    db.session.delete(q)
    db.session.commit()
    flash('Question deleted.')
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/answers/<int:answer_id>/vote/<string:action>', methods=['POST'])
@login_required
def vote_answer(answer_id, action):
    answer = Answer.query.get_or_404(answer_id)

    if action == 'up':
        answer.upvotes += 1
    elif action == 'down':
        answer.downvotes += 1
    else:
        flash("Invalid vote action.")
        return redirect(url_for('main.view_question', question_id=answer.question.id))

    db.session.commit()
    return redirect(url_for('main.view_question', question_id=answer.question.id))

@bp.route('/notifications')
@login_required
def notifications():
    notes = current_user.notifications.order_by(Notification.timestamp.desc()).all()

    for n in notes:
        n.is_read = True
    db.session.commit()

    return render_template('notifications.html', notifications=notes)

@bp.route('/home')
def home():
    questions = Question.query.order_by(Question.timestamp.desc()).all()
    return render_template('index.html', questions=questions, Answer=Answer)
