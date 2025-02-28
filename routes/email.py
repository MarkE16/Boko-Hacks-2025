from flask import Blueprint, render_template, request, jsonify, session, send_file
from extensions import db
from models.user import User
from models.email import Email
from werkzeug.utils import secure_filename

email_bp = Blueprint('email', __name__, url_prefix='/apps/email')

@email_bp.route('/')
def email():
  if 'user' not in session:
    return jsonify({'success': False, 'error': 'Not logged in'}), 401

  current_user = User.query.filter_by(username=session['user']).first()
  if not current_user:
    return jsonify({'success': False, 'error': 'User not found'}), 404

  all_emails = Email.query.filter_by(recipient=current_user.username).all()

  return render_template('email.html', emails=all_emails, current_user_id=current_user.id)

@email_bp.route('/send', methods=['POST'])
def send_email():
  if 'user' not in session:
    return jsonify({'success': False, 'error': 'Not logged in'}), 401

  current_user = User.query.filter_by(username=session['user']).first()
  if not current_user:
    return jsonify({'success': False, 'error': 'User not found'}), 404

  data = request.get_json()
  subject = data.get('subject')
  recipient = data.get('recipient')
  body = data.get('body')


  new_email = Email(subject=subject, recipient=recipient, sender=current_user.username, body=body)
  db.session.add(new_email)
  db.session.commit()

  return jsonify({'success': True, 'message': 'Email sent successfully'})
