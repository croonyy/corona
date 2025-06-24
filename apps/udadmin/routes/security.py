from fastapi import APIRouter
from ..utils.urls import Path

from apps.udadmin.views import security as st


router = APIRouter()
path = Path(router)


path("/token", st.login)
path("/refresh", st.refresh)
path("/me", st.me)
path("/get_field_types", st.get_field_types)
