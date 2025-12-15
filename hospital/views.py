from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.conf import settings
from django.db.models import Q
from datetime import date, datetime



# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/index.html')


# -------- ADMIN CLICK (chọn đăng nhập admin)
def adminclick_view(request):
    # Nếu user đã đăng nhập và là admin -> chuyển thẳng đến dashboard admin
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin-dashboard')
    
    # Nếu user đăng nhập nhưng không phải admin -> logout để tránh lỗi redirect
    elif request.user.is_authenticated:
        from django.contrib.auth import logout
        logout(request)
        return redirect('login')

    # Nếu chưa đăng nhập -> hiển thị trang chọn login admin
    return render(request, 'hospital/adminclick.html')

#for showing signup/login button for doctor(by sumit)
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/doctorclick.html')


#for showing signup/login button for patient(by sumit)
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/patientclick.html')




def admin_signup_view(request):
    if request.method == 'POST':
        form = forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            my_admin_group, _ = Group.objects.get_or_create(name='ADMIN')
            my_admin_group.user_set.add(user)
            return redirect('adminlogin')
        else:
            print(form.errors)  # 👈 giúp debug trong terminal
    else:
        form = forms.AdminSigupForm()
    return render(request, 'hospital/adminsignup.html', {'form': form})




def doctor_signup_view(request):
    userForm = forms.DoctorUserForm()
    doctorForm = forms.DoctorForm()
    context = {'userForm': userForm, 'doctorForm': doctorForm}

    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST)
        doctorForm = forms.DoctorForm(request.POST, request.FILES)

        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()

            doctor = doctorForm.save(commit=False)
            doctor.user = user
            doctor.status = True      # tự động kích hoạt
            doctor.save()

            # thêm vào group DOCTOR
            group, created = Group.objects.get_or_create(name='DOCTOR')
            group.user_set.add(user)

            return HttpResponseRedirect('doctorlogin')
        else:
            print("User form errors:", userForm.errors)
            print("Doctor form errors:", doctorForm.errors)

    return render(request, 'hospital/doctorsignup.html', context)





def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient=patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'hospital/patientsignup.html',context=mydict)






#-----------for checking user is doctor , patient or admin(by sumit)
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


