# Planificación de modelos — Cervecería y bebidas artesanales

Fecha: 31 de octubre de 2026. Este diseño se registra antes de implementar los cuatro modelos adicionales y sus migraciones.

## Los diez modelos

| Aplicación | Modelo | Campos principales | Relaciones |
| --- | --- | --- | --- |
| usuarios | Usuario | Usuario personalizado basado en AbstractUser | Pedidos, direcciones y reseñas |
| catalogo | Categoria | nombre único, descripción | Una categoría tiene muchos productos |
| catalogo | Marca | nombre único, descripción | Una marca tiene muchos productos |
| catalogo | Producto | nombre, descripción, precio, stock, imagen | Categoría y marca obligatorias; presentación opcional; varios proveedores |
| pedidos | Pedido | usuario, fecha, estado | Varios detalles y dirección de envío opcional |
| pedidos | DetallePedido | cantidad, precio unitario, subtotal calculado | Un pedido y un producto |
| catalogo | Presentacion | nombre, capacidad_ml | Una presentación puede usarse en varios productos |
| catalogo | Proveedor | nombre único, email, teléfono, dirección, activo | Muchos a muchos con productos |
| usuarios | DireccionEnvio | destinatario, calle, número, piso/departamento, ciudad, provincia, código postal, país, teléfono | Pertenece a un usuario; puede usarse en varios pedidos de ese usuario |
| catalogo | Resena | calificación de 1 a 5, comentario, fecha | Un usuario y un producto; una reseña por cada pareja usuario-producto |

## Uso en el negocio

- **Presentacion:** permite distinguir lata de 473 ml, botella de 500 ml o barril de 30.000 ml. Cada combinación de bebida y presentación se carga como un producto con su propio precio y stock. Cambiar la presentación no crea variantes automáticamente.
- **Proveedor:** permite conocer quién abastece cada bebida; un producto puede conseguirse mediante varios proveedores y cada proveedor puede suministrar varios productos.
- **DireccionEnvio:** permite que un cliente registre varias direcciones y seleccione una para el pedido. Una dirección ya usada no se elimina mientras existan pedidos que la referencien. La aplicación deberá gestionar por separado una copia histórica si necesita conservar el domicilio exactamente como estaba al comprar.
- **Resena:** permite que un cliente valore un producto una única vez y actualice posteriormente su valoración.

## Reglas y decisiones

1. La capacidad debe ser mayor que cero. No se repite una misma combinación de nombre y capacidad de presentación.
2. La calificación debe estar entre 1 y 5 y no puede repetirse la pareja usuario-producto. Estas reglas se validan también mediante restricciones de base de datos.
3. La dirección elegida para un pedido debe pertenecer al usuario de ese pedido. Esta regla se comprueba en `Pedido.clean()` y en los formularios del administrador. Las futuras escrituras desde la API deberán validar también esa pertenencia; `save()` no ejecuta `full_clean()` automáticamente.
4. Se conservan las relaciones protegidas del catálogo original. Una presentación asignada a productos y una dirección usada en pedidos se protegen con `PROTECT`.
5. Las reseñas se eliminan con `CASCADE` si se elimina su usuario o producto. Las direcciones no utilizadas se eliminan con su usuario.
6. Los productos y pedidos existentes siguen siendo válidos: presentación y dirección son opcionales, y la relación con proveedores permite una lista vacía.
7. La relación muchos a muchos genera una tabla intermedia automática. Esa tabla no se cuenta como uno de los diez modelos propios.
8. Los cuatro modelos nuevos se administrarán desde Django Admin, con búsquedas, filtros y ordenamiento según corresponda. Los cambios se distribuirán mediante nuevas migraciones, sin reescribir las iniciales.

## Ejemplo

Una clienta registra una dirección en Río Cuarto. Compra el producto «IPA artesanal, lata de 473 ml», perteneciente a una categoría y una marca, abastecido por uno o varios proveedores. Su pedido tiene un detalle con la cantidad y el precio unitario, y puede asociarse a su dirección. Después puede dejar una reseña de 1 a 5 estrellas.

## Límite de este aporte

Se implementan modelos, relaciones, validaciones, migraciones, administración y pruebas. La exposición de al menos ocho modelos mediante ViewSets y los demás requisitos de API se deben abordar en otra tarea coordinada con el grupo.
