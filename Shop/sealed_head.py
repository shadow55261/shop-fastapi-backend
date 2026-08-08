import os 
from dotenv import load_dotenv

load_dotenv("secret_seal.env") # secret_seal.env لقراءة الختم بتاع التوكن من ملف  load_dotenv نستعمل الدالة 

SECRET_SEAL = os.getenv("SECRET_SEA") # SECRET_SEAL الذي في الذاكرة بايثون اصبح يحمل ختم التوقي و نستخرج الختم ونخزنه في المتغير  SECRET_SEA و هنا نستخرج المتغير 

