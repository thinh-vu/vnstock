from .utils import get_cwd

import pytesseract
try:
    from PIL import Image
except ImportError:
    import Image

def image_ocr (image_path, lang='vie', output_path='', file_name='string_from_image.txt'):
    output = pytesseract.image_to_string(Image.open(image_path), lang=lang)
    # if output_path equal to '', save to the current directory, else save to the output_path
    if output_path == '':
        current_dir = get_cwd()
        path = os.path.join(current_dir + file_name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Saved file to the path: {current_dir}\{file_name}')
    else:
        # validate the output_path
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f'Directory doesn\'t exist. Created new directory: {output_path}')
        path = os.path.join(output_path + file_name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(output)
    return output
