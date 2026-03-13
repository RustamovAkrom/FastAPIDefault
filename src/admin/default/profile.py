from uuid import uuid4

from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, Response
from sqladmin import BaseView, expose

from core.admin.permissions import get_user_id
from core.admin.registry import register_admin
from core.database import async_session
from core.settings import get_settings
from db.models.user import User


def _form_text(value: object) -> str | None:
    return value if isinstance(value, str) else None


@register_admin
class ProfileAdmin(BaseView):
    name = "Profile"
    icon = "fa-solid fa-user"

    @expose("/profile", methods=["GET", "POST"])
    async def profile(self, request: Request) -> Response:
        settings = get_settings()
        user_id = get_user_id(request)

        async with async_session() as session:
            user = await session.get(User, user_id)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found.")

            if request.method == "POST":
                form = await request.form()

                # update text fields
                user.first_name = _form_text(form.get("first_name"))
                user.last_name = _form_text(form.get("last_name"))
                user.phone = _form_text(form.get("phone"))
                user.bio = _form_text(form.get("bio"))

                # avatar upload
                avatar = form.get("avatar")
                if isinstance(avatar, UploadFile) and avatar.filename:
                    ext = avatar.filename.split(".")[-1].lower()

                    if ext not in settings.allowed_image_extensions:
                        raise ValueError("Invalid image")

                    filename = f"{uuid4().hex}.{ext}"

                    path = settings.BASE_DIR / settings.media_root / "avatars" / filename

                    path.parent.mkdir(parents=True, exist_ok=True)

                    with open(path, "wb") as f:
                        f.write(await avatar.read())

                    user.avatar = f"{settings.media_url}/avatars/{filename}"

                await session.commit()

                return RedirectResponse("/admin/profile", status_code=303)

            return await self.templates.TemplateResponse(
                request,
                "admin/profile.html",
                {
                    "request": request,
                    "user": user,
                },
            )