# -------- SAU KHI LOGIN XONG
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval = models.Doctor.objects.filter(user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request, 'hospital/doctor_wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval = models.Patient.objects.filter(user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request, 'hospital/patient_wait_for_approval.html')

    # ❌ Đừng redirect về adminclick nữa — sẽ lặp
    # ✅ Đưa về trang chủ hoặc login
    return redirect('login')







#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
# from web3 import Web3
# from datetime import datetime
# from django.contrib import messages
# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_dashboard_view(request):
#     doctors = models.Doctor.objects.all().order_by('-id')
#     patients = models.Patient.objects.all().order_by('-id')
#     doctorcount = doctors.filter(status=True).count()
#     pendingdoctorcount = doctors.filter(status=False).count()
#     patientcount = patients.filter(status=True).count()
#     pendingpatientcount = patients.filter(status=False).count()
#     appointmentcount = models.Appointment.objects.filter(status=True).count()
#     pendingappointmentcount = models.Appointment.objects.filter(status=False).count()

#     context = {
#         'doctors': doctors,
#         'patients': patients,
#         'doctorcount': doctorcount,
#         'pendingdoctorcount': pendingdoctorcount,
#         'patientcount': patientcount,
#         'pendingpatientcount': pendingpatientcount,
#         'appointmentcount': appointmentcount,
#         'pendingappointmentcount': pendingappointmentcount,
#         'bills': bills
#     }
#     return render(request, 'hospital/admin_dashboard.html', context)
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from . import models  # hoặc từ app cụ thể import models nếu cần

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    doctors = models.Doctor.objects.all().order_by('-id')
    patients = models.Patient.objects.all().order_by('-id')
    doctorcount = doctors.filter(status=True).count()
    pendingdoctorcount = doctors.filter(status=False).count()
    patientcount = patients.filter(status=True).count()
    pendingpatientcount = patients.filter(status=False).count()
    appointmentcount = models.Appointment.objects.filter(status=True).count()
    pendingappointmentcount = models.Appointment.objects.filter(status=False).count()

    # ✅ Thay thế blockchain = MySQL query
    discharge_records = models.PatientDischargeDetails.objects.all().order_by('-id')
    
    bills = []
    for record in discharge_records:
        bills.append({
            'patientId': record.patientId,
            'patientName': record.patientName,
            'assignedDoctorName': record.assignedDoctorName,
            'addressDetail': record.address,
            'mobile': record.mobile,
            'symptoms': record.symptoms,
            'admitDate': record.admitDate.strftime('%d-%m-%Y') if record.admitDate else '',
            'releaseDate': record.releaseDate.strftime('%d-%m-%Y') if record.releaseDate else '',
            'daySpent': record.daySpent,
            'medicineCost': record.medicineCost,
            'roomCharge': record.roomCharge,
            'doctorFee': record.doctorFee,
            'otherCharge': record.OtherCharge,
            'total': record.total,
        })

    context = {
        'doctors': doctors,
        'patients': patients,
        'doctorcount': doctorcount,
        'pendingdoctorcount': pendingdoctorcount,
        'patientcount': patientcount,
        'pendingpatientcount': pendingpatientcount,
        'appointmentcount': appointmentcount,
        'pendingappointmentcount': pendingappointmentcount,
        'bills': bills,
    }
    return render(request, 'hospital/admin_dashboard.html', context)





# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request,'hospital/admin_doctor.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)

    userForm = forms.DoctorUserForm(instance=user)
    doctorForm = forms.DoctorForm(instance=doctor)

    mydict = {'userForm': userForm, 'doctorForm': doctorForm}

    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST, instance=user)
        doctorForm = forms.DoctorForm(request.POST, request.FILES, instance=doctor)

        # Debug xem lỗi gì
        if not userForm.is_valid():
            print("User form errors:", userForm.errors)
        if not doctorForm.is_valid():
            print("Doctor form errors:", doctorForm.errors)

        # LƯU Ý: phải dùng AND để chắc chắn hợp lệ trước khi save
        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()

            doctor = doctorForm.save(commit=False)
            doctor.status = True
            doctor.save()

            return redirect('admin-view-doctor')

    return render(request, 'hospital/admin_update_doctor.html', context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request,'hospital/admin_add_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_doctor.html',{'doctors':doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors = models.Doctor.objects.all()   # KHÔNG lọc status nữa
    return render(request, 'hospital/admin_view_doctor_specialisation.html', {'doctors': doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request,'hospital/admin_patient.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)

    userForm=forms.PatientUserForm(instance=user)
    patientForm=forms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request,'hospital/admin_update_patient.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'hospital/admin_add_patient.html',context=mydict)



#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')



#--------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_discharge_patient.html',{'patients':patients})



# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def discharge_patient_view(request,pk):
#     patient=models.Patient.objects.get(id=pk)
#     days=(date.today()-patient.admitDate) #2 days, 0:00:00
#     assignedDoctor=models.User.objects.all().filter(id=patient.assignedDoctorId)
#     d=days.days # only how many day that is 2
#     patientDict={
#         'patientId':pk,
#         'name':patient.get_name,
#         'mobile':patient.mobile,
#         'address':patient.address,
#         'symptoms':patient.symptoms,
#         'admitDate':patient.admitDate,
#         'todayDate':date.today(),
#         'day':d,
#         'assignedDoctorName':assignedDoctor[0].first_name,
#     }
#     if request.method == 'POST':
#         feeDict ={
#             'roomCharge':int(request.POST['roomCharge'])*int(d),
#             'doctorFee':request.POST['doctorFee'],
#             'medicineCost' : request.POST['medicineCost'],
#             'OtherCharge' : request.POST['OtherCharge'],
#             'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
#         }
#         patientDict.update(feeDict)
#         #for updating to database patientDischargeDetails (pDD)
#         pDD=models.PatientDischargeDetails()
#         pDD.patientId=pk
#         pDD.patientName=patient.get_name
#         pDD.assignedDoctorName=assignedDoctor[0].first_name
#         pDD.address=patient.address
#         pDD.mobile=patient.mobile
#         pDD.symptoms=patient.symptoms
#         pDD.admitDate=patient.admitDate
#         pDD.releaseDate=date.today()
#         pDD.daySpent=int(d)
#         pDD.medicineCost=int(request.POST['medicineCost'])
#         pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
#         pDD.doctorFee=int(request.POST['doctorFee'])
#         pDD.OtherCharge=int(request.POST['OtherCharge'])
#         pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
#         pDD.save()
#         return render(request,'hospital/patient_final_bill.html',context=patientDict)
#     return render(request,'hospital/patient_generate_bill.html',context=patientDict)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.contrib import messages
from datetime import date, datetime
from . import models
from web3 import Web3
import json
import os
from django.http import JsonResponse





INFURA_URL = "https://sepolia.infura.io/v3/d756282887684fd18e04e0b2c4a355dd"
PRIVATE_KEY = "9609eef6fd4011b533be913a5bc4cd6a9e6f40959febed0ba0f02758920c57b7"  # Của người gửi (phải khớp với ví deploy hoặc ví kết nối)
PUBLIC_ADDRESS = "0x2aEbeD4C34b0b296F5A42859F53f1C1F44f1ba2d"

# Kết nối Web3
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Load ABI
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "static", "contract_ABI.json")) as f:
    contract_json = json.load(f)
    abi = contract_json

# Địa chỉ contract
contract_address = Web3.to_checksum_address("0xb346639709EEe160a66f98cAef43bc28dDD19FC4")

# Tạo đối tượng contract
contract = w3.eth.contract(address=contract_address, abi=abi)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    days = (date.today() - patient.admitDate)
    assignedDoctor = models.User.objects.filter(id=patient.assignedDoctorId)
    d = days.days

    patientDict = {
        'patientId': pk,
        'name': patient.get_name,
        'mobile': patient.mobile,
        'address': patient.address,
        'symptoms': patient.symptoms,
        'admitDate': patient.admitDate,
        'todayDate': date.today(),
        'day': d,
        'assignedDoctorName': assignedDoctor[0].first_name if assignedDoctor else '',
    }

    if request.method == 'POST':
        room_charge_per_day = int(request.POST['roomCharge'])
        doctor_fee = int(request.POST['doctorFee'])
        medicine_cost = int(request.POST['medicineCost'])
        other_charge = int(request.POST['OtherCharge'])
        room_charge_total = room_charge_per_day * d
        total_fee = room_charge_total + doctor_fee + medicine_cost + other_charge

        feeDict = {
            'roomCharge': room_charge_total,
            'doctorFee': doctor_fee,
            'medicineCost': medicine_cost,
            'OtherCharge': other_charge,
            'total': total_fee
        }
        patientDict.update(feeDict)

        # Save to local DB
        pDD = models.PatientDischargeDetails()
        pDD.patientId = pk
        pDD.patientName = patient.get_name
        pDD.assignedDoctorName = assignedDoctor[0].first_name if assignedDoctor else ''
        pDD.address = patient.address
        pDD.mobile = patient.mobile
        pDD.symptoms = patient.symptoms
        pDD.admitDate = patient.admitDate
        pDD.releaseDate = date.today()
        pDD.daySpent = d
        pDD.medicineCost = medicine_cost
        pDD.roomCharge = room_charge_total
        pDD.doctorFee = doctor_fee
        pDD.OtherCharge = other_charge
        pDD.total = total_fee
        pDD.save()

        # Chuyển đổi ngày sang timestamp
        admit_timestamp = int(datetime.combine(patient.admitDate, datetime.min.time()).timestamp())
        release_timestamp = int(datetime.combine(date.today(), datetime.min.time()).timestamp())

        # Gửi lên blockchain
        try:
            print("🔍 Dữ liệu gửi lên contract:")
            print("🔗 Trạng thái kết nối Web3 trước estimate:", w3.is_connected())
            print(f"patientId: {pk}, name: {patient.get_name}, doctor: {assignedDoctor[0].first_name if assignedDoctor else ''}")
            print(f"address: {patient.address}, mobile: {patient.mobile}, symptoms: {patient.symptoms}")
            print(f"admit: {admit_timestamp}, release: {release_timestamp}, days: {d}")
            print(f"costs: {medicine_cost}, {room_charge_total}, {doctor_fee}, {other_charge}")

            # Ước lượng gas
            gas_estimate = contract.functions.createBill(
                int(pk),
                patient.get_name,
                assignedDoctor[0].first_name if assignedDoctor else '',
                patient.address,
                patient.mobile,
                patient.symptoms,
                admit_timestamp,
                release_timestamp,
                d,
                medicine_cost,
                room_charge_total,
                doctor_fee,
                other_charge
            ).estimate_gas({'from': PUBLIC_ADDRESS})
            print(f"Gas estimate: {gas_estimate}")
            # Lấy nonce
            nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
            print("Kết nối Web3:", w3.is_connected())
            print("Current nonce:", nonce)

            # Xây dựng giao dịch với gas estimate + 20% margin
            gas_with_margin = int(gas_estimate * 1.2)  # Tăng 20%
            tx = contract.functions.createBill(
                int(pk),
                patient.get_name,
                assignedDoctor[0].first_name,
                patient.address,
                patient.mobile,
                patient.symptoms,
                admit_timestamp,
                release_timestamp,
                d,
                medicine_cost,
                room_charge_total,
                doctor_fee,
                other_charge
            ).build_transaction({
                'from': PUBLIC_ADDRESS,
                'nonce': nonce,
                'gas': gas_with_margin,
                'gasPrice': w3.to_wei('50', 'gwei')
            })

            # Ký và gửi giao dịch
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # In log debug từ contract
            logs = contract.events.DebugLog().process_receipt(tx_receipt)
            for log in logs:
                print(f"DebugLog: {log.args.message} = {log.args.value}")

            print("Status:", tx_receipt.status)  # 1 = success

            if tx_receipt.status == 1:
                try:
                    logs = contract.events.BillCreated().process_receipt(tx_receipt)
                    print("📦 Events:", logs)
                except Exception as event_error:
                    print("⚠️ Không thể đọc sự kiện:", str(event_error))

                messages.success(request, f"Hóa đơn đã được lưu lên blockchain thành công. Tx Hash: {tx_hash.hex()}")
                patientDict['tx_hash'] = tx_hash.hex()
            else:
                raise Exception("Giao dịch đã bị revert (status = 0). Kiểm tra logic smart contract.")

        except Exception as e:
            error_message = f"Lỗi khi gửi dữ liệu lên blockchain: {str(e)}"
            print(error_message)
            messages.error(request, error_message)
            patientDict['tx_error'] = error_message

        return render(request, 'hospital/patient_final_bill.html', context=patientDict)

    return render(request, 'hospital/patient_generate_bill.html', context=patientDict)



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request,pk):
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={
        'patientName':dischargeDetails[0].patientName,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'symptoms':dischargeDetails[0].symptoms,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('hospital/download_bill.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'hospital/admin_appointment.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_appointment.html',{'appointments':appointments})



# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_add_appointment_view(request):
#     appointmentForm=forms.AppointmentForm()
#     mydict={'appointmentForm':appointmentForm,}
#     if request.method=='POST':
#         appointmentForm=forms.AppointmentForm(request.POST)
#         if appointmentForm.is_valid():
#             appointment=appointmentForm.save(commit=False)
#             appointment.doctorId=request.POST.get('doctorId')
#             appointment.patientId=request.POST.get('patientId')
#             appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
#             appointment.patientName=models.User.objects.get(id=request.POST.get('patientId')).first_name
#             appointment.status=True
#             appointment.save()
#         return HttpResponseRedirect('admin-view-appointment')
#     return render(request,'hospital/admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    if request.method == 'POST':
        form = forms.AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            doctor_id = request.POST.get('doctorId')
            patient_id = request.POST.get('patientId')

            # Gán các giá trị còn lại
            appointment.doctorId = doctor_id
            appointment.patientId = patient_id
            appointment.doctorName = models.User.objects.get(id=doctor_id).first_name
            appointment.patientName = models.User.objects.get(id=patient_id).first_name
            appointment.status = True
            appointment.save()
            return HttpResponseRedirect('admin-view-appointment')
    else:
        form = forms.AppointmentForm()

    return render(request, 'hospital/admin_add_appointment.html', {'appointmentForm': form})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    #for three cards
    patientcount=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_dashboard.html',context=mydict)



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_patient.html',context=mydict)





@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def search_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    dischargedpatients=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_appointment.html',{'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    doctor=models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    mydict={
    'patient':patient,
    'doctorName':doctor.get_name,
    'doctorMobile':doctor.mobile,
    'doctorAddress':doctor.address,
    'symptoms':patient.symptoms,
    'doctorDepartment':doctor.department,
    'admitDate':patient.admitDate,
    }
    return render(request,'hospital/patient_dashboard.html',context=mydict)



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_appointment.html',{'patient':patient})



# @login_required(login_url='patientlogin')
# @user_passes_test(is_patient)
# def patient_book_appointment_view(request):
#     appointmentForm=forms.PatientAppointmentForm()
#     patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
#     message=None
#     mydict={'appointmentForm':appointmentForm,'patient':patient,'message':message}
#     if request.method=='POST':
#         appointmentForm=forms.PatientAppointmentForm(request.POST)
#         if appointmentForm.is_valid():
#             print(request.POST.get('doctorId'))
#             desc=request.POST.get('description')

#             doctor=models.Doctor.objects.get(user_id=request.POST.get('doctorId'))
            
#             appointment=appointmentForm.save(commit=False)
#             appointment.doctorId=request.POST.get('doctorId')
#             appointment.patientId=request.user.id #----user can choose any patient but only their info will be stored
#             appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
#             appointment.patientName=request.user.first_name #----user can choose any patient but only their info will be stored
#             appointment.status=False
#             appointment.save()
#         return HttpResponseRedirect('patient-view-appointment')
#     return render(request,'hospital/patient_book_appointment.html',context=mydict)


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)  # lấy patient hiện tại
    message = None

    if request.method == 'POST':
        appointmentForm = forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment = appointmentForm.save(commit=False)

            doctor = appointmentForm.cleaned_data['doctorId']  # lấy đối tượng Doctor từ form
            appointment.doctorId = doctor.user_id  # gán doctorId là số user_id
            appointment.patientId = patient.user_id  # gán patientId từ patient hiện tại

            # Lấy tên bác sĩ và bệnh nhân
            appointment.doctorName = doctor.user.get_full_name() or doctor.user.first_name
            appointment.patientName = request.user.get_full_name() or request.user.first_name

            appointment.status = False
            appointment.save()

            message = "Đặt lịch thành công!"
            # reset form sau khi lưu thành công
            appointmentForm = forms.PatientAppointmentForm()
        else:
              print(appointmentForm.errors)  # thêm dòng này để xem lỗi
              message = "Thông tin không hợp lệ. Vui lòng kiểm tra lại."

        return render(request, 'hospital/patient_book_appointment.html', {
            'appointmentForm': appointmentForm,
            'patient': patient,
            'message': message
        })

    else:
        appointmentForm = forms.PatientAppointmentForm()

    return render(request, 'hospital/patient_book_appointment.html', {
        'appointmentForm': appointmentForm,
        'patient': patient,
        'message': message
    })


def patient_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})



