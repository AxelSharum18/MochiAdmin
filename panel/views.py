from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from .models import Producto, CategoriaP, Cliente, Venta, DetalleVenta
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from datetime import datetime
import csv

# Create your views here.
TEMPLATE_DIRS = (
    'os.path.join(BASE_DIR, "templates")'
)

def index(request):
    # Resúmenes de productos, stock y ventas
    total_productos = Producto.objects.count()
    total_stock = Producto.objects.aggregate(Sum('stock'))['stock__sum'] or 0
    total_ventas = Venta.objects.aggregate(Sum('total'))['total__sum'] or 0

    # Calcular ventas del mes
    fecha_inicio_mes = datetime(datetime.now().year, datetime.now().month, 1)
    ventas_del_mes = Venta.objects.filter(fecha__gte=fecha_inicio_mes).aggregate(Sum('total'))['total__sum'] or 0

    # Ventas recientes
    ventas_recientes = Venta.objects.order_by('-fecha')[:5]  # Muestra las últimas 5 ventas

    # Datos para los gráficos
    categorias = CategoriaP.objects.all()
    productos_por_categoria = [
        {'nombre': categoria.nombre, 'total': Producto.objects.filter(categoria=categoria).count()}
        for categoria in categorias
    ]
    
    ventas_por_mes = Venta.objects.extra(select={'mes': "strftime('%Y-%m', fecha)"}).values('mes').annotate(total_ventas=Sum('total')).order_by('mes')

    return render(request, 'index.html', {
        'total_productos': total_productos,
        'total_stock': total_stock,
        'total_ventas': total_ventas,
        'ventas_del_mes': ventas_del_mes,
        'ventas_recientes': ventas_recientes,
        'productos_por_categoria': productos_por_categoria,
        'ventas_por_mes': ventas_por_mes,
    })


def listarProductos(request): 
    
    search = request.GET.get('buscar','')
    
    if search:
        productos = Producto.objects.filter(nombre__icontains=search)
    else:
        productos = Producto.objects.all
    
    return render(request, 'productos.html', {'productos': productos, 'buscar':search})

def agregarProducto(request):
    categorias = CategoriaP.objects.all()

    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST['precio']
        stock = request.POST['stock']
        categoria_id = request.POST.get('categoria')

        categoria = CategoriaP.objects.get(id=categoria_id) if categoria_id else None

        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria
        )
        return redirect('productos')

    return render(request, 'productos/agregar.html', {'categorias': categorias})

def editarProducto(request,idPro):
    producto = get_object_or_404(Producto, id=idPro)
    categorias = CategoriaP.objects.all()

    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST.get('descripcion', '')
        producto.precio = request.POST['precio']
        producto.stock = request.POST['stock']
        categoria_id = request.POST.get('categoria')
        producto.categoria = CategoriaP.objects.get(id=categoria_id) if categoria_id else None
        producto.save()
        return redirect('productos')

    return render(request, 'productos/editar.html', {'producto': producto, 'categorias': categorias})

def eliminarProducto(request,idPro):
    producto = get_object_or_404(Producto, id=idPro)
    producto.delete()
    return redirect('productos')


def listarCat(request):
    categorias = CategoriaP.objects.all()
    return render(request,'categorias.html',{'categorias':categorias})

def agregarCat(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST.get('descripcion', '')
        color = request.POST.get('color', '#6c757d')  # valor por defecto si está vacío
        icono = request.POST.get('icono', '')
        
        CategoriaP.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            color=color,
            icono=icono
        )
        return redirect('categorias')
    return render(request, 'categorias/agregar.html')

def editarCat(request, id):
    categoria = get_object_or_404(CategoriaP, id=id)
    if request.method == 'POST':
        categoria.nombre = request.POST['nombre']
        categoria.descripcion = request.POST.get('descripcion', '')
        categoria.color = request.POST.get('color', '#6c757d')
        categoria.icono = request.POST.get('icono', '')
        categoria.save()
        return redirect('categorias')
    return render(request, 'categorias/editar.html', {'categoria': categoria})

