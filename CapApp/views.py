from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.utils.timezone import now, timedelta

from .models import Vocabulary, User, Example, Topic, YourDictionary
from .serializers import (
    VocabularySerializer,
    VocabularyWordSerializer,
    ExampleSerializer,
    VocabularyImageSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    YourDictionarySerializer
)


@api_view(['GET', 'POST'])
def VocabularyApi(request):
    if request.method == 'GET':
        vocabularies = Vocabulary.objects.all()
        serializer = VocabularySerializer(vocabularies, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = VocabularySerializer(data=request.data)
        if serializer.is_valid():
            vocabulary = serializer.save()
            return Response(VocabularySerializer(vocabulary).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def ExamplesByWordApi(request, topic, word):
    try:
        topic_instance = Topic.objects.get(name=topic)
        vocabulary = Vocabulary.objects.get(word=word, topic=topic_instance.name)
    except (Topic.DoesNotExist, Vocabulary.DoesNotExist):
        return Response({"error": "Topic or Vocabulary not found"}, status=status.HTTP_404_NOT_FOUND)

    examples = Example.objects.filter(vocabulary=vocabulary)
    serializer = ExampleSerializer(examples, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def AddExampleByWordApi(request, topic, word):
    try:
        topic_instance = Topic.objects.get(name=topic)
        vocabulary = Vocabulary.objects.get(word=word, topic=topic_instance.name)
    except (Topic.DoesNotExist, Vocabulary.DoesNotExist):
        return Response({"error": "Topic or Vocabulary not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ExampleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(vocabulary=vocabulary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def VocabularyByWordApi(request, topic, word):
    try:
        vocabulary = Vocabulary.objects.get(word=word, topic=topic)
        serializer = VocabularySerializer(vocabulary)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Vocabulary.DoesNotExist:
        return Response({"error": "Word not found in the specified topic"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def VocabularyOnlyWordApi(request, topic, word):
    try:
        vocabulary = Vocabulary.objects.get(word=word, topic=topic)
        serializer = VocabularyWordSerializer(vocabulary)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Vocabulary.DoesNotExist:
        return Response({"error": "Word not found in the specified topic"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_vocabulary_by_topic(request, topic):
    try:
        vocabularies = Vocabulary.objects.filter(topic=topic)
        if not vocabularies.exists():
            return Response({'error': f'No vocabulary found for topic "{topic}"'}, status=status.HTTP_404_NOT_FOUND)

        serializer = VocabularyWordSerializer(vocabularies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def add_multiple_vocabularies(request):
    if request.method == 'POST':
        data = request.data
        if isinstance(data, list):
            created_vocabularies = []
            for vocab_data in data:
                serializer = VocabularySerializer(data=vocab_data)
                if serializer.is_valid():
                    serializer.save()
                    created_vocabularies.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(created_vocabularies, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Expected a list of vocabularies'}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        phone = request.data.get('phone')
        pin = request.data.get('pin')

        # Check if username exists
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Tên người dùng này đã được đăng ký."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if phone exists
        if User.objects.filter(phone=phone).exists():
            return Response(
                {"error": "Số điện thoại này đã được đăng ký."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create serializer
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.pin = make_password(pin or "123456")  # Default PIN if not provided
            user.save()

            return Response(
                {
                    "message": "User registered successfully",
                    "username": user.username,
                    "phone": user.phone
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdatePinView(APIView):
    def post(self, request):
        # Fetch the username from the request data
        username = request.data.get('username')

        # Validate that username exists
        if not username:
            return Response(
                {"error": "Tên người dùng là bắt buộc."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the user by username
        user = get_object_or_404(User, username=username)

        # Get the new PIN from the request data
        new_pin = request.data.get('pin')

        # Validate PIN length and format
        if not new_pin or len(new_pin) != 6 or not new_pin.isdigit():
            return Response(
                {"error": "Mã PIN phải gồm đúng 6 chữ số."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Hash and update the PIN
        user.pin = make_password(new_pin)
        user.save()

        return Response({"message": "PIN updated successfully."}, status=status.HTTP_200_OK)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')

            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    return Response({"message": "Login successful", "user_id": user._id, "usename": user.username}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UploadVocabularyImageView(APIView):
    def post(self, request, topic, word):
        vocabulary = get_object_or_404(Vocabulary, topic=topic, word=word)
        serializer = VocabularyImageSerializer(vocabulary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Image uploaded successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetVocabularyImageView(APIView):
    def get(self, request, topic, word):
        vocabulary = get_object_or_404(Vocabulary, topic=topic, word=word)
        if vocabulary.image:
            return FileResponse(vocabulary.image.open(), content_type='image/jpeg')
        return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)


class VocabularyDetailView(APIView):
    def get(self, request, topic, word):
        try:
            vocabulary = Vocabulary.objects.get(topic=topic, word=word)
        except Vocabulary.DoesNotExist:
            return Response({"error": "Vocabulary not found"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "word": vocabulary.word,
            "vietnamese": vocabulary.vietnamese,
            "examples": [example.sentence for example in vocabulary.examples.all()],
            "image": request.build_absolute_uri(vocabulary.image.url) if vocabulary.image else None,
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def AddWordYourDictionaryApi(request):
    word = request.data.get('word')
    vietnamese = request.data.get('vietnamese')  # Get vietnamese translation
    username = request.data.get('user')

    # Kiểm tra xem user có được truyền vào không
    if not username:
        return Response({"error": "User is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Kiểm tra xem word có được truyền vào không
    if not word:
        return Response({"error": "Word is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Kiểm tra xem vietnamese có được truyền vào không
    if not vietnamese:
        return Response({"error": "Vietnamese translation is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Tìm user từ username
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra nếu từ đã tồn tại
    try:
        existing_entry = YourDictionary.objects.get(user=user, word=word)
        return Response({"error": "Word already exists in YourDictionary"}, status=status.HTTP_400_BAD_REQUEST)
    except YourDictionary.DoesNotExist:
        pass
    # Tạo bản ghi mới
    your_dictionary_entry = YourDictionary.objects.create(user=user, word=word, vietnamese=vietnamese)

    # Serialize bản ghi và trả về
    serializer = YourDictionarySerializer(your_dictionary_entry)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
@api_view(['POST'])
def YourDictionaryChart(request):
    username = request.data.get('user')  # Lấy từ body thay vì query params

    # Kiểm tra xem username có được truyền vào không
    if not username:
        return Response({"error": "User is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Tìm user từ username
    try:
        user = User.objects.get(username=username)
        user_id = user._id  # Lấy user ID từ user tìm được
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Tính ngày từ hôm nay đến 6 ngày trước
    today = now().date()
    seven_days_ago = today - timedelta(days=6)
    words_last_7_days = YourDictionary.objects.filter(user=user, learned_date__range=[seven_days_ago, today])

    # Tạo thống kê theo ngày
    stats = {}
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        count = words_last_7_days.filter(learned_date=day).count()
        stats[day.strftime('%Y-%m-%d')] = count

    return Response({"username": user.username, "stats": stats}, status=status.HTTP_200_OK)


@api_view(['POST'])
def YourDictionaryAPI(request):
    username = request.data.get('user')

    # Kiểm tra xem username có được truyền vào không
    if not username:
        return Response({"error": "User is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Tìm user từ username
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Lấy tất cả các từ đã học của user
    learned_words = YourDictionary.objects.filter(user=user)
    serializer = YourDictionarySerializer(learned_words, many=True)

    return Response({ "learned_words": serializer.data}, status=status.HTTP_200_OK)