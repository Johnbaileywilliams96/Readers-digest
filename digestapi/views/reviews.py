from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from digestapi.models import Review, Book
from django.contrib.auth.models import User

class ReviewSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'book', 'user', 'rating', 'comment', 'date_posted', 'is_owner']
        read_only_fields = ['user']

    def get_is_owner(self, obj):
        # Check if the user is the owner of the review
        return self.context['request'].user == obj.user


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]  # Changed from AllowAny since you check for user

    def list(self, request):
        reviews = Review.objects.all()  # Fixed typo: object → objects
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)  # Added .data


# class Review(models.Model):
#     book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="booksReviews")
#     rating = models.IntegerField()
#     comment = models.TextField(null=True, blank=True)
#     date_posted = models.DateTimeField(auto_now_add=True)
    

    def create(self, request):
        # Create a new instance of a review and assign properties
        try:
            # Get the book object from the ID
            book_id = request.data.get('book')
            book = Book.objects.get(pk=book_id)
            
            rating = request.data.get('rating')
            comment = request.data.get('comment')
            
            # We typically don't let users set date_posted directly
            # It should use auto_now_add=True in the model

            review = Review.objects.create(
                user=request.user,
                book=book,
                rating=rating,
                comment=comment)

            # Serialize the object and return
            serializer = ReviewSerializer(review, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk)
            serializer = ReviewSerializer(review, context={'request': request})
            return Response(serializer.data)
        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

    def destroy(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk)
            
            # Check if user owns this review
            if review.user.id != request.user.id:
                return Response(status=status.HTTP_403_FORBIDDEN)
            
            # Delete the review
            review.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)