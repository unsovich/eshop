import os
from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order


@shared_task
def payment_completed(order_id):
    # Task to send an e-mail notification when an order is successfully paid.
    order = Order.objects.get(id=order_id)
    # create invoice e-mail
    subject = f'EShop - Invoice no. {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject,
                         message,
                         'test@cocob.ru',
                         [order.email])
    # generate PDF
    html = render_to_string('pdf.html', {'order': order})
    out = BytesIO()
    css_path = os.path.join(settings.STATIC_ROOT, 'css/pdf.css')
    stylesheets = [weasyprint.CSS(filename=css_path)]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

    email.attach(f'order_{order.id}.pdf',
                 out.getvalue(),
                 'application/pdf')

    email.send()
