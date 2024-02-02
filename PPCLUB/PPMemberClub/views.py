from django.http import HttpResponse
from django.shortcuts import render, redirect

from .info import EMAIL_HOST_USER
from .forms import CreateUserForm, LoginForm, CreateMemberData, UpdateMemberData, CreateMemberFamilyData, UpdateMemberFamilyData, CreateMemberAddressData, UpdateMemberAddressData, CreateMemberBusinessData, UpdateMemberBusinessData, ProposedMemberDataForm, ProposedMemberFamilyDataForm, ProposedMemberAddressDataForm, ProposedMemberBusinessDataForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from .models import MemberData, MemberFamilyData, MemberAddressData, MemberBusinessData, ProposedMemberData
from django.contrib import messages
from .decorator import unauthenticated_user, allowed_users
from django.contrib.auth.models import Group

from django.forms.models import model_to_dict

from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.core.mail import EmailMessage



def Home(request):
    #return HttpResponse('Hey there...')
    return render(request, 'PPMemberClub/index.html')


#############################################################################################################################################################################################

# - Register a user
@unauthenticated_user
def register(request):

    form = CreateUserForm()

    if request.method == "POST":

        form = CreateUserForm(request.POST)

        if form.is_valid():

            #this below code is to check new freshly entered username with the existing usernames.
            # if user.objects.filter(username=username):
            #     messages.error(request, "Username already exists, try some other name....")
            #     return redirect("index")
            
            # if user.objects.filter(email=email):
            #     messages.error(request, "Email Id already exists, try some other Id....")
            #     return redirect("index")

            #by default the new user joined will not be active. he will be activated as soon as he opens the confirmation link send on the mail of the user.
            form.instance.is_active = False
            user = form.save()
            
            group = Group.objects.get(name='NormalUsers')
            user.groups.add(group)
            
            #this below code is to extract username and show in messages when new user register.
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            messages.success(request, 'Account created successfully! Welcome ' + username + 'please check your mail to confirm Email-Address.')

            #this below code is for Email Confirmation.
            subject = "Welcome to Pitam-Pura Members Club!!"
            message = "Thank you for visiting our website.\nWe have sent you an comfirmation Email, please check your inbox in order to confirm it."
            from_email = EMAIL_HOST_USER
            print(from_email)
            to_list = [email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            #this below code is to send unique confirmation link to the user mail account.
            current_site = get_current_site(request)
            email_subject = "Confirm your Email Address @gmail login!"
            message1 = render_to_string('email-confirmation.html',
            {
                'name' : username,
                'domain' : current_site.domain,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : generate_token.make_token(user),
            })

            email = EmailMessage(
                email_subject,
                message1,
                EMAIL_HOST_USER,
                [email],
            )
            email.fail_silently = True
            email.send()

            return redirect("my-login")

    context = {'form':form}
    return render(request, 'PPMemberClub/register.html', context=context)



# To activate the user when he confirm the Email Address via mail....

def activate(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = user.objects.get(pk = uid)
    if user.DoesNotExist:
        user = None
    
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        my_login(request, user)
        
    else:
        return render(request,'activation-failed.html')




# - Login a user

def my_login(request):

    form = LoginForm()

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                messages.success(request, 'Successfully Logged in!!')
                return redirect("dashboard")    

    context = {'form':form}

    return render(request, 'PPMemberClub/my-login.html', context=context)



# - User logout

def user_logout(request):

    auth.logout(request)

    messages.success(request, "Logout successfully!")

    return redirect("my-login")




# - User Dashboard

@login_required(login_url='my-login')
def dashboard(request):

    my_records = MemberData.objects.all()

    context = {'records': my_records}

    return render(request, 'PPMemberClub/dashboard.html', context=context)



#############################################################################################################################################################################################


#- View Memberdata

@login_required(login_url='my-login')
def view_member(request, pk):

    my_records = MemberData.objects.get(id=pk)

    context = {'form' : my_records}

    return render(request, 'PPMemberClub/view-member.html', context=context)



# - Create new member data

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])

