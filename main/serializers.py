from django.db.models import Avg
from rest_framework import serializers
from main.models import Category, Post, PostImage, Comment, Rating
from main import services


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'

    def _get_image_url(self, obj):
        if obj.image:
            url = obj.image.url
            request = self.context.get('request')
            if request is not None:
                url = request.build_absolute_uri(url)
        else:
            url = ''
        return url

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = self._get_image_url(instance)
        return representation


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)
    is_fan = serializers.SerializerMethodField()

    def get_is_fan(self, obj):
        user = self.context.get('request').user
        return services.is_fan(obj, user)

    class Meta:
        model = Post
        fields = ('id', 'title', 'category', 'created_at', 'text', 'is_fan', 'total_likes')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['category'] = CategorySerializer(instance.category).data
        representation['images'] = PostImageSerializer(instance.images.all(), many=True,
                                                       context=self.context).data
        representation['comments'] = PostCommentSerializer(instance.post_c.all(), many=True,
                                                           context=self.context).data
        representation['ratings'] = instance.ratings.all().aggregate(Avg('rating')).get('rating__avg')
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        images_data = request.FILES
        user_id = request.user.id
        validated_data['author_id'] = user_id
        post = Post.objects.create(**validated_data)
        for image in images_data.getlist('images'):
            PostImage.objects.create(post=post, image=image)
        return post


class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text', 'post')

    def create(self, validated_data):
        request = self.context.get('request')
        user_id = request.user.id
        validated_data['user_id'] = user_id
        comment = Comment.objects.create(**validated_data)
        return comment


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('post', 'author', 'rating')

    def validate(self, attrs):
        rating = attrs.get('rating')
        if rating > 5:
            raise serializers.ValidationError('The value must not exceed 5')
        return attrs

    def get_fields(self):
        fields = super().get_fields()
        action = self.context.get('action')
        if action == 'create':
            fields.pop('author')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        rat = validated_data.get('rating')
        rating = Rating.objects.get_or_create(author=user, post=post)[0]
        rating.rating = rat
        rating.save()
        return rating
