from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializers
from .models import User
import jwt, datetime

# Create your views here.

class RegisterView(APIView):
    # data is getting from requset
    def post(self, request):
        serializer = UserSerializers(data= request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email=email).first()  # Because email is unique

        if user is None:
            raise AuthenticationFailed ('User not found!')
        
        # Have to check password using check_password given by django, beacuse password is converted as hash already
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password!')
        

        payload = {
            'id':user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),  # make token for 60 minutes
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf=8')

        response = Response()

        # Now save the token in browser cookies
        response.set_cookie(key='jwt', value = token, httponly= True)
        response.data = {
            'jwt': token
        }

        return response
    
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthorised!')
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializers(user)

        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Success'
        }

        return response
