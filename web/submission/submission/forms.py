from flask_security.forms import RegisterForm
from flask_wtf import Form  
from wtforms import StringField
from wtforms.validators import DataRequired

from submission.models import User

class ExtendedRegisterForm(RegisterForm):
    username = StringField('Username', [DataRequired()])
    firstname = StringField('First Name', [DataRequired()])
    lastname = StringField('Last Name', [DataRequired()])

    def validate(self):
        validation = Form.validate(self)
        if not validation:
            return False

        # Check if username already exists       
        user = User.query.filter_by(
            username=self.username.data).first()
        if user is not None:
            self.username.errors.append('Username already exists')
            return False

        return True	
