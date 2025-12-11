# graphql_app.py

"""
This file integrates the GraphQL schema with FastAPI using Strawberry.

To use GraphQL with your FastAPI app, you need to:
1. Install strawberry: pip install strawberry-graphql
2. Add this route to your FastAPI app
3. Access GraphQL at /graphql endpoint
"""

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from graphql_schema import schema

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# This will be imported and added to your main FastAPI app
# In youthGroupFastAPI.py, add:
#   from graphql_app import graphql_app
#   app.include_router(graphql_app, prefix="/graphql")

