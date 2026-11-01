from django.db.models.deletion import ProtectedError
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Categoria, Marca, Producto
from .permissions import IsStaffOrReadOnly
from .serializers import (
    CategoriaSerializer,
    MarcaSerializer,
    ProductoSerializer,
    ProductoPublicSerializer,
)


# ModelViewSet de producto: contiene metodos GET,PUT,PATCH y DELETE
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related(
        "categoria", "marca"
    ).order_by("id")
    serializer_class = ProductoSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductoPublicSerializer
        return ProductoSerializer

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                "No se puede eliminar un producto incluido en pedidos."
            )

# ModelViewSet de categoría.
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.order_by("id")
    serializer_class = CategoriaSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                "No se puede eliminar una categoría con productos asociados."
            )
# ModelViewSet de marca.
class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.order_by("id")
    serializer_class = MarcaSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                "No se puede eliminar una marca con productos asociados."
            )