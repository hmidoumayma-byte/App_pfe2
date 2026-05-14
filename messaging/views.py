# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Conversation, Message
from accounts.models import User

@login_required
def inbox(request):
    conversations = request.user.conversations.filter(is_active=True
        ).prefetch_related('participants','messages').order_by('-updated_at')
    for conv in conversations:
        conv.unread_count = conv.messages.filter(
            is_read=False).exclude(sender=request.user).count()
    return render(request, 'messaging/inbox.html', {'conversations': conversations})

@login_required
def conversation_detail(request, pk):
    conv = get_object_or_404(Conversation, pk=pk)
    if request.user not in conv.participants.all(): return redirect('messaging:inbox')
    conv.messages.filter(is_read=False).exclude(sender=request.user
        ).update(is_read=True, read_at=timezone.now())
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(conversation=conv, sender=request.user, content=content)
            conv.save()
            from notifications.models import Notification
            for p in conv.participants.exclude(pk=request.user.pk):
                Notification.objects.create(user=p,
                    title=f'Nouveau message de {request.user.get_full_name()}',
                    message=content[:100], notification_type='info')
        return redirect('messaging:conversation', pk=pk)
    msgs = conv.messages.select_related('sender').all()
    return render(request, 'messaging/conversation.html', {'conv':conv,'msgs':msgs})

@login_required
def new_conversation(request):
    if request.method == 'POST':
        rid = request.POST.get('recipient')
        subject = request.POST.get('subject','').strip()
        content = request.POST.get('content','').strip()
        if not (rid and subject and content):
            messages.error(request, 'Tous les champs sont requis.')
            return redirect('messaging:new')
        recipient = get_object_or_404(User, pk=rid)
        if request.user.is_student() and recipient.is_teacher(): ct = 'student_teacher'
        elif request.user.is_student() and recipient.is_admin(): ct = 'student_admin'
        else: ct = 'teacher_student'
        conv = Conversation.objects.create(subject=subject, conv_type=ct)
        conv.participants.add(request.user, recipient)
        Message.objects.create(conversation=conv, sender=request.user, content=content)
        from notifications.models import Notification
        Notification.objects.create(user=recipient, title=f'Nouveau message: {subject}',
            message=content[:100], notification_type='info')
        messages.success(request, 'Message envoye.')
        return redirect('messaging:conversation', pk=conv.pk)
    if request.user.is_student(): recipients = User.objects.filter(role__in=['teacher','admin'])
    elif request.user.is_teacher(): recipients = User.objects.filter(role='student')
    else: recipients = User.objects.all()
    return render(request, 'messaging/new.html', {'recipients': recipients})
