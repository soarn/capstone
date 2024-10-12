from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash
from db.db_models import User, db
from flask_login import login_required, current_user

# Create a blueprint for profile-related routes
profile = Blueprint('profile', __name__)

# Route to display the profile page
@profile.route('/profile')
@login_required  # Ensure user is logged in
def profile_page():
    return render_template('profile.html', user=current_user)

# Route to update account settings
@profile.route('/profile/update-account', methods=['POST'])
@login_required
def update_account_settings():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    # Update the current user's username and email
    current_user.username = username
    current_user.email = email

    # If the user provided a new password, hash it and update the user's password
    if password:
        current_user.password_hash = generate_password_hash(password)

    db.session.commit()
    flash("Account settings updated successfully!", "success")
    return redirect(url_for('profile.profile_page'))

# Route to update theme settings
@profile.route('/profile/update-theme', methods=['POST'])
@login_required
def update_theme_settings():
    theme = request.form['theme']

    # Store the selected theme in the session
    session['bootswatch_theme'] = theme

    # Optionally, you can save the user's theme preference to the database
    current_user.theme = theme
    db.session.commit()

    flash("Theme updated successfully!", "success")
    return redirect(url_for('profile.profile_page'))

# Route to update privacy settings
@profile.route('/profile/update-privacy', methods=['POST'])
@login_required
def update_privacy_settings():
    data_sharing = 'data_sharing' in request.form

    # Update user's privacy settings in the database
    current_user.data_sharing = data_sharing
    db.session.commit()

    flash("Privacy settings updated successfully!", "success")
    return redirect(url_for('profile.profile_page'))

# Route to update notification settings
@profile.route('/profile/update-notifications', methods=['POST'])
@login_required
def update_notification_settings():
    email_notifications = 'email_notifications' in request.form

    # Update user's notification settings in the database
    current_user.notifications = email_notifications
    db.session.commit()

    flash("Notification settings updated successfully!", "success")
    return redirect(url_for('profile.profile_page'))
