from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from tasks.pagination import CustomPagination
from tasks.models import User
from tasks.models import Task
from .serializers import LoginSerializer, TaskSerializer, UserSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny

from drf_yasg import openapi
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
import logging
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q


class RegisterView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    logger = logging.getLogger(__name__)

    def post(self, request):
        self.logger.debug("Login attempt received.")

        email = request.data.get("email")
        password = request.data.get("password")
        self.logger.info(f"Login request for email: {email}")

        if not email or not password:
            self.logger.error("Email or password not provided.")
            raise AuthenticationFailed("Email and password are required.")

        try:

            user = User.objects.get(email=email)
            self.logger.debug(f"User found: {user.email}")

            if not user.is_active:
                self.logger.warning(f"Inactive user login attempt: {email}")
                raise AuthenticationFailed("User account is inactive.")

            # Verify password
            if not check_password(password, user.password):
                self.logger.warning(f"Password mismatch for user: {email}")
                raise AuthenticationFailed("Invalid credentials.")

            self.logger.info(f"Password verified for user: {email}")

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            self.logger.info(f"JWT tokens successfully generated for user: {email}")

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            self.logger.error(f"Login failed. User does not exist for email: {email}")
            raise AuthenticationFailed("Invalid credentials.")
        except Exception as e:
            self.logger.exception(
                f"Unexpected error during login for {email}: {str(e)}"
            )
            raise AuthenticationFailed(
                "An unexpected error occurred. Please try again."
            )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:

            page_size = int(request.data.get("page_size", 10))
            page_number = int(request.data.get("page_number", 1))
            search_query = request.data.get("search")

            queryset = User.objects.all()

            if search_query:
                queryset = queryset.filter(
                    Q(email__icontains=search_query)
                    | Q(first_name__icontains=search_query)
                    | Q(last_name__icontains=search_query)
                )

            paginator = Paginator(queryset, page_size)
            try:
                page_obj = paginator.page(page_number)
            except EmptyPage:
                return Response(
                    {"status": "fail", "message": "Page not found.", "data": {}},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = UserSerializer(
                page_obj.object_list, many=True, context={"request": request}
            )

            response_data = {
                "total_pages": paginator.num_pages,
                "current_page": page_obj.number,
                "total_items": paginator.count,
                "results": serializer.data,
            }

            return Response(
                {
                    "status": "success",
                    "message": "User retrieved successfully",
                    "data": response_data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Task Created successfully",
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskListUpdate(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request):
        task_id = request.data.get("id")
        if not task_id:
            return Response(
                {"status": "fail", "message": "Task ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {"status": "fail", "message": "Task not found.", "data": {}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Task updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "fail",
                "message": "Validation errors",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class TaskListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        try:
            # Fetch data from request.data
            page_size = int(request.data.get("page_size", 10))
            page_number = int(request.data.get("page_number", 1))
            search_query = request.data.get("search")

            # Start with a base queryset
            queryset = Task.objects.all()

            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query)
                    | Q(description__icontains=search_query)
                )

            paginator = Paginator(queryset, page_size)
            try:
                page_obj = paginator.page(page_number)
            except EmptyPage:
                return Response(
                    {"status": "fail", "message": "Page not found.", "data": {}},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = TaskSerializer(
                page_obj.object_list, many=True, context={"request": request}
            )

            response_data = {
                "total_pages": paginator.num_pages,
                "current_page": page_obj.number,
                "total_items": paginator.count,
                "results": serializer.data,
            }

            return Response(
                {
                    "status": "success",
                    "message": "Task retrieved successfully",
                    "data": response_data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TaskListById(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = TaskSerializer

    def get(self, request):
        try:

            task_id = request.data.get("id")

            if not task_id:
                return Response(
                    {"status": "fail", "message": "Task ID is required.", "data": {}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            task = Task.objects.filter(id=task_id).first()
            if not task:
                return Response(
                    {"status": "fail", "message": "Task not found.", "data": {}},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = self.serializer_class(task, context={"request": request})
            return Response(
                {
                    "status": "success",
                    "message": "Task retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TaskDetailDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = TaskSerializer

    def delete(self, request):
        task_id = request.data.get("id")
        if not task_id:
            return Response(
                {"status": "fail", "message": "Task ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task = Task.objects.get(id=task_id)
            task.delete()
            return Response(
                {"status": "success", "message": "Task deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Task.DoesNotExist:
            return Response(
                {"status": "fail", "message": "Task not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# class TaskDetailView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = (MultiPartParser, FormParser)
#     serializer_class = TaskSerializer

#     def get(self, request, *args, **kwargs):
#         task_id = request.data.get("id")
#         if not task_id:
#             raise ValidationError({"detail": "Task ID is required."})

#         try:
#             task = Task.objects.get(id=task_id, assigned_user=request.user)
#         except Task.DoesNotExist:
#             return Response(
#                 {"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND
#             )

#         serializer = self.serializer_class(task)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def put(self, request, *args, **kwargs):
#         task_id = request.data.get("id")  # Get the ID from the form data
#         if not task_id:
#             raise ValidationError({"detail": "Task ID is required."})

#         try:
#             task = Task.objects.get(id=task_id, assigned_user=request.user)
#         except Task.DoesNotExist:
#             return Response(
#                 {"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND
#             )

#         serializer = self.serializer_class(task, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, *args, **kwargs):
#         task_id = request.data.get("id")  # Get the ID from the form data
#         if not task_id:
#             raise ValidationError({"detail": "Task ID is required."})

#         try:
#             task = Task.objects.get(id=task_id, assigned_user=request.user)
#         except Task.DoesNotExist:
#             return Response(
#                 {"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND
#             )

#         task.delete()
#         return Response(
#             {"detail": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT
#         )
