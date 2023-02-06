from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MenuItemSerializer, CategorySerializer
from .models import MenuItem, Category
from django.core.paginator import Paginator, EmptyPage

# Create your views here.


class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class MenuItemsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        price = request.query_params.get('price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)

        if category_name:
            items = items.filter(category__title=category_name.title())
        if price:
            items = items.filter(price__lte=price)
        if search:
            items = items.filter(title__contains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)

        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []

        serializer = MenuItemSerializer(items, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = {
            "title": request.data.get("title"),
            "price": request.data.get("price"),
            "inventory": request.data.get("inventory"),
            "category_id": request.data.get("category_id"),
        }

        serializer = MenuItemSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SingleMenuItemAPIView(APIView):
    def get_object(self, pk):
        try:
            return MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        item = self.get_object(pk)

        if not item:
            return Response({"res": "Item does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        item = self.get_object(pk)

        if not item:
            return Response({"res": "Item does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "title": request.data.get("title"),
            "price": request.data.get("price"),
            "inventory": request.data.get("inventory"),
            "category_id": request.data.get("category_id"),
        }

        serializer = MenuItemSerializer(instance=item, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        item = self.get_object(pk)

        if not item:
            return Response({"res": "Item does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        item.delete()
        return Response({"res": "Item deleted"}, status=status.HTTP_200_OK)
