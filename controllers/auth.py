from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import functools

from app import db
from models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    """View decorator that ensures user is admin."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or not g.user.is_admin:
            flash('Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if g.user:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob_str = request.form['dob']
        
        error = None
        
        # Validate form inputs
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not full_name:
            error = 'Full name is required.'
        elif not qualification:
            error = 'Qualification is required.'
        elif not dob_str:
            error = 'Date of birth is required.'
        
        try:
            # Convert string date to Python date object
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            error = 'Invalid date format. Please use YYYY-MM-DD.'
            
        # Check if email already exists
        if error is None:
            if User.query.filter_by(email=email).first() is not None:
                error = f"Email {email} is already registered."
        
        # Create new user if no errors
        if error is None:
            new_user = User(
                email=email,
                password=generate_password_hash(password),
                full_name=full_name,
                qualification=qualification,
                date_of_birth=dob,
                is_admin=False
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        flash(error, 'danger')
    
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        
        # Validate form inputs
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
            
        # Check if user exists and password is correct
        if error is None:
            user = User.query.filter_by(email=email).first()
            if user is None:
                error = 'Incorrect email.'
            elif not check_password_hash(user.password, password):
                error = 'Incorrect password.'
        
        # Log in user if no errors
        if error is None:
            session.clear()
            session['user_id'] = user.id
            session.permanent = True
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
                
        flash(error, 'danger')
    
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
