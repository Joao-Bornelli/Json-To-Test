from django.shortcuts import render,redirect
from django.template import loader
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm
import json

from core.docxGeneration import generate_docx

from django.contrib.auth.decorators import login_required
# Create your views here.

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request=request, username=username, password=password)
        print('>>usuario',user)
        print('>>username',username)
        print('>>password',password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            error = "Usuario ou senha incorretos!"
    
    return render(request, 'login.html', {'error': error})

def signup_view(request):
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('home')
    else:
        form = SignupForm()
    
    return render(request, 'signup.html', {'form': form})


@login_required
def home_view(request):
    fields = {'Contexto','Comando','Alternativas','Justificativa do Gabarito','Justificativa dos Distratores','Informações Essenciais'}
    error = []
    if request.method == 'POST':
        # Test Header Data Validation
        receivedFile = request.FILES.get('file')
        headerData = {
            'Course_Unit': request.POST.get('Course_Unit',''),
            'Instructor': request.POST.get('Instructor',''),
            'Course': request.POST.get('Course',''),
        }
        
        if not receivedFile:
            error.append('Nenhum arquivo selecionado.')
            #return render(request, 'home.html', {'error': 'Nenhum arquivo selecionado.'})
        
        if headerData['Course_Unit'].strip() == '':
            error.append('O campo "Unidade Curricular" é obrigatório.')
            #return render(request, 'home.html', {'course_unit_error': 'O campo "Unidade Curricular" é obrigatório.'})
        if headerData['Instructor'].strip() == '':
            error.append('O campo "Docente" é obrigatório.')
            #return render(request, 'home.html', {'instructor_error': 'O campo "Docente" é obrigatório.'})
        if headerData['Course'].strip() == '':
            error.append('O campo "Curso" é obrigatório.')
            #return render(request, 'home.html', {'course': 'O campo "Curso" é obrigatório.'})
        
        if error:        
            return render(request, 'home.html', {'error': error})
        
        
        
        # Test File Data Validation
        try:
            jsonData = json.load(receivedFile)
            if isinstance(jsonData, list):
                if len(jsonData) == 0:
                    error.append('Arquivo JSON está vazio.')
                    #return render(request, 'home.html', {'error': 'Arquivo JSON está vazio.'})
                else:
                    jsonData = jsonData[0]
                
            missing = fields - jsonData.keys() 
            for field in missing:
                error.append(f'Campo obrigatório "{field}" ausente no arquivo.')
                #return render(request, 'home.html', {'error': f'Campo obrigatório "{field}" ausente no arquivo.'})
            
            if len(jsonData['Alternativas'])<3:
                error.append('O campo "Alternativas" deve conter pelo menos 3 itens.')
                #return render(request, 'home.html', {'error': 'O campo "Alternativas" deve conter pelo menos 3 itens.'})
            
            if len(jsonData['Alternativas'])>4:
                error.append('O campo "Alternativas" deve conter no máximo 4 itens.')
                #return render(request, 'home.html', {'error': 'O campo "Alternativas" deve conter no máximo 4 itens.'})
            
            for alt in jsonData['Alternativas']:
                if alt['texto'].strip() == '':
                    error.append('As alternativas não podem estar vazias.')
                    #return render(request, 'home.html', {'error': 'As alternativas não podem estar vazias.'})
                if alt['gabarito'] not in [True,False]:
                    error.append('O campo "gabarito" das alternativas deve ser True ou False.')
                    #return render(request, 'home.html', {'error': 'O campo "gabarito" das alternativas deve ser True ou False.'})
            
            if sum(1 for alt in jsonData['Alternativas'] if alt.get('gabarito')==True) != 1:
                error.append('Deve haver ao menos uma alternativa marcada como gabarito (True).')
                #return render(request, 'home.html', {'error': 'Deve haver ao menos uma alternativa marcada como gabarito (True).'})
        except Exception:
            error.append('Arquivo inválido.')
            #return render(request, 'home.html', {'error': 'Arquivo inválido.'})
        
        
       
        
        print('>>headerData',headerData)
        #generate_docx(headerData, jsonData)
        if error:
            return render(request, 'home.html', {'error': error})
        
        #teste     
        return render(request, 'home.html', {'success': 'Arquivo processado com sucesso!', 'data': jsonData})
        
    
        
    
    return render(request, 'home.html')

@login_required
def profile_view(request):
    template = loader.get_template('profile.html')
    return render(request, 'profile.html')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('home')