def create_member(request):

    form1 = CreateMemberData()
    form2 = CreateMemberFamilyData()
    form3 = CreateMemberAddressData()
    form4 = CreateMemberBusinessData()
    if request.method == "POST":

        form1 = CreateMemberData(request.POST, request.FILES)
        form2 = CreateMemberFamilyData(request.POST)
        form3 = CreateMemberAddressData(request.POST)
        form4 = CreateMemberBusinessData(request.POST)

        if form1.is_valid() and form2.is_valid() and form3.is_valid() and form4.is_valid():
            member = form1.save()

            form2.instance.member_id = member.id
            form2.save()

            form3.instance.member_id = member.id
            form3.save()

            form4.instance.member_id = member.id
            form4.save()  

            messages.success(request, "Your record was created!")
            
            return redirect('dashboard')
        
        else:
            print(form1.errors)

        

    context = {'mform' : form1, 'mfform' : form2, 'maform' : form3, 'mbform' : form4}

    return render(request, 'PPMemberClub/create-member.html', context=context)



# - Update existing member data

@login_required(login_url='my-login')

def update_member(request, pk):
    record = MemberData.objects.get(id=pk)

    # fields_to_copy = ['Fullname', 'Email', 'Dob', 'Resphone', 'Altermobileno', 'Resaddress', 'Officeno', 'Country', 'Profilepic', 'Signature']

    # form_data = {field: getattr(record, field) for field in fields_to_copy}

    form_data = model_to_dict(record)

    form = UpdateMemberData(request.POST or None, instance=record)

    form1 = ProposedMemberDataForm(request.POST or None, initial=form_data, instance=ProposedMemberData())

    if request.method == "POST":
        if request.user.is_superuser:
            form = UpdateMemberData(request.POST, instance=record)
            if form.is_valid():
                form.save()
                return redirect("dashboard")
            else:
                print(form.errors)

        elif request.user.username == 'FrontDesk':
            if form1.is_valid():
                form1.instance.proposed_memberdata_id = record.id
                form1.save()
                return redirect("dashboard")
            else:
                print(form1.errors)

    if request.user.is_superuser :
        context = {'form': form} 
    else :
        context = {'form': form1}
    return render(request, 'PPMemberClub/update-member.html', context=context)




# - FrontDesk User Update Permission / Proposed data ready to be Accept or Reject.

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])

def proposed_memberdata(request, pk):
    proposeddata = ProposedMemberData.objects.get(proposed_memberdata_id=pk)

    if proposeddata is None or ProposedMemberData.DoesNotExist:
        return render(request, 'PPMemberClub/pending.html')
    else :
        memberdata = MemberData.objects.get(id=pk)
        form2 = UpdateMemberData(request.GET or None, instance=memberdata)
        
        form_data = model_to_dict(proposeddata)

        form1 = ProposedMemberDataForm(request.GET or None, instance=proposeddata)

        if request.method == 'POST':
            form2 = UpdateMemberData(request.POST, initial=form_data, instance=memberdata)
            if form2.is_valid():
                form2.save()
                proposeddata.delete()
                return redirect("dashboard")


        context = {'form1': form1, 'form2': form2}
        return render(request, 'PPMemberClub/proposedmemberdata.html', context)



@login_required(login_url='my-login')
def pending(request):

    return HttpResponse("There is no Pendeing Request left.... please go back!")



# - Delete a Proposed Table record

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])
def delete_proposedmember(request, pk):

    proposeddata = ProposedMemberData.objects.get(id=pk)

    proposeddata.delete()

    messages.success(request, "Proposed data request was deleted!")

    return redirect("dashboard")



# - Delete a record

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])
def delete_member(request, pk):

    record = MemberData.objects.get(id=pk)

    record.delete()

    messages.success(request, "Your record was deleted!")

    return redirect("dashboard")



#############################################################################################################################################################################################



# - View Member-Family details

@login_required(login_url='my-login')
def view_memberfamily(request, pk):

    my_records = MemberFamilyData.objects.get(member_id=pk)

    if my_records:
        context = {'record': my_records}
        return render(request, 'PPMemberClub/view-memberfamily.html', context=context)
    else:
        return redirect('create-memberfamily', pk=pk)



