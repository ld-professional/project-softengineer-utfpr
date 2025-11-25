from django.contrib import admin
from .models import UserPersonalizado
from django.contrib.auth.admin import UserAdmin
 

class UserPersonalizadoAdmin(UserAdmin):

    list_display=(
        'username',
        'email',
        'telefone',
        )

    search_fields=(
        'username', 
        )

    list_filter=('is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email",'telefone')}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2",'email','telefone'),
            },
        ),
    )

admin.site.register(UserPersonalizado,UserPersonalizadoAdmin)