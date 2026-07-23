from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Hash user state so token invalidates once is_verified changes
        return f"{user.pk}{timestamp}{user.is_verified}"

account_activation_token = EmailVerificationTokenGenerator()