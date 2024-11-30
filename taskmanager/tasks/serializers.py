from rest_framework import serializers
from .models import Task, User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "address",
            "mobile_number",
        ]

    def create(self, validated_data):

        validated_data["password"] = make_password(validated_data["password"])
        user = User.objects.create(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ["email", "password"]

    email = serializers.EmailField()

    password = serializers.CharField(write_only=True)


class TaskSerializer(serializers.ModelSerializer):

    assigned_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Task
        fields = "__all__"

    def create(self, validated_data):
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        assigned_user_data = validated_data.pop("assigned_user", None)
        if assigned_user_data:
            assigned_user = User.objects.get(id=assigned_user_data.id)
            instance.assigned_user = assigned_user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):

        representation = super().to_representation(instance)
        assigned_user = instance.assigned_user
        representation["assigned_user"] = {
            "email": assigned_user.email,
            "first_name": assigned_user.first_name,
            "last_name": assigned_user.last_name,
            "mobile_number": assigned_user.mobile_number,
            "address": assigned_user.address,
            "date_joined": assigned_user.date_joined,
        }
        return representation
