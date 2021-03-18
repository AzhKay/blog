from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from Blog_t import settings
from main.views import CategoryListView, PostViewSet, PostImageView, PostCommentView, RatingViewSet
from drf_yasg.views import get_schema_view


schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version='v1',
        description="Test description",
    ),
    public=True
)

router = DefaultRouter()
router.register('posts', PostViewSet)

router_com = DefaultRouter()
router.register('comments', PostCommentView)

router.register('ratings', RatingViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('v1/api/docs/', schema_view.with_ui()),
    path('v1/api/categories/', CategoryListView.as_view()),
    path('v1/api/add-image/', PostImageView.as_view()),
    path('v1/api/account/', include('account.urls')),
    path('v1/api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
