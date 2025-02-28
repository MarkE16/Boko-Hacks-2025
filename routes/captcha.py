from flask import Blueprint, send_file, session, request, jsonify
from io import BytesIO
import random
import string
from utils.captcha import generate_captcha

captcha_bp = Blueprint("captcha", __name__)

@captcha_bp.route("/captcha/generate", methods=["GET"])
def get_captcha():
    """Generate a new illusion-based CAPTCHA image"""
    
    # Generate the captcha image with two illusions
    image, metadata = generate_captcha()
    
    # Store the metadata in the session for verification
    session['captcha_metadata'] = metadata
    
    # Convert the image to bytes for sending
    img_io = BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@captcha_bp.route("/captcha/verify", methods=["POST"])
def verify_captcha():
    """Verify the user's response to the captcha"""
    
    # Get the user's answer (A or B)
    user_answer = request.form.get('captcha_answer', '').upper()
    
    # Get the stored metadata
    metadata = session.get('captcha_metadata')
    
    if not metadata:
        return jsonify({
            'success': False,
            'message': 'Captcha expired. Please try again.'
        })
    
    # Check if the user selected the real illusion
    if user_answer == metadata['real_illusion']:
        # Clear the captcha from the session
        session.pop('captcha_metadata', None)
        
        # Set a flag indicating the captcha was verified
        session['captcha_verified'] = True
        
        return jsonify({
            'success': True,
            'message': 'Captcha verified successfully!'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Incorrect captcha answer. Please try again.'
        })