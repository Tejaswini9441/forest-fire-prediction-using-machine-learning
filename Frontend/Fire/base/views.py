from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pandas as pd
import pickle
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
# Load the saved forest fire model
with open('forest_fire_model.pkl', 'rb') as model_file:
    saved_model = pickle.load(model_file)

# Retrieve the feature names used during model training
if hasattr(saved_model, 'feature_names_in_'):
    trained_columns = list(saved_model.feature_names_in_)
else:
    raise ValueError("The model does not store the feature names. Ensure you have the correct feature names.")

# Define possible months and days for one-hot encoding
MONTHS = [
    'month_jan', 'month_feb', 'month_mar', 'month_apr', 'month_may', 'month_jun',
    'month_jul', 'month_aug', 'month_sep', 'month_oct', 'month_nov', 'month_dec'
]

DAYS = [
    'day_mon', 'day_tue', 'day_wed', 'day_thu', 'day_fri', 'day_sat', 'day_sun'
]

def send_violence_email():
    subject = "HIGH LEVEL"
    message = "Please take immediate action to ensure safety. If the alert level is high, evacuate the area and contact emergency services immediately."
    from_email = 'abninfotechcse01@gmail.com'
    recipient_list = ['abninfotechprojects@gmail.com']  # Add recipient emails here
    send_mail(subject, message, from_email, recipient_list)
    print("Alert email sent successfully!")


def send_violence_email1():
    subject1 = "MEDIUM LEVEL"
    message1 = "Please take immediate action to ensure safety. If the alert level is medium, evacuate the area and contact emergency services immediately."
    from_email = 'abninfotechcse01@gmail.com'
    recipient_list = ['abninfotechprojects@gmail.com']  # Add recipient emails here
    send_mail(subject1, message1, from_email, recipient_list)
    print("Alert email sent successfully!")
    

def send_violence_email2():
    subject2 = "LOW LEVEL"
    message2 = "If the alert level is low, evacuate the area and contact emergency services immediately."
    from_email = 'abninfotechcse01@gmail.com'
    recipient_list = ['abninfotechprojects@gmail.com']  # Add recipient emails here
    send_mail(subject2, message2, from_email, recipient_list)
    print("Alert email sent successfully!")



def HomePage(request):
    return render(request, 'home.html')

def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Your password and confirm password do not match!")
        else:
            try:
                my_user = User.objects.create_user(uname, email, pass1)
                my_user.save()
                return redirect('login')
            except Exception as e:
                return HttpResponse(f"Error creating user: {e}")

    return render(request, 'signup.html')

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return HttpResponse("Username or Password is incorrect!")

    return render(request, 'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')

def get_fire_prediction(input_data):
    """
    Predicts the forest fire area based on input data.
    Args:
        input_data (dict): A dictionary containing the input features.
    Returns:
        prediction: The prediction result.
        alert: The alert level based on predicted area.
    """
    try:
        # Convert input dictionary to DataFrame
        input_df = pd.DataFrame([input_data])

        # Ensure the input matches the model's trained feature names
        if set(input_df.columns) != set(trained_columns):
            missing_cols = set(trained_columns) - set(input_df.columns)
            for col in missing_cols:
                input_df[col] = 0  # Add missing columns with default value 0

        # Reorder columns to match the training data
        input_df = input_df[trained_columns]

        # Make the prediction
        predicted_area = saved_model.predict(input_df)[0]

        # Determine alert level
        alert = alert_level(predicted_area)
        return predicted_area, alert
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None, "Error"

def alert_level(area):
    """ Determine the alert level based on predicted area. """
    if area < 10:
        send_violence_email2()
        return "Low"
    elif 10 <= area < 50:
        send_violence_email1()
        return "Medium"
    else:
        send_violence_email()
        return "High"

@csrf_exempt  # Use only if necessary. Prefer using CSRF tokens in your forms.
def result(request):
    if request.method == 'POST':
        try:
            # Extract input data from POST request
            X = float(request.POST.get('X'))
            Y = float(request.POST.get('Y'))
            FFMC = float(request.POST.get('FFMC'))
            DMC = float(request.POST.get('DMC'))
            DC = float(request.POST.get('DC'))
            ISI = float(request.POST.get('ISI'))
            temp = float(request.POST.get('temp'))
            RH = float(request.POST.get('RH'))
            wind = float(request.POST.get('wind'))
            rain = float(request.POST.get('rain'))

            month = request.POST.get('month').lower()
            day = request.POST.get('day').lower()

            # Initialize input data with numerical features
            input_data = {
                'X': X,
                'Y': Y,
                'FFMC': FFMC,
                'DMC': DMC,
                'DC': DC,
                'ISI': ISI,
                'temp': temp,
                'RH': RH,
                'wind': wind,
                'rain': rain
            }

            # One-hot encode 'month'
            for m in MONTHS:
                input_data[m] = 1 if m == f'month_{month}' else 0

            # One-hot encode 'day'
            for d in DAYS:
                input_data[d] = 1 if d == f'day_{day}' else 0

            # Get prediction and alert level
            predicted_area, alert = get_fire_prediction(input_data)

            if predicted_area is None:
                return HttpResponse("Error processing prediction.")

            return render(request, 'result.html', {
                'predicted_area': predicted_area,
                'alert_level': alert
            })
        except Exception as e:
            return HttpResponse(f"Error processing prediction: {e}")
    else:
        return HttpResponse("Invalid request method.")
