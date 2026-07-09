from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *
from django.contrib.auth.decorators import login_required

# 로그인
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user) 
            return redirect('posts:post_list')
        else:
            messages.error(request, "아이디 또는 비밀번호가 틀렸습니다.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


# 로그아웃
def logout_view(request):
    auth_logout(request) 
    return redirect('accounts:login')


# 회원가입 
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # 자동 로그인(auth_login) 제거! 비밀번호 암호화 후 DB 저장만 수행
            return redirect('accounts:signup_complete') 
        else:
            messages.error(request, "회원가입 정보가 올바르지 않습니다. 다시 확인해주세요.")
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


# 회원가입 완료 창 뷰 (완료 창 + 로그인 하러 가기 버튼 대응)
def signup_complete(request):
    return render(request, 'accounts/signup_complete.html')


# 아이디 중복 확인 API (프론트엔드 비동기 JavaScript 요청용)
@csrf_exempt
def check_username(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username", "")
            
            # 아이디 4~12자
            if len(username) < 4 or len(username) > 12:
                return JsonResponse({"result": "fail", "message": "아이디는 4~12자여야 합니다."}, status=400)
                
            if User.objects.filter(username=username).exists():
                return JsonResponse({"result": "fail", "message": "이미 사용 중인 아이디입니다."}, status=200)
                
            return JsonResponse({"result": "success", "message": "사용 가능한 아이디입니다."}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"result": "fail", "message": "잘못된 요청 데이터입니다."}, status=400)
        
        

# 프로필 설정 페이지(HTML)를 보여주는 뷰
@login_required 
def profile_setup_view(request):
    return render(request, 'profile_setup.html')

#  닉네임 중복 확인         
@csrf_exempt
def check_nickname(request):
    if request.method != "POST":
        return JsonResponse({"result": "fail", "message": "잘못된 요청 메서드입니다."}, status=405)
        
    try:
        data = json.loads(request.body)
        nickname = data.get("nickname", "").strip()
        
        if len(nickname) < 2 or len(nickname) > 12:
            return JsonResponse({"result": "fail", "message": "닉네임은 2~12자여야 합니다."}, status=400)
            
        # 로그인 유저라면 본인 닉네임은 제외하고 중복 체크
        query = Profile.objects.filter(nickname=nickname)
        if request.user.is_authenticated:
            query = query.exclude(user=request.user)
            
        if query.exists():
            return JsonResponse({"result": "fail", "message": "이미 사용 중인 닉네임입니다."}, status=400)
            
        return JsonResponse({"result": "success", "message": "사용 가능한 닉네임입니다."}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({"result": "fail", "message": "잘못된 요청 데이터입니다."}, status=400)



# 중복 검증 완료 후 최종적으로 닉네임을 변경 및 저장하는 API
@csrf_exempt
def update_profile(request):
    # API 환경에 맞는 로그인 필수 검증
    if not request.user.is_authenticated:
        return JsonResponse({"result": "fail", "message": "로그인이 필요한 서비스입니다."}, status=401)

    if request.method != "POST":
        return JsonResponse({"result": "fail", "message": "잘못된 요청 메서드입니다."}, status=405)

    # FormData 형식으로 들어오는 데이터는 request.POST와 request.FILES로 받음
    new_nickname = request.POST.get('nickname', '').strip()
    profile_image = request.FILES.get('profile_image')  # 프론트의 파일 input name과 맞춰야 함

    if not new_nickname:
        return JsonResponse({"result": "fail", "message": "닉네임을 입력해주세요."}, status=400)

    if not (2 <= len(new_nickname) <= 12):
        return JsonResponse({"result": "fail", "message": "닉네임은 2자 이상 12자 이하로 입력해주세요."}, status=400)

    # 본인이 현재 사용 중인 닉네임을 그대로 유지하는 경우는 통과시키고, 다른 사람이 쓰는 경우만 차단
    if Profile.objects.filter(nickname=new_nickname).exclude(user=request.user).exists():
        return JsonResponse({"result": "fail", "message": "이미 사용 중인 닉네임입니다."}, status=400)

    # 안전하게 프로필 가져오기
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, nickname=f"유저_{request.user.id}")

    # 데이터 업데이트 후 저장
    profile.nickname = new_nickname
    
    # 새로운 프로필 이미지 파일이 정상적으로 등록되었다면 저장함
    if profile_image:
        profile.profile_image = profile_image
        
    profile.save()

    return JsonResponse({"result": "success", "message": "프로필 설정이 정상적으로 완료되었습니다."}, status=200)