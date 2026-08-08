from pathlib import Path # نستدعي المكتبة الحديثة للتعامل مع الملفات 

def delete_images_user(image_path):
    if not image_path:
        return None

    
    file_path = Path.cwd() / "uploads" / "users" / image_path # احظار مسار المجلدات التي فيها مجلد المشروع و علامة الشرطة المائلة هذه هنا ليست قسمة بالطريقة فصل بين اسماء المسارات سواء ويندز او لنكس cwd() وظيفة دالة 
    if file_path.is_file(): # للتحقق من وجود الملف و نضع شرط التحقق is_file تستعل دالة 
        file_path.unlink() # لحذف الملفات  فا نحذف الملف بشكل نهائي لو كان موجودunlink تستعمل 
        return True
    return None
def delete_images_product(image_path):
    if not image_path:
        return None
    file_path = Path.cwd() / "uploads" / "products" / image_path # احظار مسار المجلدات التي فيها مجلد المشروع و علامة الشرطة المائلة هذه هنا ليست قسمة بالطريقة فصل بين اسماء المسارات سواء ويندز او لنكس cwd() وظيفة دالة 
    if file_path.is_file(): # للتحقق من وجود الملف و نضع شرط التحقق is_file تستعل دالة 
        file_path.unlink() # لحذف الملفات  فا نحذف الملف بشكل نهائي لو كان موجودunlink تستعمل 
        return True
    return None