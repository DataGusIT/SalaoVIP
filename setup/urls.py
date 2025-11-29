from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Remova a importação antiga 'auth_views' se não for usar mais nada dela, 
# ou mantenha se tiver usando PasswordReset
from users import views as user_views 

urlpatterns = [
    path('', user_views.home, name='home'),
    path('admin/', admin.site.urls),
    
    path('registro/', user_views.registro, name='registro'),
    
    # --- MUDANÇA AQUI: Usando nossas views customizadas ---
    path('login/', user_views.CustomLoginView.as_view(), name='login'),
    path('logout/', user_views.custom_logout, name='logout'),
    # -----------------------------------------------------
    
    path('perfil/', user_views.editar_perfil, name='editar_perfil'),
    path('agendamento/', include('agendamento.urls')),
    
    path('notificacoes/', include('notificacoes.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)