def test_package_imports():
    from mathcyx_mongo_utils import MongoConnection, MongoRepository, MongoSettings
    from mongodb_connect.mongo_crud import mongo_operation

    assert MongoConnection is not None
    assert MongoRepository is not None
    assert MongoSettings is not None
    assert mongo_operation is not None
