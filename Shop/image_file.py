from fastapi import UploadFile, HTTPException
import os
from PIL import Image
import uuid
from starlette.concurrency import run_in_threadpool
class ImagesProcessing:
    def __init__(self):
        self.ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
        self.MAXIMUM_PRODUCT_IMAGES_BYTE = 5 * 1024 * 1024
        self.CREATE_FELDER_PRODUCT_IMAGES = "uploads/products" # الخطوة الأولى تحديد المجلدات التي سوف نخزن الصور داخلهم
        self.MAXIMUM_USERS_IMAGE_SIZE_BYTE = 1 * 1024 * 1024
        self.CREATING_USERS_IMAGES = "uploads/users"

    def _compressing_product_images(self, file: UploadFile, file_path):
    
        with Image.open(file.file) as image: # فا هو كائن بالفعل مفتوح في الذاكرة هذا يقللك الجهد file.file نقراء منه عشان هو لايزال نص لم يتم حفظه فا بنفتح file_path  لفتح الملف و القرأة منه ما بنفتح   with Image.open(file.file) as image  نستعمل 
            image.thumbnail((800, 800)) # نضغط الصورة لنقلل حجمها لعرض 800 يكسل برتفاع 800 
            image.save(file_path, optimize=True, quality=85) # تحدد الجوة الصرة 85 ممكن تقول ليه مش 100 العين البشرية لا تفرق بين 85 وال 100 لذا نحن نستغل هذا لتقليل المساحة المستهلكة quality=85 تقوم بعمل مسح إضافي لتبحث عن أكثر الطرق كفاءة لترتيب ألوان البكسلات و ضغطها رياضياً وهذا يقلل بنسبة كبيرة من حجم الصورة وهذهoptimize=True نحفظ الصورة على القرص الصلب و هذه

    async def validation_product_images(self, file: UploadFile):
        if not file:
            return None
        if file.content_type not in self.ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="نوع الملف غير مدعوم")
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > self.MAXIMUM_PRODUCT_IMAGES_BYTE:
            HTTPException(status_code=400, detail="يتجاوز حجم الملف حد 5 ميغابايت")
        os.makedirs(self.CREATE_FELDER_PRODUCT_IMAGES, exist_ok=True) # لتعني انه لو المجلد موجود بالفعل لا ترجع خطأ exist_ok=True الخطوة الثانية انشاء المجلد و اضفنا 
    
        #  (.) وظيفته فصل أسم الملف نصفين عند اخر علامة  splitext هذا 
        #  و نستعمل الأنداكس 1 لستخراج الشق الثاني من اسم الملف الذي هو الأمتداد
        file_extension = os.path.splitext(file.filename)[1]
    
        # uuid.uuid4() مع الأسم العشوائي فريد لكل ملف الجديد الذي تولد file_extension و ندمج امتداد الملف الراجع من  
        unique_file_name = f"{uuid.uuid4()}{file_extension}"
        
        # لدمج المسار المجلدات مع الملف الذي يحمل اسم جديد os.path.join ثما نستعم]ل 
        file_path = os.path.join(self.CREATE_FELDER_PRODUCT_IMAGES, unique_file_name)
        await run_in_threadpool(lambda: self._compressing_product_images(file, file_path))
        return unique_file_name
    def check_presence_image_link(self, image_link):
        if not image_link:
            return None
        else:
            return str(image_link)


    def _compression_users_images(self, file: UploadFile, file_path):
    
        with Image.open(file.file) as image: # فا هو كائن بالفعل مفتوح في الذاكرة هذا يقللك الجهد file.file نقراء منه عشان هو لايزال نص لم يتم حفظه فا بنفتح file_path  لفتح الملف و القرأة منه ما بنفتح   with Image.open(file.file) as image  نستعمل 
            image.thumbnail((800, 800)) # نضغط الصورة لنقلل حجمها لعرض 800 يكسل برتفاع 800 
            image.save(file_path, optimize=True, quality=85) # تحدد الجوة الصرة 85 ممكن تقول ليه مش 100 العين البشرية لا تفرق بين 85 وال 100 لذا نحن نستغل هذا لتقليل المساحة المستهلكة quality=85 تقوم بعمل مسح إضافي لتبحث عن أكثر الطرق كفاءة لترتيب ألوان البكسلات و ضغطها رياضياً وهذا يقلل بنسبة كبيرة من حجم الصورة وهذهoptimize=True نحفظ الصورة على القرص الصلب و هذه

    async def validation_users_images(self, file: UploadFile):
        if not file:
            return None
        if file.content_type not in self.ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="نوع الملف غير مدعوم")
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > self.MAXIMUM_USERS_IMAGE_SIZE_BYTE:
            HTTPException(status_code=400, detail="يتجاوز حجم الملف حد 5 ميغابايت")
        os.makedirs(self.CREATING_USERS_IMAGES, exist_ok=True) # لتعني انه لو المجلد موجود بالفعل لا ترجع خطأ exist_ok=True الخطوة الثانية انشاء المجلد و اضفنا 
    
        #  (.) وظيفته فصل أسم الملف نصفين عند اخر علامة  splitext هذا 
        #  و نستعمل الأنداكس 1 لستخراج الشق الثاني من اسم الملف الذي هو الأمتداد
        file_extension = os.path.splitext(file.filename)[1]
    
        # uuid.uuid4() مع الأسم العشوائي فريد لكل ملف الجديد الذي تولد file_extension و ندمج امتداد الملف الراجع من  
        unique_file_name = f"{uuid.uuid4()}{file_extension}"
        
        # لدمج المسار المجلدات مع الملف الذي يحمل اسم جديد os.path.join ثما نستعم]ل 
        file_path = os.path.join(self.CREATING_USERS_IMAGES, unique_file_name)
        await run_in_threadpool(lambda: self._compression_users_images(file, file_path))
        return unique_file_name



