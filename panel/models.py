from django.db import models

# Create your models here.

class CategoriaP(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default="#6c757d")  # Color en HEX
    icono = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    categoria = models.ForeignKey(CategoriaP, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_agregado = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente.nombre}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


#class Categoria(models.Model):
#    nombre = models.CharField(max_length=40, unique=True)
#    color = models.CharField(max_length=7)
#    class Meta:
#        db_table = 'Categoria'
#    def __str__(self):
#        return self.nombre

#class Transaccion(models.Model):
#    id = models.AutoField(primary_key=True)
#    tipo = models.CharField(max_length=30)
#    monto = models.IntegerField()
#    descripcion = models.CharField(max_length=100)
#    fecha = models.DateField(null=True)
#    categoria = models.ForeignKey(
#        Categoria, 
#       on_delete=models.SET_NULL, 
#        null=True, 
#        blank=True
#    )
#    class Meta:
#        db_table = 'Transaccion'


      