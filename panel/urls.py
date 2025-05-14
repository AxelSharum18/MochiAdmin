from django.contrib import admin
from django.urls import path
from django import views
from . import views

urlpatterns = [
   path('', views.index, name="index"),
   
   #Productos
   path('producto/', views.listarProductos, name="productos"),
   path('producto/agregar/',views.agregarProducto, name="agregar"),
   path('producto/editar/<int:idPro>/',views.editarProducto, name="editar"),
   path('producto/delete/<int:idPro>/',views.eliminarProducto,name="eliminar"),
   path('producto/export/', views.exportCSV, name="export_csv"),
   #Categoria de Productos
   path('categoria/',views.listarCat,name="categorias"),
   path('categoria/agregar/',views.agregarCat, name = "agregarca"),
   path('categoria/editar/<int:id>/',views.editarCat, name = "editarca"),
   path('categoria/delete/<int:id>/',views.eliminarCat, name = "eliminarca"),
   #Clientes
   path('cliente/',views.listarClientes, name="clientes"),
   path('cliente/agregar',views.agregarCli, name="agregarCli"),
   path('cliente/editar/<int:id>/',views.editarCli, name="editarCli"),
   path('cliente/delete/<int:id>/',views.eliminarCli, name="eliminarCli"),
   #Ventas
   path('ventas/',views.listarVentas, name="ventas"),
   path('ventas/agregar',views.agregar_venta,name = "agregarVe"),
   path('ventas/eliminar/<int:id>/', views.eliminar_venta, name='eliminar_venta'),
   path('ventas/factura/<int:venta_id>/', views.generar_factura_pdf, name='generar_factura'),
]