# Eliminar categoría
def eliminarCat(request, id):
    categoria = get_object_or_404(CategoriaP, id=id)
    categoria.delete()
    return redirect('categorias')


def listarClientes(request):
    search = request.GET.get('buscar','')
    
    if search:
        clientes = Cliente.objects.filter(nombre__icontains=search)
    else:
        clientes = Cliente.objects.all
    return render(request,'clientes.html',{'clientes':clientes, 'buscar':search})

def agregarCli(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        correo = request.POST.get('correo', '')
        telefono = request.POST.get('telefono', '')  # valor por defecto si está vacío
        direccion = request.POST.get('direccion', '')
        
        Cliente.objects.create(
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            direccion=direccion
        )
        return redirect('clientes')
    return render(request, 'clientes/agregar.html')

def editarCli(request,id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.nombre = request.POST['nombre']
        cliente.correo = request.POST.get('correo', '')
        cliente.telefono = request.POST.get('telefono','')
        cliente.direccion = request.POST.get('direccion', '')
        cliente.save()
        return redirect('clientes')
    return render(request, 'clientes/editar.html', {'cliente': cliente})

def eliminarCli(request,id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.delete()
    return redirect('clientes')

def listarVentas(request):
    ventas = Venta.objects.all().order_by('-fecha')
    return render(request, 'ventas.html', {'ventas': ventas})

def agregar_venta(request):
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()

    if request.method == 'POST':
        cliente_id = request.POST['cliente']
        cliente = get_object_or_404(Cliente, id=cliente_id)
        nueva_venta = Venta.objects.create(cliente=cliente, fecha=now())

        # Recupera listas de productos y cantidades
        productos_ids = request.POST.getlist('producto[]')
        cantidades = request.POST.getlist('cantidad[]')

        total_venta = 0

        for i in range(len(productos_ids)):
            producto_id = productos_ids[i]
            cantidad = int(cantidades[i])

            if cantidad > 0:
                producto = get_object_or_404(Producto, id=producto_id)
                precio_unitario = producto.precio

                DetalleVenta.objects.create(
                    venta=nueva_venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )

                total_venta += cantidad * float(precio_unitario)

        nueva_venta.total = total_venta
        nueva_venta.save()

        return redirect('ventas')

    return render(request, 'ventas/registrar.html', {
        'productos': productos,
        'clientes': clientes
    })
    
def eliminar_venta(request, id):
    # Obtener la venta
    venta = get_object_or_404(Venta, id=id)
    
    # Eliminar los detalles de la venta asociados
    DetalleVenta.objects.filter(venta=venta).delete()
    
    # Eliminar la venta
    venta.delete()
    
    # Redirigir a la lista de ventas
    return redirect('ventas')
    
def generar_factura_pdf(request, venta_id):
    venta = Venta.objects.get(id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{venta.id}.pdf"'

    p = canvas.Canvas(response)

    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"Factura N° {venta.id}")

    # Datos del cliente
    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"Cliente: {venta.cliente.nombre}")
    p.drawString(100, 750, f"Fecha: {venta.fecha}")

    # Tabla
    y = 700
    p.drawString(100, y, "Producto")
    p.drawString(300, y, "Cantidad")
    p.drawString(400, y, "Precio")

    y -= 20
    for d in detalles:
        p.drawString(100, y, d.producto.nombre)
        p.drawString(300, y, str(d.cantidad))
        p.drawString(400, y, f"S/. {d.precio_unitario}")
        y -= 20

    # Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y - 20, f"Total: S/. {venta.total}")

    p.showPage()
    p.save()
    return response

def exportCSV(request):
    # Crea la respuesta con el tipo de contenido CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Productos.csv"'

    writer = csv.writer(response)
    
    # Escribe la cabecera del archivo CSV
    writer.writerow(['Nombre', 'Descripción', 'Precio', 'Stock', 'Categoria'])

    # Escribe cada fila con los datos de la base de datos
    for produc in Producto.objects.select_related('categoria').all():
        writer.writerow([
            produc.nombre,
            produc.descripcion,
            produc.precio,
            produc.stock,
            produc.categoria.nombre if produc.categoria else 'Sin categoría'
            
        ])

    return response