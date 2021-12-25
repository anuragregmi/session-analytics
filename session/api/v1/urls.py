from rest_framework.routers import DefaultRouter

from session.api.v1.views import SessionViewSet

router = DefaultRouter()

router.register('', SessionViewSet)

urlpatterns = router.urls
