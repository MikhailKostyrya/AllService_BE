import os
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FileField
from django.forms import FileField as FormFileField
from django.utils.deconstruct import deconstructible
from PIL import Image, ImageFile

def is_svg(file):
    file.seek(0)  # Перемещаем указатель в начало файла
    try:
        header = file.read(100).decode('utf-8', errors='ignore').strip()
        return header.startswith('<svg')
    except UnicodeDecodeError:
        return False
    finally:
        file.seek(0)  # Сбрасываем указатель в начало файла

@deconstructible
class SVGAndImageFieldValidator:
    error_messages = {
        'invalid_image': "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
        'invalid_svg': "Upload a valid SVG file.",
    }

    def __call__(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext == '.svg':
            if not is_svg(value.file):
                raise ValidationError(self.error_messages['invalid_svg'])
        else:
            try:
                Image.open(value.file).verify()
            except (IOError, SyntaxError):
                raise ValidationError(self.error_messages['invalid_image'])

class CustomImageField(FileField):
    default_validators = [SVGAndImageFieldValidator()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.extend(self.default_validators)

    def formfield(self, **kwargs):
        defaults = {'form_class': FormFileField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
