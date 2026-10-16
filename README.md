# mathcyx-mongo-utils

Reusable, typed MongoDB setup and CRUD helpers for Python projects. The package keeps
configuration in environment variables, creates clients lazily, verifies connectivity,
and closes resources explicitly.

## Installation

Install from GitHub while the package is under development:

    python -m pip install "mathcyx-mongo-utils @ git+https://github.com/Pen20/mathcyx-mongo-utils.git"

After a PyPI release:

    python -m pip install mathcyx-mongo-utils

For CSV and Excel imports:

    python -m pip install "mathcyx-mongo-utils[data]"

## Quick start

Set configuration without committing credentials:

    MONGODB_URI=mongodb://localhost:27017
    MONGODB_DATABASE=my_application

Use one connection for the lifetime of an application:

    from mathcyx_mongo_utils import MongoConnection, MongoSettings

    settings = MongoSettings.from_env()

    with MongoConnection(settings) as mongo:
        mongo.ping()
        users = mongo.collection("users")
        result = users.insert_one({"name": "Ada", "active": True})
        print(result.inserted_id)

The URI can also be passed directly:

    from mathcyx_mongo_utils import MongoConnection

    mongo = MongoConnection.from_uri(
        "mongodb://localhost:27017",
        database="example",
    )

## CRUD repository

    from mathcyx_mongo_utils import MongoConnection, MongoRepository, MongoSettings

    with MongoConnection(MongoSettings.from_env()) as mongo:
        repository = MongoRepository(mongo.collection("users"))
        repository.insert_one({"email": "ada@example.org", "active": True})
        user = repository.find_one({"email": "ada@example.org"})
        repository.update_one({"email": "ada@example.org"}, {"active": False})

The update_one method automatically wraps ordinary field changes in the MongoDB set
operator. Pass a MongoDB update document when an operator such as increment is needed.

## Importing files

    from mathcyx_mongo_utils import MongoConnection, MongoSettings, import_records

    with MongoConnection(MongoSettings.from_env()) as mongo:
        result = import_records("users.csv", mongo.collection("users"))
        print(len(result.inserted_ids))

CSV, JSON, and JSON Lines use the Python standard library. Excel files require the
data extra. Empty files are rejected instead of issuing an invalid bulk insert.

## Configuration

MongoSettings.from_env() reads:

| Variable | Required | Default |
| --- | --- | --- |
| MONGODB_URI | Yes | — |
| MONGODB_DATABASE | Yes | — |
| MONGODB_APP_NAME | No | mathcyx-mongo-utils |
| MONGODB_TIMEOUT_MS | No | 5000 |

A custom prefix is supported. For example, MongoSettings.from_env(prefix="MYAPP_MONGO")
reads MYAPP_MONGO_URI, MYAPP_MONGO_DATABASE, and the corresponding optional variables.

## Compatibility

The original import remains available:

    from mongodb_connect.mongo_crud import mongo_operation

New projects should use mathcyx_mongo_utils.

## Development

    python -m pip install -e ".[dev,data]"
    ruff check .
    mypy
    pytest
    python -m build
    twine check dist/*

Unit tests use mocks and do not require a live database.

## Security

- Never commit MongoDB connection strings or passwords.
- Give each application a least-privilege database user.
- Prefer TLS-enabled mongodb+srv connections in hosted environments.
- Call close during application shutdown, or use the context manager.

## License

MIT
