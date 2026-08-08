import os
def profile_photo_folder():
    if not os.path.exists("uploads"):
            os.makedirs("uploads")