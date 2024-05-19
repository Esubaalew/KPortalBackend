import wikipedia
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def get_wikipedia_article(request, title):
    wikipedia.set_lang("en")
    try:
        summary = wikipedia.summary(title)
        data = {
            'title': title,
            'summary': summary,
        }
        return Response(data, status=status.HTTP_200_OK)
    except wikipedia.exceptions.DisambiguationError as e:
        data = {'error': 'Disambiguation error. Options: ' + ', '.join(e.options)}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    except wikipedia.exceptions.PageError:
        data = {'error': 'Page not found'}
        return Response(data, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def search_wikipedia(request, query):
    wikipedia.set_lang("en")
    try:
        results = wikipedia.search(query)
        search_results = [{'title': result} for result in results]
        return Response(search_results, status=status.HTTP_200_OK)
    except wikipedia.exceptions.PageError:
        data = {'error': 'No results found'}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
