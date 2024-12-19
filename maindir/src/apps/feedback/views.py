from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FeedbackCreateForm
from django.core.mail import EmailMessage
from utils.helpers import get_client_ip
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from config import settings

from .forms import FeedbackCreateForm

def feedback_form(request):
    return {'feedback_form': FeedbackCreateForm()}


def feedback_create_view(request):
    success_url = reverse_lazy('home')
    form = FeedbackCreateForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.ip_address = get_client_ip(request)
        if request.user.is_authenticated:
            feedback.user = request.user
        feedback.save()

        user = User.objects.get(id=feedback.user_id) if feedback.user_id else None
        message = render_to_string('feedback_email_send.html', {
            'email': feedback.email,
            'content': feedback.content,
            'ip': feedback.ip_address,
            'user': user,
        })
        email = EmailMessage(
            feedback.subject,
            message,
            from_email=settings.EMAIL_SERVER,
            to=[settings.EMAIL_ADMIN]
        )
        email.send(fail_silently=False)

        messages.success(request, 'Ваше письмо успешно отправлено администрации сайта')
        return redirect(success_url)