import bcrypt

"""
TODO: Раскидать комментарии
"""

class Hashed():
    @staticmethod
    async def hashed_password(password: str):
        hpassword = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )
        return hpassword.decode("utf-8")
    
    @staticmethod
    async def verify_password(password: str, hashed_password: str):
        current = bcrypt.checkpw(
            password=password.encode("utf-8"),
            hashed_password=hashed_password.encode("utf-8")
        )
        return current