def search_doctor_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors=models.Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})




@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'hospital/patient_view_appointment.html',{'appointments':appointments,'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'patient':patient,
        'patientId':patient.id,
        'patientName':patient.get_name,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'mobile':patient.mobile,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict={
            'is_discharged':False,
            'patient':patient,
            'patientId':request.user.id,
        }
    return render(request,'hospital/patient_discharge.html',context=patientDict)


#------------------------ PATIENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------








#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START ------------------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'hospital/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'hospital/contactussuccess.html')
    return render(request, 'hospital/contactus.html', {'form':sub})


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------



# statistic
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import io, base64
import pandas as pd
from datetime import datetime, timedelta
from django.shortcuts import render
from .models import PatientDischargeDetails

def stacked_area_chart(request):
    discharge_records = PatientDischargeDetails.objects.all().values(
        'releaseDate', 'medicineCost', 'roomCharge', 'doctorFee', 'OtherCharge'
    )

    df = pd.DataFrame(discharge_records)

    if df.empty:
        return render(request, 'hospital/admin_chart.html',
                      {'chart_matplotlib': None, 'message': 'Không có dữ liệu để hiển thị.'})

    # Chuyển releaseDate thành date
    df['releaseDate'] = pd.to_datetime(df['releaseDate']).dt.date

    # Lọc 7 ngày gần nhất
    today = datetime.today().date()
    seven_days_ago = today - timedelta(days=6)

    df = df[df['releaseDate'].between(seven_days_ago, today)]

    if df.empty:
        return render(request, 'hospital/admin_chart.html',
                      {'chart_matplotlib': None, 'message': 'Không có dữ liệu trong 7 ngày gần đây.'})

    # Nhóm theo ngày, tính tổng
    df_grouped = df.groupby('releaseDate').sum().reset_index()

    dates = df_grouped['releaseDate']
    medicine = df_grouped['medicineCost']
    room = df_grouped['roomCharge']
    doctor = df_grouped['doctorFee']
    other = df_grouped['OtherCharge']

    # Vẽ stacked bar chart biểu đồ cột chồng
    plt.figure(figsize=(10, 5))
    plt.bar(dates, medicine, label='Medicine Cost')
    plt.bar(dates, room, bottom=medicine, label='Room Charge')
    plt.bar(dates, doctor, bottom=medicine+room, label='Doctor Fee')
    plt.bar(dates, other, bottom=medicine+room+doctor, label='Other Charge')

    plt.title("Biểu đồ chi phí bệnh viện - 7 ngày gần nhất")
    plt.xlabel("Ngày xuất viện")
    plt.ylabel("Chi phí (VNĐ)")
    plt.xticks(rotation=45)
    plt.legend()

    # Xuất ảnh sang base64
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graphic = base64.b64encode(image_png).decode('utf-8')
    buffer.close()
    plt.close()

    return render(request, 'hospital/admin_chart.html',
                  {'chart_matplotlib': graphic, 'message': None})

