from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from .models import User

@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    # Campos que aparecem na lista (tabela) de usuários
    list_display = ["username", "email", "tipo", "telefone", "is_superuser"]
    
    # Filtros laterais
    list_filter = ["tipo", "is_superuser", "is_active", "groups"]
    
    # Campos de busca
    search_fields = ["username", "email", "telefone"]

    # Configuração dos campos no formulário de EDIÇÃO de usuário
    # Precisamos adicionar nossos campos personalizados (tipo, telefone, foto)
    fieldsets = auth_admin.UserAdmin.fieldsets + (
        ("Informações Extras", {"fields": ("tipo", "telefone", "foto")}),
    )

    # Configuração dos campos no formulário de CRIAÇÃO de usuário
    add_fieldsets = auth_admin.UserAdmin.add_fieldsets + (
        ("Informações Extras", {"fields": ("tipo", "telefone", "foto")}),
    )