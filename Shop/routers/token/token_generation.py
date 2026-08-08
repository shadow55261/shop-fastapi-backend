import jwt
from sealed_head import SECRET_SEAL
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from logging_info import log_message
from routers.database.database_token import user_id_admin
def token_creation(payload):
    expire =  datetime.now(timezone.utc) +  timedelta(hours=2)
    payload["exp"] = expire

    token = jwt.encode(payload, SECRET_SEAL, "HS256") # أنشاء التوكن لنمرر لدالة أنشاء التوكن معلومات المستخدم و وقت صلاحية التوكن أنتهاء التوكن كا قاموس و نمرر الكتم الخاص بسيرفر و تقنية التشفير المستخدمة
    return token 
def http_error():
   return HTTPException(status.HTTP_401_UNAUTHORIZED, "نعتذر تعذر التحقق من صحة البيانات", {"WWW-Authenticate": "Bearer"})

token_scheme = HTTPBearer() # هذه التقنية و ظيفتها فصل التوكن القادم مع الطلب عن الطلب
# token وهذا ما يسهل عليك أدارة انواع اخرى من  credentials و الشق الثاني الذي هو التوكن يضعها في خاصية اخرى تسمى  scheme يضعها في خاصية تسمى  Bearer تقريباً هذا الكائن يضمن ادارة البيانات التوكن القادمة بهذا الشكل بذكاء فا يخزن الشق الأول منها المسمى  Bearer <token هو كائن ذكي عندما يتم فصل التوكن عن الطلب تعود لك البيانات هكذا  HTTPAuthorizationCredentials هذا 
def verify_token(token: HTTPAuthorizationCredentials = Depends(token_scheme)): # ويتعامل معهم بمعرفتهBearer و هو يتعامل معهم و يفصل شق التوكن و الشق  HTTPAuthorizationCredentials تقريباً و الوابة ترجع هذا التنسيق للكلاس الذكي  Bearer <token البوابة هنا ترجع التوكن المفصول عن الطلب على شكل شقين هكذا 
    try:
        token_str = token.credentials # credentials يخزن التوكن في تقنية اسمها  HTTPAuthorizationCredentials فا كما قلنا ال  credentials هكذا نحن نستخرج التوكن الذي على هيأت نص من 
        token_bytes = token_str.encode("utf-8") # HS256 لتحويل التوكن للغة  تفهمها  utf-8 نستعمل  str لفك تشفير التوكن و بما انها لا تفهم التوكن على هيأت  HS256 لتحويل التوكن من نص لأرقام او كما يعرف عنها بيتات و تضعها في مصفوفة لتفهمها خوارزمية التشفير المستعملة في انشاء التوكن المعرفة بأسم  utf-8 بتنسيق  encode نستخدم دالة 
        token_verification = jwt.decode(token_bytes, SECRET_SEAL, "HS256")
        if len(token_verification) == 0:
            log_message("احذر قد  تكون محاولة أختراق ناتجة عن تلاعب في بيانات التوكن", "WARNING")
            raise http_error()
        return token_verification
    except jwt.exceptions.ExpiredSignatureError:
        log_message("أنتهاء صلاحية التوكن", "INFO")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        log_message("احذر قد  تكون محاولة أختراق ناتجة عن تلاعب في بيانات التوكن", "WARNING")
        raise http_error()
async def verify_admin_token(user_data: str = Depends(verify_token)):
    status = await user_id_admin(user_data)
    if status.upper() == "ADMIN":
        return True
    else:
        log_message("احذر محاولة دخول مسار الخاص في الأدارة", "WARNING")
        raise HTTPException(status_code=403, detail="غير مصرح لك بالدخول انت لا تملك صلاحيات")
   