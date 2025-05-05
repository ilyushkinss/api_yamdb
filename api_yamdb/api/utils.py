from random import choices
from string import ascii_uppercase, digits

LENGTH_CONFIRMATION_CODE = 6


def generate_and_save_confirmation_codes(user):
    confirmation_code = ''.join(
        choices(ascii_uppercase + digits, k=LENGTH_CONFIRMATION_CODE)
    )
    user.confirmation_code = confirmation_code
    user.save()
    return confirmation_code


def check_confirmation_code(user, confirmation_code):
    return confirmation_code == user.confirmation_code
