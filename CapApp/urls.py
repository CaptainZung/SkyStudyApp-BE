from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns=[
    path('Vocabulary/', views.VocabularyApi),
    path('Topic/<str:topic>/<str:word>/', views.VocabularyDetailView.as_view()),
    path('Topic/<str:topic>/Word/<str:word>/', views.VocabularyOnlyWordApi), 
    path('Topic/<str:topic>/<str:word>/AddExamples/', views.AddExampleByWordApi),
    path('Topic/<str:topic>/<str:word>/AddImage/', views.UploadVocabularyImageView.as_view()),
    path('Topic/<str:topic>/<str:word>/GetImage/', views.GetVocabularyImageView.as_view()),
    path('Topic/<str:topic>/<str:word>/Examples/', views.ExamplesByWordApi),
    path('Topic/<str:topic>/', views.get_vocabulary_by_topic),
    path('Register/', views.RegisterView.as_view()),
    path('Login/', views.LoginView.as_view()),
    path('User/', views.UserListView.as_view()),
    path('User/UpdatePin/', views.UpdatePinView.as_view()),
    path('AddYourWord/',views.AddWordYourDictionaryApi),
    path('YourDictionary/',views.YourDictionaryAPI),
    path('YourDictionaryChart/',views.YourDictionaryChart),
]
