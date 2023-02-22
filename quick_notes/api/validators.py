from rest_framework.serializers import ValidationError

def required_field(value):
    if not value:
        raise ValidationError('This is field is required. Fill it in')
    return value