# Create Member-Family Details

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])
def create_memberfamily(request):

    form = CreateMemberFamilyData()

    if request.method == "POST":

        form = CreateMemberFamilyData(request.POST)

        if form.is_valid():
            
            form.save()
            
            return redirect("dashboard")
        
        else:

            print(form.errors)

    context = {'form' : form}

    return render(request, 'PPMemberClub/create-memberfamily.html', context=context)



# - Update existing member family data

@login_required(login_url='my-login')

def update_memberfamily(request, pk):

    record = MemberFamilyData.objects.get(id=pk)

    form_data = model_to_dict(record)

    form = UpdateMemberFamilyData(request.POST or None, instance=record)

    form1 = ProposedMemberFamilyDataForm(request.POST or None, initial=form_data, instance=ProposedMemberData())

    if request.method == "POST":
        if request.user.is_superuser:
            form = UpdateMemberFamilyData(request.POST or None, instance=record)
            if form.is_valid():
                form.save()
                return redirect("dashboard")
            else:
                print(form.errors)


        elif request.user.username == 'FrontDesk':
            if form1.is_valid():
                form1.instance.proposed_memberfamilydata_id = record.id
                form1.save()
                return redirect("dashboard")
            else:
                print(form1.errors)

    if request.user.is_superuser :
        context = {'form': form} 
    else :
        context = {'form': form1}

    return render(request, 'PPMemberClub/update-memberfamily.html', context=context)





    
# - FrontDesk User Update Permission / Proposed data ready to be Accept or Reject.

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])
def proposed_memberfamilydata(request, pk):
    proposeddata = ProposedMemberData.objects.get(proposed_memberfamilydata_id=pk)
    if not(proposeddata):
        return redirect("dashboard")
    
    memberfamilydata = MemberFamilyData.objects.get(id=pk)
    
    form1 = ProposedMemberFamilyDataForm(request.POST or None, instance=proposeddata)

    form_data = model_to_dict(proposeddata)

    form2 = UpdateMemberFamilyData(request.POST or None, instance=memberfamilydata)

    if request.method == 'POST':
        form2 = UpdateMemberFamilyData(request.POST or None, initial=form_data, instance=memberfamilydata)
        if form2.is_valid():
            form2.save()
            proposeddata.delete()
            return redirect("dashboard")


    context = {'form1': form1, 'form2': form2}
    return render(request, 'PPMemberClub/proposedmemberfamilydata.html', context)



#############################################################################################################################################################################################



# - View Member-Address details

@login_required(login_url='my-login')
def view_memberaddress(request, pk):

    my_records = MemberAddressData.objects.get(member_id=pk)

    if my_records:
        context = {'record': my_records}
        return render(request, 'PPMemberClub/view-memberaddress.html', context=context)
    


# Create Member-Address Details

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])
def create_memberaddress(request):

    form = CreateMemberAddressData()

    if request.method == "POST":

        form = CreateMemberAddressData(request.POST)

        if form.is_valid():
            
            form.save()
            
            return redirect("dashboard")
        
        else:

            print(form.errors)

    context = {'form' : form}

    return render(request, 'PPMemberClub/create-memberaddress.html', context=context)



# - Update existing member family data

@login_required(login_url='my-login')

def update_memberaddress(request, pk):

    record = MemberAddressData.objects.get(id=pk)

    form = UpdateMemberAddressData(request.POST or None, instance=record)

    form_data = model_to_dict(record)

    form1 = ProposedMemberAddressDataForm(request.POST or None, initial=form_data, instance=ProposedMemberData())

    if request.method == "POST":
        if request.user.is_superuser:
            form = UpdateMemberAddressData(request.POST, instance=record)
            if form.is_valid():
                form.save()
                return redirect("dashboard")
            else:
                print(form.errors)

        elif request.user.username == 'FrontDesk':
            if form1.is_valid():
                form1.instance.proposed_memberaddressdata_id = record.id
                form1.save()
                return redirect("dashboard")
            else:
                print(form1.errors)

    if request.user.is_superuser :
        context = {'form': form} 
    else :
        context = {'form': form1}

    return render(request, 'PPMemberClub/update-memberaddress.html', context=context)




# - FrontDesk User Update Permission / Proposed data ready to be Accept or Reject.

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])

