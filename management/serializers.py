from django.contrib.auth.models import User
from rest_framework import serializers

from rest_framework.exceptions import ValidationError
from .models import CandidateProfile


class CandidateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CandidateProfile
        fields = '__all__'

    def validate_email(self, value):
        # Check if the email is already in use
        if User.objects.filter(email=value).exists():
            raise ValidationError("This email is already in use.")
        return value

    def create(self, validated_data):
        email = self.context['request'].data.get('email')
        name = validated_data.get('full_name', '')
        password = validated_data.pop('password', '')
        if User.objects.filter(email=email).exclude(
                candidate_profile__id=self.instance.id if self.instance else None).exists():
            raise ValidationError("This email is already in use.")
        name_parts = name.split(" ")
        first_name = name_parts[0] if name_parts else ''
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ''
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        candidate = CandidateProfile.objects.create(user=user, **validated_data)
        return candidate
