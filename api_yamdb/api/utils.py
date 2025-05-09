from django.contrib.auth.tokens import default_token_generator


def generate_and_save_confirmation_codes(user):
    return default_token_generator.make_token(user)