def proposed_memberaddressdata(request, pk):
    proposeddata = ProposedMemberData.objects.get(proposed_memberaddressdata_id=pk)
    
    memberaddressdata = MemberAddressData.objects.get(id=pk)

    form1 = ProposedMemberAddressDataForm(request.POST or None, instance=proposeddata)

    form_data = model_to_dict(proposeddata)

    form2 = UpdateMemberAddressData(request.POST or None, instance=memberaddressdata)

    if request.method == 'POST':
        form2 = UpdateMemberAddressData(request.POST or None, initial=form_data, instance=memberaddressdata)
        if form2.is_valid():
            form2.save()
            proposeddata.delete()
            return redirect("dashboard")


    context = {'form1': form1, 'form2': form2}
    return render(request, 'PPMemberClub/proposedmemberaddressdata.html', context)



#############################################################################################################################################################################################



# - View Member-Business details

@login_required(login_url='my-login')
def view_memberbusiness(request, pk):

    my_records = MemberBusinessData.objects.get(member_id=pk)

    if my_records:
        context = {'record': my_records}
        return render(request, 'PPMemberClub/view-memberbusiness.html', context=context)
    


# Create Member-Address Details

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])
def create_memberbusiness(request):

    form = CreateMemberBusinessData()

    if request.method == "POST":

        form = CreateMemberBusinessData(request.POST)

        if form.is_valid():
            
            form.save()
            
            return redirect("dashboard")
        
        else:

            print(form.errors)

    context = {'form' : form}

    return render(request, 'PPMemberClub/create-memberbusiness.html', context=context)



# - Update existing member family data

@login_required(login_url='my-login')

def update_memberbusiness(request, pk):

    record = MemberBusinessData.objects.get(id=pk)

    fields_to_copy = ['Businessname', 'Businessdetails', 'Businessaddress', 'Businesscity', 'Businessemail', 'Businesspostalcode']

    form_data = {field: getattr(record, field) for field in fields_to_copy}

    form = UpdateMemberBusinessData(request.POST or None, instance=record)

    form1 = ProposedMemberBusinessDataForm(request.POST or None, initial=form_data, instance=ProposedMemberData())

    if request.method == "POST":
        if request.user.is_superuser:
            form = UpdateMemberBusinessData(request.POST, instance=record)
            if form.is_valid():
                form.save()
                return redirect("dashboard")
            else:
                print(form.errors)

        elif request.user.username == 'FrontDesk':
            if form1.is_valid():
                form1.instance.proposed_memberbusinessdata_id = record.id
                form1.save()
                return redirect("dashboard")
            else:
                print(form1.errors)

    if request.user.is_superuser :
        context = {'form': form} 
    else :
        context = {'form': form1}

    return render(request, 'PPMemberClub/update-memberbusiness.html', context=context)





# - FrontDesk User Update Permission / Proposed data ready to be Accept or Reject.

@login_required(login_url='my-login')
@allowed_users(allowed_roles=['SuperUsers'])

def proposed_memberbusinessdata(request, pk):
    proposeddata = ProposedMemberData.objects.get(proposed_memberbusinessdata_id=pk)
    if not(proposeddata):
        return redirect("dashboard")
    memberbusinessdata = MemberBusinessData.objects.get(id=pk)

    fields_to_copy = ['Businessname', 'Businessdetails', 'Businessaddress', 'Businesscity', 'Businessemail', 'Businesspostalcode']

    form_data = {field: getattr(proposeddata, field) for field in fields_to_copy}

    form1 = ProposedMemberBusinessDataForm(request.POST or None, instance=proposeddata)

    form2 = UpdateMemberBusinessData(request.POST or None, instance=memberbusinessdata)
    if request.method == 'POST':
        form2 = UpdateMemberBusinessData(request.POST or None, initial=form_data, instance=memberbusinessdata)
        if form2.is_valid():
            form2.save()
            proposeddata.delete()
            return redirect("dashboard")


    context = {'form1': form1, 'form2': form2}
    return render(request, 'PPMemberClub/proposedmemberbusinessdata.html', context)

    

#############################################################################################################################################################################################
