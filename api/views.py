from django.shortcuts import render
from rest_framework import viewsets, permissions, views, response, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PublicItem, UserLibrary
from .serializers import PublicItemSerializer, UserLibrarySerializer, UserSerializer
import requests # Para llamar a TMDb, Jikan
import os # Para obtener la API Key

# Vista para el registro de usuarios
class UserCreate(views.APIView):
    permission_classes = [permissions.AllowAny] # Cualquiera puede registrarse

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para la biblioteca del usuario (CRUD completo)
class UserLibraryViewSet(viewsets.ModelViewSet):
    serializer_class = UserLibrarySerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios logueados

    def get_queryset(self):
        # Asegura que un usuario solo pueda ver y editar *su propia* biblioteca
        return UserLibrary.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        # Asigna el usuario automáticamente al guardar
        serializer.save(user=self.request.user)

# ¡La Vista de Búsqueda Segura!
class SearchAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        item_type = request.query_params.get('type', 'movie') # 'movie', 'series', 'anime', etc.

        if not query:
            return Response({'error': 'Query (q) es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Llamar a la API externa (Aquí es donde usas la clave secreta)
        try:
            if item_type == 'movie':
                api_url = f"https://api.themoviedb.org/3/search/movie"
                params = {
                    'api_key': os.environ.get('TMDB_API_KEY'),
                    'query': query,
                    'language': 'es-ES'
                }
            elif item_type == 'series':
                api_url = f"https://api.themoviedb.org/3/search/tv"
                params = {
                    'api_key': os.environ.get('TMDB_API_KEY'),
                    'query': query,
                    'language': 'es-ES'
                }
            elif item_type == 'anime':
                api_url = os.environ.get('JIKAN_API_URL', 'https://api.jikan.moe/v4') + "/anime"
                params = {'q': query, 'limit': 10}
            
            # (Faltaría la lógica de OpenLibrary y iTunes, pero esto es un ejemplo)
            else:
                 return Response({'error': 'Tipo de item no soportado'}, status=status.HTTP_400_BAD_REQUEST)

            
            api_response = requests.get(api_url, params=params)
            api_response.raise_for_status() # Lanza un error si la API falla
            api_data = api_response.json()
            
            # 2. "Cachear" los resultados en nuestra DB `public_items`
            # (Esta es la lógica clave que discutimos)
            
            processed_results = []
            
            # Procesar datos de TMDb (Movie/Series)
            if item_type in ['movie', 'series']:
                for item in api_data.get('results', []):
                    api_id = f"tmdb-{item['id']}"
                    
                    # Usamos get_or_create para evitar duplicados
                    obj, created = PublicItem.objects.get_or_create(
                        api_id=api_id,
                        defaults={
                            'item_type': item_type,
                            'title': item.get('title') or item.get('name'),
                            'poster_url': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                            'release_date': item.get('release_date') or item.get('first_air_date') or None,
                            'total_episodes': item.get('number_of_episodes', None) # Solo para series
                        }
                    )
                    processed_results.append(obj)
                    
            # Procesar datos de Jikan (Anime)
            elif item_type == 'anime':
                 for item in api_data.get('data', []):
                    api_id = f"jikan-{item['mal_id']}"
                    obj, created = PublicItem.objects.get_or_create(
                        api_id=api_id,
                        defaults={
                            'item_type': 'anime',
                            'title': item.get('title'),
                            'poster_url': item.get('images', {}).get('jpg', {}).get('image_url'),
                            'release_date': item.get('aired', {}).get('from', '0001-01-01T00:00:00+00:00').split('T')[0] or None,
                            'total_episodes': item.get('episodes')
                        }
                    )
                    processed_results.append(obj)

            # 3. Devolver los resultados de *nuestra* base de datos
            serializer = PublicItemSerializer(processed_results, many=True)
            return Response(serializer.data)

        except requests.exceptions.RequestException as e:
            return Response({'error': f'Error llamando a la API externa: {e}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({'error': f'Error interno del servidor: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)