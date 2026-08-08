# API نستدعي أطار العمل الذي سوف يمكننا من بناء  
# يستلم هذه النصوص المبعثرة القادمة على هيأت ملف و يعزلها عن الملفات القادمة و يجمعها From  لا يفهم النصوصو المبعثرة القادمة على هيأت ملفات فا وظيفة  pydantic يتوقع ان المدخل ملفات و وليس جوسن و انت ادخلت مع الملفات نصوص فا  api هي ان في حالة كان ال  From وظيفة ال 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# نستورد ملف قاعدة البيانات التي أنشأنا بها جدول المستخدمين
from routers.database.database import init_db
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from routers.auth import router as recording_router
from routers.products import router as products_router
from routers.users import router as users_router
from routers.general import router as general_router
from create_image_files import profile_photo_folder
profile_photo_folder()
@asynccontextmanager # وظيفة هذا الديكريتر التحكم في تشغيل
async def lifespan(app: FastAPI):

    await init_db()
    yield
    
# API بناء ال 
app = FastAPI(lifespan=lifespan)
# API كود فتح صلاحيات الأتصال لصفحات  في 
# لأسباب أمنية بستخدام هذا الكود نحن نعطي صلاحيات الأتصال Backend مع  Frontend المتصفحات تمنع اي عملية اتصال لصفحات 
app.add_middleware(
    CORSMiddleware, # لتخطي المنع CORنستخدم 
    allow_origins = ["*"], # API نعطي صلاحيات الأتصال لي اي صفحة تحاول الاتصال في 
    allow_methods = ["*"], # إلخ post او get يعني هذا السطر اسمح بكل أنواع الطلبات
    allow_headers = ["*"] # يعني هذا السطر اسمح بأرسال اي نوع من البيانات في رأس الطلب

    )
# بختصار هي جسر وظيفتها ان تقول للسيرفر اي طلب يأتي على الرابط كاذا لا تبحث عن دالة برمجية بالاذهب للقرص الصلب و احظر الملف من مجلد كذا  mount وظيفة 
#  "/static" تعني اننا نضع للرابط كا كل اسم لأستدعائه لو تغير اسم المسار على سبيل المثال هذا  name="static" و بناء على تكملة اسم المسار بتاع مجلد الأبن و أسم الملف اذهب للقرص الصلب و ادخل للملف و هاتو هذه "uploads" هذه تعني عندما ترى اسم المسار دا في الرابط استبدله و ضع بداله اسم المجلد الأب هذا  "/static" تعال نفصص محتوايات هذا الأمر  
# هي ليسة مجرد امر بسيط فيهي تقوم بثلاثة اشياء هي الأمان لو حاول مستخدم خبيث كتابة مسار خبيث للوصول لملفات النظام تمنعه هي تتعرف تلقائي هل هذا ملف او صورة او فيديو تضع علامة للمتصفح ليحفظ الصورة StaticFiles وظيفة ال 
app.mount("/static", StaticFiles(directory="uploads"), name="static")

app.include_router(recording_router)
app.include_router(products_router)
app.include_router(users_router)
app.include_router(general_router)
