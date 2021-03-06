# -*- coding:utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, redirect, render_to_response
from django.template.context_processors import csrf
from alibaba.forms import PosterForm
from alibaba.models import WallPoster, Photo, Cover, Follow, MyFollowers, SecretKey, Vip_peoples
from django.contrib import auth
from django.contrib.auth.models import User
from alibaba.other_functions_by_kirill import end_of_name
from django.core.mail import send_mail
from AlibabaStudio.settings import EMAIL_HOST_USER, MEDIA_ROOT


def signup(request):
    args = {}
    args.update(csrf(request))
    args['signup_error'] = None
    if auth.get_user(request).username:
        return redirect('/user/{userlogin}/'.format(userlogin=auth.get_user(request).username))
    if request.POST:
        args['username'] = request.POST.get('username', '')
        args['email'] = request.POST.get('email', '')
        args['first_name'] = request.POST.get('first_name', '')
        args['password'] = request.POST.get('password', '')
        args['password2'] = request.POST.get('password2', '')
        args['key'] = request.POST.get('key','')

        if SecretKey.objects.filter(secret_key=args['key']).count() == 0:
            # args['signup_error'] = 'Нет пользователя с таким персональным ключом!'
            return redirect('/auth/signup/?error=NOT_ACCESS')

        if args['username'] == '' or args['first_name'] == '' or args['password'] == '' or args['password2'] == '':
            # args['signup_error'] = 'Ни одно поле не должно быть пустым!'
            return redirect('/auth/signup/?error=empty_input')

        if args['password'] != args['password2']:
            # args['signup_error'] = 'Пароли не совпадают!'
            return redirect('/auth/signup/?error=passwords_not')

        if User.objects.filter(username=args['username']).count() > 0:
            # args['signup_error'] = 'Пользователь c таким логином уже есть!'
            return redirect('/auth/signup/?error=user_in_db')

        if User.objects.filter(email=args['email']).count() > 0:
            # args['signup_error'] = 'Пользователь c таким email уже есть!'
            return redirect('/auth/signup/?error=email_in_db')

        user = User.objects.create_user(username=args['username'], first_name=args['first_name'], password=args['password'], email=args['email'])
        user_object = User.objects.get(username=args['username'])
        profile_photo = Photo.objects.create(profile=user_object, username_photo=args['username'], profile_photo='/static/alibaba/images/addPhoto.png', first_name_photo=user_object.first_name)
        profile_cover = Cover.objects.create(profile=user_object, username_cover=args['username'], profile_cover='/static/alibaba/images/fon.jpg', first_name_cover=user_object.first_name)
        profile_photo.save()
        profile_cover.save()
        user.save()
        return render(request, 'loginsys/success_signup.html', args)
    elif request.GET:
        error = request.GET.get('error', '')
        if error == 'empty_input':
            args['signup_error'] = 'Заполните все поля!'
            return render_to_response('loginsys/signup.html', args)
        elif error == 'NOT_ACCESS':
            args['signup_error'] = 'Нет пользователя с таким персональным ключом!'
            return render_to_response('loginsys/signup.html', args)
        elif error == 'passwords_not':
            args['signup_error'] = 'Пароли не совпадают!'
            return render_to_response('loginsys/signup.html', args)
        elif error == 'email_in_db':
            args['signup_error'] = 'Пользователь с таким email уже есть!'
            return render_to_response('loginsys/signup.html', args)
        elif error == 'user_in_db':
            args['signup_error'] = 'Такой пользователь уже есть!'
            return render_to_response('loginsys/signup.html', args)
    else:
        return render(request, 'loginsys/signup.html')


def login(request):
    if auth.get_user(request).username:
        return redirect('/user/{userlogin}/'.format(userlogin=auth.get_user(request).username))
    args = {}
    args.update(csrf(request))
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        args['username'] = username
        args['password'] = password
        if user is not None:
            auth.login(request, user)
            return redirect('/user/{userlogin}/'.format(userlogin=auth.get_user(request).username))
        else:
            # args['login_error'] = 'Такого пользователя нет!'
            return redirect('/auth/login/?error=user_false')
    elif request.GET:
        error = request.GET.get('error', '')
        if error == 'user_false':
            args['login_error'] = 'Такого пользователя нет!'
            return render_to_response('loginsys/login.html', args)
    else:
        return render(request, 'loginsys/login.html', args)


