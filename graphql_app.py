"""
graphql_app.py - GraphQL Router Integration

This file creates a GraphQL endpoint for the FastAPI application using Strawberry.
GraphQL provides an alternative to REST APIs - clients can request exactly the data they need.

Key Concepts:
- GraphQL Router: Connects the GraphQL schema to FastAPI routes
- Schema: Defined in graphql_schema.py, describes all available queries and mutations
- Single Endpoint: Unlike REST (many endpoints), GraphQL uses one endpoint (/graphql)
- Query Language: Clients send queries describing what data they want

How it works:
1. Client sends a GraphQL query to /graphql endpoint
2. Router receives query and passes it to the schema
3. Schema's resolvers execute database queries
4. Results are returned in the exact format requested

Example GraphQL Query:
{
  people {
    id
    firstName
    lastName
  }
}

To use GraphQL with your FastAPI app:
1. Install strawberry: pip install strawberry-graphql
2. Import this router in youthGroupFastAPI.py
3. Add router to FastAPI app: app.include_router(graphql_app, prefix="/graphql")
4. Access GraphQL at http://localhost:8099/graphql
"""

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from graphql_schema import schema  # Import the schema defined in graphql_schema.py

# Create GraphQL router
# This router handles all GraphQL requests and routes them to the appropriate resolvers
# The schema contains all the type definitions, queries, and mutations
graphql_app = GraphQLRouter(schema)

# This router will be imported and added to the main FastAPI app
# In youthGroupFastAPI.py, add:
#   from graphql_app import graphql_app
#   app.include_router(graphql_app, prefix="/graphql")
# This makes GraphQL available at the /graphql endpoint

