from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session
)
from datetime import datetime
from sqlalchemy import func, desc

from app import db
from models import Subject, Chapter, Quiz, Question, Score, UserAnswer
from controllers.auth import login_required

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/dashboard')
@login_required
def dashboard():
    # Get upcoming quizzes (not attempted by user)
    today = datetime.today().date()
    
    # Get quizzes attempted by user
    attempted_quiz_ids = db.session.query(Score.quiz_id).filter_by(user_id=g.user.id).all()
    attempted_quiz_ids = [row[0] for row in attempted_quiz_ids]
    
    # Get upcoming quizzes not attempted by the user
    upcoming_quizzes = Quiz.query.filter(
        Quiz.date_of_quiz >= today,
        ~Quiz.id.in_(attempted_quiz_ids) if attempted_quiz_ids else True
    ).order_by(Quiz.date_of_quiz).all()
    
    # Enhance quiz objects with chapter and subject info
    for quiz in upcoming_quizzes:
        quiz.chapter_name = quiz.chapter.name
        quiz.subject_name = quiz.chapter.subject.name
    
    return render_template('user/dashboard.html', upcoming_quizzes=upcoming_quizzes)


@bp.route('/quiz/<int:quiz_id>/start')
@login_required
def start_quiz(quiz_id):
    # Check if user has already attempted this quiz
    existing_score = Score.query.filter_by(user_id=g.user.id, quiz_id=quiz_id).first()
    if existing_score:
        flash('You have already attempted this quiz.', 'warning')
        return redirect(url_for('user.dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if quiz has questions
    questions_count = Question.query.filter_by(quiz_id=quiz_id).count()
    if questions_count == 0:
        flash('This quiz does not have any questions yet.', 'warning')
        return redirect(url_for('user.dashboard'))
    
    # Store quiz start time in session
    session['quiz_start_time'] = datetime.now().timestamp()
    session['quiz_id'] = quiz_id
    
    return redirect(url_for('user.take_quiz', quiz_id=quiz_id, question_index=0))


@bp.route('/quiz/<int:quiz_id>/question/<int:question_index>', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id, question_index):
    # Validate quiz_id and session data
    if 'quiz_start_time' not in session or session['quiz_id'] != quiz_id:
        flash('Quiz session not found or expired. Please start again.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        flash('No questions found for this quiz.', 'warning')
        return redirect(url_for('user.dashboard'))
    
    # Validate question index
    if question_index < 0 or question_index >= len(questions):
        flash('Invalid question index.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    current_question = questions[question_index]
    
    # Calculate remaining time
    start_time = session.get('quiz_start_time', 0)
    elapsed_seconds = int(datetime.now().timestamp() - start_time)
    total_seconds = quiz.time_duration * 60
    remaining_seconds = max(0, total_seconds - elapsed_seconds)
    
    # Check if time is up
    if remaining_seconds <= 0:
        return finish_quiz(quiz_id)
    
    # Process answer submission
    if request.method == 'POST':
        selected_option = request.form.get('option')
        
        if selected_option:
            # Save user's answer
            is_correct = selected_option == current_question.correct_option
            
            # Check if answer already exists and update it
            existing_answer = UserAnswer.query.filter_by(
                user_id=g.user.id,
                question_id=current_question.id,
                quiz_id=quiz_id
            ).first()
            
            if existing_answer:
                existing_answer.selected_option = selected_option
                existing_answer.is_correct = is_correct
            else:
                user_answer = UserAnswer(
                    user_id=g.user.id,
                    question_id=current_question.id,
                    quiz_id=quiz_id,
                    selected_option=selected_option,
                    is_correct=is_correct
                )
                db.session.add(user_answer)
            
            db.session.commit()
        
        # Check if this is the last question or if user wants to submit
        if question_index == len(questions) - 1 or 'submit_quiz' in request.form:
            return finish_quiz(quiz_id)
        
        # Go to next question
        return redirect(url_for('user.take_quiz', quiz_id=quiz_id, question_index=question_index + 1))
    
    # Get user's previous answer for this question if exists
    user_answer = UserAnswer.query.filter_by(
        user_id=g.user.id,
        question_id=current_question.id,
        quiz_id=quiz_id
    ).first()
    
    selected_option = user_answer.selected_option if user_answer else None
    
    return render_template('user/quiz.html', 
                           quiz=quiz,
                           question=current_question,
                           question_index=question_index,
                           total_questions=len(questions),
                           remaining_seconds=remaining_seconds,
                           selected_option=selected_option)


def finish_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Calculate score
    user_answers = UserAnswer.query.filter_by(user_id=g.user.id, quiz_id=quiz_id).all()
    correct_answers = sum(1 for answer in user_answers if answer.is_correct)
    
    # Calculate time taken
    start_time = session.get('quiz_start_time', 0)
    time_taken = int(datetime.now().timestamp() - start_time)
    
    # Save score
    score = Score(
        user_id=g.user.id,
        quiz_id=quiz_id,
        score=correct_answers,
        total_questions=len(questions),
        time_taken=time_taken,
        attempt_date=datetime.now()
    )
    db.session.add(score)
    db.session.commit()
    
    # Clear quiz session data
    session.pop('quiz_start_time', None)
    session.pop('quiz_id', None)
    
    flash('Quiz completed successfully!', 'success')
    return redirect(url_for('user.quiz_result', score_id=score.id))


@bp.route('/quiz/result/<int:score_id>')
@login_required
def quiz_result(score_id):
    score = Score.query.get_or_404(score_id)
    
    # Check if this score belongs to the current user
    if score.user_id != g.user.id:
        flash('You do not have access to this result.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    quiz = Quiz.query.get(score.quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    
    # Format time taken
    minutes, seconds = divmod(score.time_taken, 60)
    time_taken_formatted = f"{minutes}m {seconds}s"
    
    return render_template('user/quiz_result.html', 
                           score=score,
                           quiz=quiz,
                           chapter=chapter,
                           subject=subject,
                           time_taken=time_taken_formatted)


@bp.route('/scores')
@login_required
def scores():
    user_scores = Score.query.filter_by(user_id=g.user.id).order_by(Score.attempt_date.desc()).all()
    
    # Enhance score objects with quiz, chapter, and subject info
    for score in user_scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        
        score.quiz_name = quiz.name
        score.chapter_name = chapter.name
        score.subject_name = subject.name
        
        # Calculate percentage
        score.percentage = (score.score / score.total_questions) * 100 if score.total_questions > 0 else 0
        
        # Format time taken
        minutes, seconds = divmod(score.time_taken, 60)
        score.time_taken_formatted = f"{minutes}m {seconds}s"
    
    return render_template('user/scores.html', scores=user_scores)


@bp.route('/summary')
@login_required
def summary():
    return render_template('user/summary.html')


@bp.route('/api/chart/subject-scores')
@login_required
def subject_scores():
    # Get user's average scores by subject
    query = db.session.query(
        Subject.name,
        func.avg(Score.score * 100.0 / Score.total_questions).label('avg_score')
    ).join(Chapter, Subject.id == Chapter.subject_id)\
     .join(Quiz, Chapter.id == Quiz.chapter_id)\
     .join(Score, Quiz.id == Score.quiz_id)\
     .filter(Score.user_id == g.user.id)\
     .group_by(Subject.id)\
     .all()
    
    labels = [row[0] for row in query]
    data = [float(row[1]) for row in query]
    
    return jsonify({
        'labels': labels,
        'data': data
    })


@bp.route('/api/chart/quiz-attempts')
@login_required
def quiz_attempts():
    # Get count of quizzes attempted by subject
    query = db.session.query(
        Subject.name,
        func.count(Score.id).label('attempt_count')
    ).join(Chapter, Subject.id == Chapter.subject_id)\
     .join(Quiz, Chapter.id == Quiz.chapter_id)\
     .join(Score, Quiz.id == Score.quiz_id)\
     .filter(Score.user_id == g.user.id)\
     .group_by(Subject.id)\
     .all()
    
    labels = [row[0] for row in query]
    data = [row[1] for row in query]
    
    return jsonify({
        'labels': labels,
        'data': data
    })
