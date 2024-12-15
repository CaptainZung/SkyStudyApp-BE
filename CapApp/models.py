import uuid
from django.db import models
from django.contrib.auth.hashers import make_password

def generate_uuid():
    return str(uuid.uuid4())

class Topic(models.Model):  
    name = models.CharField(max_length=100, unique=True)  # Topic name
    vietnamese = models.CharField(max_length=100)  # Vietnamese topic name

    def __str__(self):  
        return self.name

class Vocabulary(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, default=generate_uuid)
    word = models.CharField(max_length=100)
    vietnamese = models.CharField(max_length=100)
    definition = models.TextField()
    topic = models.CharField(max_length=100)
    image = models.ImageField(upload_to='vocabulary_images/', blank=True, null=True)
    icon = models.ImageField(upload_to='vocabulary_icons/', blank=True, null=True)

    def __str__(self):
        return self.word

class Example(models.Model):
    vocabulary = models.ForeignKey(Vocabulary, related_name="examples", on_delete=models.CASCADE)
    sentence = models.TextField()

    def __str__(self):
        return self.sentence

class User(models.Model):
    _id = models.CharField(max_length=100, primary_key=True, default=generate_uuid)
    username = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    pin = models.CharField(max_length=6, default="123456")

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        if not self.pin.startswith('pbkdf2_sha256$'):
            self.pin = make_password(self.pin)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