def user(request, login):
    args = {}
    args.update(csrf(request))
    try:
        args['img'] = Photo.objects.get(username_photo=login)
        args['img_url'] = args['img'].profile_photo.url
    except ObjectDoesNotExist:
        args['img_url'] = '/static/alibaba/images/addPhoto.png'
    try:
        args['cover'] = Cover.objects.get(username_cover=login)
        args['cover_url'] = args['cover'].profile_cover.url
    except ObjectDoesNotExist:
        args['cover_url'] = '/static/alibaba/images/fon.jpg'

    if Vip_peoples.objects.filter(vip_person=login).count() > 0:
        args['vip_persons'] = Vip_peoples.objects.filter(vip_person=login).values_list('vip_person', flat=True)

    try:
        if login == auth.get_user(request).username:
            poster_form = PosterForm()
            args['user'] = User.objects.get(username=auth.get_user(request).username)
            args['my_login'] = auth.get_user(request).username
            args['form'] = poster_form
            u = auth.get_user(request).id
            args['posters'] = WallPoster.objects.filter(poster=u)
            args['count_posters'] = WallPoster.objects.filter(poster=u).count()
            args['word'] = end_of_name.end(args['count_posters'])
            args['login'] = login
            # Мои интересные страницы
            args['i_follow'] = Follow.objects.filter(whoes_profile_page=args['user'].username)
            args['i_follow_count'] = args['i_follow'].count()
            # Те, кому я интересен
            args['me_follow'] = Follow.objects.filter(follow_username=args['user'].username)
            args['me_follow_count'] = args['me_follow'].count()


            args['media_root'] = MEDIA_ROOT
        else:
            if auth.get_user(request).username:
                poster_form = PosterForm()
                args['user'] = User.objects.get(username=login)
                args['my_login'] = auth.get_user(request).username
                args['form'] = poster_form
                u = args['user'].id
                args['posters'] = WallPoster.objects.filter(poster=u)
                args['count_posters'] = WallPoster.objects.filter(poster=u).count()
                args['word'] = end_of_name.end(args['count_posters'])
                args['login'] = login
                # Интересные страницы пользователя
                args['i_follow'] = Follow.objects.filter(whoes_profile_page=args['user'].username)
                args['i_follow_count'] = args['i_follow'].count()
                # Те, кому пользователь интересен
                args['me_follow'] = Follow.objects.filter(follow_username=args['user'].username)
                args['me_follow_count'] = args['me_follow'].count()
                if Follow.objects.filter(followers_username=args['my_login'], follow_username=args['user'].username):
                    args['button_status'] = 'already_follow'
                else:
                    args['button_status'] = 'not_follow'
            else:
                return render(request, 'alibaba/anon_user.html', args)
    except ObjectDoesNotExist:
        raise Http404
    return render(request, 'alibaba/user.html', args)


def logout(request):
    auth.logout(request)
    return redirect('/')


def forgot_pass(request):
    if auth.get_user(request).username:
        return redirect('/user/{userlogin}/'.format(userlogin=auth.get_user(request).username))
    if request.GET:
        error = request.GET.get('error','')
        return render(request, 'loginsys/forgot_pass.html', {'error':error})
    return render(request, 'loginsys/forgot_pass.html')


def success_forgot(request):
    if auth.get_user(request).username:
        return redirect('/user/{userlogin}/'.format(userlogin=auth.get_user(request).username))
    return render(request, 'loginsys/success_forgot.html')


def send_password_on_mail(request):
    if auth.get_user(request).username:
        return redirect('/user/{userlogin}/'.format(userlogin=auth.get_user(request).username))
    if request.POST:
        email = request.POST.get('email', '')
        if User.objects.filter(email=email).count() != 0:
            send_mail('Восстановление пароля vipmakergold.ru', 'Запрос на воостановление', EMAIL_HOST_USER, [email])
        else:
            return redirect('/auth/forgot_pass/?error=no_email')
        return redirect('/auth/success_forgot/')
    return redirect('/')