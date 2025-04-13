from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from datetime import datetime
from sqlalchemy import func

from app import db
from models import Subject, Chapter, Quiz, Question, User, Score
from controllers.auth import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/dashboard')
@admin_required
def dashboard():
    # Count statistics for dashboard
    subject_count = Subject.query.count()
    chapter_count = Chapter.query.count()
    quiz_count = Quiz.query.count()
    user_count = User.query.filter_by(is_admin=False).count()
    
    # Get subjects for subject list
    subjects = Subject.query.order_by(Subject.created_at.desc()).all()
    
    return render_template('admin/dashboard.html', 
                           subject_count=subject_count, 
                           chapter_count=chapter_count, 
                           quiz_count=quiz_count, 
                           user_count=user_count,
                           subjects=subjects)


# Subject management
@bp.route('/subjects', methods=['GET', 'POST'])
@admin_required
def subjects():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        if not name:
            flash('Subject name is required.', 'danger')
        else:
            subject = Subject(name=name, description=description)
            db.session.add(subject)
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin.subjects'))
    
    # Get all subjects
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin/subjects.html', subjects=subjects)


@bp.route('/subjects/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        if not name:
            flash('Subject name is required.', 'danger')
        else:
            subject.name = name
            subject.description = description
            db.session.commit()
            flash('Subject updated successfully!', 'success')
            return redirect(url_for('admin.subjects'))
    
    return render_template('admin/subjects.html', 
                           edit_subject=subject,
                           subjects=Subject.query.order_by(Subject.name).all())


@bp.route('/subjects/<int:id>/delete', methods=['POST'])
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin.subjects'))


# Chapter management
@bp.route('/subjects/<int:subject_id>/chapters', methods=['GET', 'POST'])
@admin_required
def chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        if not name:
            flash('Chapter name is required.', 'danger')
        else:
            chapter = Chapter(name=name, description=description, subject_id=subject_id)
            db.session.add(chapter)
            db.session.commit()
            flash('Chapter added successfully!', 'success')
            return redirect(url_for('admin.chapters', subject_id=subject_id))
    
    chapters = Chapter.query.filter_by(subject_id=subject_id).order_by(Chapter.name).all()
    return render_template('admin/chapters.html', subject=subject, chapters=chapters)


@bp.route('/chapters/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        if not name:
            flash('Chapter name is required.', 'danger')
        else:
            chapter.name = name
            chapter.description = description
            db.session.commit()
            flash('Chapter updated successfully!', 'success')
            return redirect(url_for('admin.chapters', subject_id=chapter.subject_id))
    
    return render_template('admin/chapters.html', 
                           subject=chapter.subject,
                           edit_chapter=chapter,
                           chapters=Chapter.query.filter_by(subject_id=chapter.subject_id).order_by(Chapter.name).all())


@bp.route('/chapters/<int:id>/delete', methods=['POST'])
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('admin.chapters', subject_id=subject_id))


# Quiz management
@bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET', 'POST'])
@admin_required
def quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        name = request.form['name']
        date_str = request.form['date_of_quiz']
        duration = request.form['time_duration']
        
        error = None
        if not name:
            error = 'Quiz name is required.'
        elif not date_str:
            error = 'Quiz date is required.'
        elif not duration:
            error = 'Quiz duration is required.'
            
        try:
            date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d').date()
            duration_minutes = int(duration)
        except ValueError:
            error = 'Invalid date format or duration.'
        
        if error is None:
            quiz = Quiz(
                name=name,
                chapter_id=chapter_id,
                date_of_quiz=date_of_quiz,
                time_duration=duration_minutes
            )
            db.session.add(quiz)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('admin.quizzes', chapter_id=chapter_id))
        else:
            flash(error, 'danger')
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).order_by(Quiz.date_of_quiz).all()
    return render_template('admin/quizzes.html', chapter=chapter, quizzes=quizzes)


