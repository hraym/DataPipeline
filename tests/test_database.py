import pytest
from unittest.mock import patch, MagicMock
from pymongo.errors import ConnectionFailure
from datetime import datetime, UTC
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import MongoDBHandler

@pytest.fixture
def db_handler():
    with patch('src.database.MongoClient') as mock_client:
        handler = MongoDBHandler(db_name='test_world_bank_data')
        handler.client = mock_client
        handler.db = mock_client['test_world_bank_data']
        yield handler

@pytest.mark.parametrize("command_result,expected", [
    (None, True),
    (ConnectionFailure("Server not available"), False)
])
def test_test_connection(db_handler, command_result, expected):
    db_handler.client.admin.command.side_effect = command_result
    assert db_handler.test_connection() == expected

@pytest.mark.parametrize("existing_data,new_data,expected_calls", [
    (None, {'country_code': 'USA', 'year': 2020, 'value': 100}, 'insert_one'),
    ({'_id': 1, 'country_code': 'USA', 'year': 2020, 'value': 100}, 
     {'country_code': 'USA', 'year': 2020, 'value': 100}, None),
    ({'_id': 1, 'country_code': 'USA', 'year': 2020, 'value': 100}, 
     {'country_code': 'USA', 'year': 2020, 'value': 110}, 'update_one')
])
def test_insert_or_update_indicator_data(db_handler, existing_data, new_data, expected_calls):
    mock_collection = MagicMock()
    db_handler.db.__getitem__.return_value = mock_collection
    mock_collection.find_one.return_value = existing_data

    db_handler.insert_or_update_indicator_data('GDP', [new_data])

    if expected_calls == 'insert_one':
        mock_collection.insert_one.assert_called_once()
        args, _ = mock_collection.insert_one.call_args
        assert args[0]['country_code'] == new_data['country_code']
        assert args[0]['year'] == new_data['year']
        assert args[0]['value'] == new_data['value']
        assert 'last_updated' in args[0]
    elif expected_calls == 'update_one':
        mock_collection.update_one.assert_called_once()
        args, _ = mock_collection.update_one.call_args
        assert args[0] == {'_id': 1}
        assert args[1]['$set']['value'] == new_data['value']
        assert 'last_updated' in args[1]['$set']
    else:
        mock_collection.insert_one.assert_not_called()
        mock_collection.update_one.assert_not_called()

def test_get_indicator_data(db_handler):
    mock_collection = MagicMock()
    db_handler.db.__getitem__.return_value = mock_collection
    mock_collection.find.return_value = [{'country_code': 'USA', 'year': 2020, 'value': 100}]

    result = db_handler.get_indicator_data('GDP', ['USA'], 2020, 2020)
    
    assert len(result) == 1
    assert result[0]['country_code'] == 'USA'
    assert result[0]['year'] == 2020
    assert result[0]['value'] == 100

def test_get_missing_data_ranges(db_handler):
    mock_collection = MagicMock()
    db_handler.db.__getitem__.return_value = mock_collection
    mock_collection.find.return_value = [
        {'country_code': 'USA', 'year': 2020},
        {'country_code': 'USA', 'year': 2021},
        {'country_code': 'CAN', 'year': 2020},
    ]

    result = db_handler.get_missing_data_ranges('GDP', ['USA', 'CAN'], 2020, 2021)
    
    assert len(result) == 1
    assert ('CAN', 2021) in result

def test_create_indexes(db_handler):
    mock_collection = MagicMock()
    db_handler.db.list_collection_names.return_value = ['GDP', 'Population']
    db_handler.db.__getitem__.return_value = mock_collection

    db_handler.create_indexes()

    assert mock_collection.create_index.call_count == 2
    mock_collection.create_index.assert_called_with([('country_code', 1), ('year', 1)], unique=True)

@pytest.mark.parametrize("find_one_result,expected", [
    ({'year': 2022}, 2022),
    (None, None)
])
def test_get_latest_year(db_handler, find_one_result, expected):
    mock_collection = MagicMock()
    db_handler.db.__getitem__.return_value = mock_collection
    mock_collection.find_one.return_value = find_one_result

    result = db_handler.get_latest_year('GDP')
    
    assert result == expected
    mock_collection.find_one.assert_called_with(sort=[('year', -1)])

def test_close_connection(db_handler):
    db_handler.close_connection()
    db_handler.client.close.assert_called_once()