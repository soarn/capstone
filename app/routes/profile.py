from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash
from db.db_models import User, db
from flask_login import login_required, current_user
from utils import fetch_bootswatch_themes
from forms import UpdateProfileForm

# Create a blueprint for profile-related routes
profile = Blueprint('profile', __name__)

# Route to display the profile page
@profile.route('/profile', methods=['GET', 'POST'])
@login_required  # Ensure user is logged in
def profile_page():
    # Fetch Bootswatch themes
    themes = fetch_bootswatch_themes()

    # Ensure 'themes' is a list of dictionaries with 'name' keys
    if not themes or not all(isinstance(theme, dict) and 'name' in theme for theme in  themes):
        flash("Unable to fetch Bootswatch themes. Please try again later.", "danger")
        themes = [{'name': 'default'}]

    form = UpdateProfileForm(obj=current_user)
    form.data_sharing.default = current_user.data_sharing
    form.notifications.default = current_user.notifications
    form.confetti_enabled.default = current_user.confetti_enabled
    form.theme.choices = [(theme['name'], f"{theme['name']} - {theme.get('description', 'No description')}") for theme in themes]
    form.pagination.default = current_user.pagination

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        current_user.theme = form.theme.data
        current_user.pagination = form.pagination.data
        current_user.notifications = form.notifications.data
        current_user.data_sharing = form.data_sharing.data
        current_user.confetti_enabled = form.confetti_enabled.data

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile.profile_page'))
    
    return render_template('profile.html', user=current_user, themes=themes, form=form)