@bp.route('/quizzes/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        date_str = request.form['date_of_quiz']
        duration = request.form['time_duration']
        
        error = None
        if not name:
            error = 'Quiz name is required.'
        elif not date_str:
            error = 'Quiz date is required.'
        elif not duration:
            error = 'Quiz duration is required.'
            
        try:
            date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d').date()
            duration_minutes = int(duration)
        except ValueError:
            error = 'Invalid date format or duration.'
        
        if error is None:
            quiz.name = name
            quiz.date_of_quiz = date_of_quiz
            quiz.time_duration = duration_minutes
            db.session.commit()
            flash('Quiz updated successfully!', 'success')
            return redirect(url_for('admin.quizzes', chapter_id=quiz.chapter_id))
        else:
            flash(error, 'danger')
    
    return render_template('admin/quizzes.html', 
                           chapter=quiz.chapter,
                           edit_quiz=quiz,
                           quizzes=Quiz.query.filter_by(chapter_id=quiz.chapter_id).order_by(Quiz.date_of_quiz).all())


@bp.route('/quizzes/<int:id>/delete', methods=['POST'])
@admin_required
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    chapter_id = quiz.chapter_id
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.quizzes', chapter_id=chapter_id))


# Question management
@bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET', 'POST'])
@admin_required
def questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_option = request.form['correct_option']
        
        error = None
        if not question_statement:
            error = 'Question statement is required.'
        elif not option_a or not option_b or not option_c or not option_d:
            error = 'All options are required.'
        elif correct_option not in ['A', 'B', 'C', 'D']:
            error = 'Please select a valid correct option.'
        
        if error is None:
            question = Question(
                quiz_id=quiz_id,
                question_statement=question_statement,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option
            )
            db.session.add(question)
            db.session.commit()
            flash('Question added successfully!', 'success')
            return redirect(url_for('admin.questions', quiz_id=quiz_id))
        else:
            flash(error, 'danger')
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin/questions.html', quiz=quiz, questions=questions)


@bp.route('/questions/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_question(id):
    question = Question.query.get_or_404(id)
    
    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_option = request.form['correct_option']
        
        error = None
        if not question_statement:
            error = 'Question statement is required.'
        elif not option_a or not option_b or not option_c or not option_d:
            error = 'All options are required.'
        elif correct_option not in ['A', 'B', 'C', 'D']:
            error = 'Please select a valid correct option.'
        
        if error is None:
            question.question_statement = question_statement
            question.option_a = option_a
            question.option_b = option_b
            question.option_c = option_c
            question.option_d = option_d
            question.correct_option = correct_option
            db.session.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('admin.questions', quiz_id=question.quiz_id))
        else:
            flash(error, 'danger')
    
    return render_template('admin/questions.html', 
                           quiz=question.quiz,
                           edit_question=question,
                           questions=Question.query.filter_by(quiz_id=question.quiz_id).all())


@bp.route('/questions/<int:id>/delete', methods=['POST'])
@admin_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.questions', quiz_id=quiz_id))


# Summary charts
@bp.route('/summary')
@admin_required
def summary():
    return render_template('admin/summary.html')


@bp.route('/api/chart/subject-quiz-count')
@admin_required
def subject_quiz_count():
    try:
        # Get subject quiz counts for chart
        query = db.session.query(
            Subject.name.label('subject_name'),
            func.count(Quiz.id).label('quiz_count')
        ).select_from(Subject).join(Chapter, Subject.id == Chapter.subject_id) \
         .join(Quiz, Chapter.id == Quiz.chapter_id) \
         .group_by(Subject.id).all()
        
        labels = [row.subject_name for row in query]
        data = [row.quiz_count for row in query]
        
        # If no data, provide default empty response
        if not labels:
            return jsonify({
                'labels': [],
                'data': []
            })
        
        return jsonify({
            'labels': labels,
            'data': data
        })
    except Exception as e:
        app.logger.error(f"Error in subject_quiz_count: {str(e)}")
        return jsonify({
            'labels': [],
            'data': [],
            'error': str(e)
        }), 500


@bp.route('/api/chart/subject-user-count')
@admin_required
def subject_user_count():
    try:
        # Get subject user attempt counts for chart
        query = db.session.query(
            Subject.name.label('subject_name'),
            func.count(distinct(Score.user_id)).label('user_count')
        ).select_from(Subject).join(Chapter, Subject.id == Chapter.subject_id) \
         .join(Quiz, Chapter.id == Quiz.chapter_id) \
         .join(Score, Quiz.id == Score.quiz_id) \
         .group_by(Subject.id).all()
        
        labels = [row.subject_name for row in query]
        data = [row.user_count for row in query]
        
        # If no data, provide default empty response
        if not labels:
            return jsonify({
                'labels': [],
                'data': []
            })
        
        return jsonify({
            'labels': labels,
            'data': data
        })
    except Exception as e:
        app.logger.error(f"Error in subject_user_count: {str(e)}")
        return jsonify({
            'labels': [],
            'data': [],
            'error': str(e)
        }), 500
