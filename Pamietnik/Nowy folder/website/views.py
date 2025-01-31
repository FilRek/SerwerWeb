from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Note
from . import db
import os
import datetime

views = Blueprint('views', __name__)

IMAGE_UPLOAD_FOLDER = 'website/static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/')
@login_required
def home():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", user=current_user)

@views.route('/note/<int:note_id>')
@login_required
def view_note(note_id):
    note = Note.query.get(note_id)
    if not note or note.user_id != current_user.id:
        flash("Note not found.", category="error")
        return redirect(url_for('views.home'))
    return render_template("view_note.html", note=note, user=current_user)

@views.route('/create-note', methods=['GET', 'POST'])
@login_required
def create_note():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')

        if not title:
            flash('Title is required!', category='error')
            return redirect(url_for('views.create_note'))

        image_filename = None
        if image:
            if image and allowed_file(image.filename):
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(IMAGE_UPLOAD_FOLDER, image_filename))
            else:
                flash('Invalid image format. Please upload a PNG, JPG, or JPEG file.', category='error')
                return redirect(url_for('views.create_note'))

        new_note = Note(
            title=title,
            data=content,
            image_file=image_filename,
            date=datetime.datetime.now(),
            user_id=current_user.id
        )
        db.session.add(new_note)
        db.session.commit()
        flash('Note created!', category='success')
        return redirect(url_for('views.home'))

    return render_template("create_note.html", user=current_user)

@views.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get(note_id)
    if not note or note.user_id != current_user.id:
        flash("Note not found or you're not the owner.", category="error")
        return redirect(url_for('views.home'))

    if note.image_file:
        other_notes = Note.query.filter(Note.image_file == note.image_file).all()
        if len(other_notes) == 1:
            image_path = os.path.join(IMAGE_UPLOAD_FOLDER, note.image_file)
            if os.path.exists(image_path):
                os.remove(image_path)

    db.session.delete(note)
    db.session.commit()
    flash('Note deleted!', category='success')
    return redirect(url_for('views.home'))

@views.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get(note_id)
    if not note or note.user_id != current_user.id:
        flash("Note not found or you're not the owner.", category="error")
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')

        if not title:
            flash('Title is required!', category='error')
            return redirect(url_for('views.edit_note', note_id=note.id))


        image_filename = note.image_file
        if image:

            if allowed_file(image.filename):
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(IMAGE_UPLOAD_FOLDER, image_filename))
            else:
                flash('Invalid image format. Please upload a PNG, JPG, or JPEG file.', category='error')
                return redirect(url_for('views.edit_note', note_id=note.id))

        note.title = title
        note.data = content
        note.image_file = image_filename
        note.date = datetime.datetime.now()

        db.session.commit()
        flash('Note updated!', category='success')
        return redirect(url_for('views.home'))

    return render_template("edit_note.html", note=note, user=current_user)