from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy .orm import Mapped, mapped_column, relationship
from src .models .base import Base

from src.utils.time import utcnow


class Role (Base ):
    __tablename__ ="roles"

    CODE_STUDENT ="student"
    CODE_TEACHER ="teacher"

    id :Mapped [int ]=mapped_column (BigInteger ,primary_key =True )
    code :Mapped [str ]=mapped_column (String (255 ),nullable =False ,unique =True )
    name :Mapped [str ]=mapped_column (String (255 ),nullable =False )

class User (Base ):
    __tablename__ ="users"

    id :Mapped [int ]=mapped_column (BigInteger ,primary_key =True )
    role_id :Mapped [int ]=mapped_column (ForeignKey ("roles.id"),nullable =False )
    email :Mapped [str ]=mapped_column (String (255 ),nullable =False ,unique =True )
    password_hash :Mapped [str ]=mapped_column (String (255 ),nullable =False )
    full_name :Mapped [str ]=mapped_column (String (255 ),nullable =False )
    is_active :Mapped [bool ]=mapped_column (Boolean ,nullable =False ,default =True )
    created_at :Mapped [datetime ]=mapped_column (
    DateTime ,nullable =False ,default =utcnow
    )

    role_obj :Mapped ["Role"]=relationship ("Role",lazy ="joined",foreign_keys =[role_id ])

    @property
    def role_code (self )->str :
        return self .role_obj .code if self .role_obj else ""

    @property
    def role (self )->str :
        return self .role_code

    @property
    def is_teacher (self )->bool :
        return self .role_code ==Role .CODE_TEACHER

    @property
    def is_student (self )->bool :
        return self .role_code ==Role .CODE_STUDENT
