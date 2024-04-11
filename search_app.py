# my_search_app.py

import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from boolean_model import BooleanModel
def load_inverted_index(filename):
    inverted_index = {}
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            keyword, frequency, documents = row
            inverted_index[keyword] = {'frequency': int(frequency), 'documents': documents.split(',')}
    return inverted_index



def load_metadata(filename):
    metadata = {}
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            if lines[i].strip():
                try:
                    doc_id = int(lines[i].split(':', 1)[1].strip())
                    url = lines[i + 1].split(':', 1)[1].strip()
                    title = lines[i + 2].split(':', 1)[1].strip()
                    description = lines[i + 3].split(':', 1)[1].strip().split(', ')
                    metadata[doc_id] = {'title': title, 'url': url, 'description': description}
                except (IndexError, ValueError) as e:
                    print(f"Error parsing metadata at line {i+1}: {e}")
                finally:
                    i += 4
            else:
                i += 1  # Move to the next line
    return metadata



# Load inverted index and metadata
inverted_index = load_inverted_index('inverted_index.csv')
metadata = load_metadata('meta.txt')

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Define search function
def search(request):
    query = request.GET.get('q', '').lower()
    search_results = []

    # Search query in inverted index
    if query in inverted_index:
        posting_pages = inverted_index[query]['documents']
        for page_id in posting_pages:
            page_id = int(page_id.strip())
            if page_id in metadata:
                metadata_item = metadata[page_id]
                result = {
                    'title': metadata_item['title'],
                    'url': metadata_item['url'],
                    'description': ', '.join(metadata_item['description'])
                }
                print(result)
                search_results.append(result)

    return render(request, 'search.html', {'query': query, 'results': search_results})

# Define advanced search function
def advanced(request):
    print("in advanced func")
    # Retrieve the query from the request
    query = request.GET.get('q', '').lower()

    # Create an instance of the BooleanModel class
    boolean_model = BooleanModel()

    # Parse the query using the infix_to_postfix method
    postfix_query = boolean_model.infix_to_postfix(query.split())

    # Perform the search using the parsed query
    search_results = boolean_model.evaluate_query(postfix_query, inverted_index)

    # Retrieve metadata for the matching documents
    matching_metadata = []
    for page_id in search_results:
        if page_id in metadata:
            metadata_item = metadata[page_id]
            matching_metadata.append({
                'title': metadata_item['title'],
                'url': metadata_item['url'],
                'description': ', '.join(metadata_item['description'])
            })

    # Render the results in the advanced.html template
    return render(request, 'advanced.html', {'query': query, 'results': matching_metadata})

# Define main function to run Django server
if __name__ == "__main__":
    # Configure Django settings
    settings.configure(
        DEBUG=True,
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': ['templates'],
            },
        ],
        ROOT_URLCONF=__name__,
    )

    # Define URL patterns
    from django.urls import path
    urlpatterns = [
        path('', search, name='search'),
        path('advanced', advanced,name='advanced')
    ]

    # Run Django server
    from django.core.management import execute_from_command_line
    execute_from_command_line(['search_app.py', 'runserver'])
