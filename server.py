from concurrent import futures
import grpc
import psycopg2
import search_pb2
import search_pb2_grpc

class SearchService(search_pb2_grpc.SearchServiceServicer):
    def Search(self, request, context):
        query = request.query
        results = []

        # Connect to the PostgreSQL database
        connection = psycopg2.connect(user="flexiuser",
                                      password="flexipassword",
                                      host="database",
                                      port="5432",
                                      database="flexidb")
        cursor = connection.cursor()

        # Execute SQL query to fetch search results
        cursor.execute("SELECT title, snippet FROM documents WHERE title ILIKE %s", ('%' + query + '%',))
        rows = cursor.fetchall()

        # Construct SearchResults from database query results
        for row in rows:
            results.append(search_pb2.SearchResult(title=row[0], snippet=row[1]))

        # Close database connection
        cursor.close()
        connection.close()

        return search_pb2.SearchResponse(results=results)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    search_pb2_grpc.add_SearchServiceServicer_to_server(SearchService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()