from django.core.exceptions import ValidationError

def validated_file_size(file):
    max_size_kb = 50
    if file.size > max_size_kb * 1024:
        raise ValidationError(f'File can not be larger than {max_size_kb} kb')