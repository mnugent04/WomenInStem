# graphql_main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

# database connection helpers
from database import (
    get_mysql_pool,
    get_mongo_client,
    get_redis_client,
    close_connections
)

# --- App Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up... connecting to MySQL, MongoDB, and Redis")
    get_mysql_pool()
    get_mongo_client()
    get_redis_client()
    yield
    print("Shutting down... closing database connections")
    close_connections()


# --- FastAPI App ---
app = FastAPI(
    title="Youth Group GraphQL API",
    description="GraphQL layer for the YouthGroupDB, powered by MySQL, MongoDB, and Redis.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files (optional) ---
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static"
)

# --- GraphQL Router ---
from strawberry.fastapi import GraphQLRouter
from graphql_schema import schema

graphql_app = GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/graphql")

# --- Demo Page (optional) ---
@app.get("/demo", response_class=FileResponse)
async def read_demo():
    return os.path.join(os.path.dirname(__file__), "index.html")


if __name__ == "__main__":
    print("\nTo run this GraphQL API:")
    print("1. pip install -r requirements.txt")
    print("2. uvicorn graphql_main:app --reload --port 8099")
    print("3. Visit http://127.0.0.1:8099/graphql for GraphiQL")
