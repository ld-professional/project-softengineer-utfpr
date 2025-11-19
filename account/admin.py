from django.contrib import admin
from .models import UserPersonalizado
from django.contrib.auth.admin import UserAdmin
# Register your models here.


#. Como você está usando um AbstractUser, o ideal não é usar admin.ModelAdmin simples, e sim herdar de UserAdmin.

class UserPersonalziadoAdmin(UserAdmin):

    list_display=(
        'username',
        'email',
        'telefone',
        #'is_staff' so se eu tivesse funcionarios...
        #  mas o mehlor seria criar um campo proprio chamado eh_funct pq aqui eles tem acesso
        #  ao /admin msm q seja so pra visualizar
    )

    search_fields=(
        'username',
    )

    list_filter=(['is_staff', 'is_superuser', 'is_active'])


    #clico em useradmin copio um tal de  fieldsets e em informacoes pessoas coloco o telefone
    # cltr e botao direito em useradmin => go to definiton, dps apagar o _()

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email",'telefone')}),
        (
            ("Permissions"),
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
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2"),
            },
        ),
    )

admin.site.register(UserPersonalizado,UserPersonalziadoAdmin)