from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import TokenAuthForm, PasswordAuthForm, RegisterForm
from .models import Team, TeamManager, TeamLogin
from quests.models import Quest
from board.boards import get_scoreboard

# Create your views here.
from quests.models import Quest


def groupby(collection, key):
    current = prev = object()
    res = []
    subres = []
    it = iter(collection)
    try:
        first = next(it)
    except StopIteration:
        return []
    prev = getattr(first, key)
    subres.append(first)
    for el in it:
        current = getattr(el, key)
        if current == prev:
            subres.append(el)
        else:
            res.append((prev, subres))
            prev = current
            subres = [el]
    if subres:
        res.append((prev, subres))
    return res


@login_required
def show(req, name):
    team = get_object_or_404(Team, name=name)
    solved_tasks = Quest.objects.filter(questvariant__team_id=team.id, questvariant__questanswer__is_checked=True,
                                        questvariant__questanswer__is_success=True).distinct().select_related('category').order_by('category__id')
    by_category = groupby(solved_tasks, 'category')
    
    total_points = sum([t.score for t in solved_tasks])
    scoreboard = get_scoreboard()
    place = list(scoreboard).index(team) + 1

    return render(req, 'teams/show.html', {"team": team, "total_points": total_points, "place": place, "solved_tasks": solved_tasks, "by_category": by_category})


# Obsolete, don't use now
def do_login_by_token(request):
    if request.method == "POST":
        form = TokenAuthForm(data=request.POST)
        if form.is_valid():
            team = authenticate(token=form.cleaned_data['token'])

            # Don't know why, but don't allow to login staff and admins via main form
            if team is not None and not team.is_staff and not team.is_superuser:
                login(request, team)
                return redirect("home")
            else:
                if team is None:
                    form.errors['token'] = form.error_class(["Wrong token"])
                else:
                    form.errors['token'] = form.error_class(["Special users can't login by token"])
        return render(request, "teams/login.html", {"form": form})
    else:
        return render(request, "teams/login.html", {"form": TokenAuthForm()})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def do_login(request):
    if request.method == "POST":
        form = PasswordAuthForm(data=request.POST)
        if form.is_valid():
            team = authenticate(username=form.cleaned_data['login'], password=form.cleaned_data['password'])

            if team is not None:
                TeamLogin(team=team, ip_address=get_client_ip(request)).save()
                login(request, team)
                next_page = request.POST.get("next")
                if next_page:
                    return redirect(next_page)
                return redirect("home")
            else:
                form.errors['password'] = form.error_class(["Wrong login or password"])
        return render(request, "teams/login.html", {"form": form})
    else:
        return render(request, "teams/login.html", {"form": PasswordAuthForm()})



def do_logout(request):
    logout(request)
    return redirect("home")


def set_lang(request, lang_code):
    from django.utils import translation

    translation.activate(lang_code)
    response = redirect(request.META['HTTP_REFERER'])
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


def open_all_quests(team):
    quests = Quest.objects.all()
    for q in quests:
       q.open_for.add(team)
       q.save()


def register(request):
    if request.method == "POST":
        form = RegisterForm(data=request.POST)
        ### Registration is disabled due attack 2015.11.17
        ### Registration is open since 2015.11.24
        if form.is_valid():
            name = form.cleaned_data['name']
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']

            team = Team(name=name, login=login, is_staff=False, is_superuser=False)
            team.set_password(password)

            try:
                team.save()

                open_all_quests(team)

                return redirect('home')
            except:
                form.errors['login'] = form.error_class(['User with same login already exists'])

        return render(request, 'teams/register.html', {'form': form})
    else:
        return render(request, 'teams/register.html', {'form': RegisterForm()})
